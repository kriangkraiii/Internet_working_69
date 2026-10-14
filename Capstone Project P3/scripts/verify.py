"""verify.py — ตรวจ Control Plane / Data Plane / Management Plane อัตโนมัติ แล้วออกรายงาน PASS/FAIL

ใช้งาน:  python scripts/verify.py                 ตรวจทุกเครื่อง -> evidence/verify_<เวลา>.md
         python scripts/verify.py --quick         ตรวจเฉพาะ OSPF/IKE/ping (ใช้ระหว่าง fault injection)
"""
from __future__ import annotations

import argparse
import json
import re

from common import EVIDENCE, banner, connect, load_inventory, now, run_parallel, select

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"


def _rows(parsed):
    return parsed if isinstance(parsed, list) else []


def _success_rate(out: str) -> int:
    m = re.search(r"Success rate is (\d+) percent", out)
    return int(m.group(1)) if m else 0


def check_device(dev: dict, inventory: dict, quick: bool = False) -> dict:
    res: list[tuple[str, str, str]] = []
    raw: dict[str, str] = {}
    conn = connect(dev, via="ssh", tag="verify")

    def cmd(c: str, **kw):
        out = conn.send_command(c, read_timeout=60, **kw)
        if isinstance(out, str):
            raw[c] = out
        return out

    # 1) Interfaces
    want = [i["name"] for i in dev.get("interfaces", [])]
    if dev["role"] != "isp":
        want = [dev["wan"]["name"], dev["lan"]["name"]] + [f"Tunnel{t['id']}" for t in dev["tunnels"]]
    brief = _rows(cmd("show ip interface brief", use_textfsm=True))
    state = {(r.get("interface") or r.get("intf")): (r.get("status"), r.get("proto")) for r in brief}
    for ifn in want:
        st = state.get(ifn)
        ok = st == ("up", "up")
        res.append((f"Interface {ifn}", PASS if ok else FAIL, "/".join(st) if st else "not found"))

    if dev["role"] == "isp":
        ntp = cmd("show ntp status")
        res.append(("NTP master (stratum 3)", PASS if "synchronized" in ntp else FAIL,
                    ntp.splitlines()[0] if ntp else ""))
        conn.disconnect()
        return {"results": res, "raw": raw}

    # 2) OSPFv2 / OSPFv3 adjacency
    nbrs = _rows(cmd("show ip ospf neighbor", use_textfsm=True))
    full = [n for n in nbrs if str(n.get("state", "")).startswith("FULL")]
    res.append(("OSPFv2 neighbors FULL", PASS if len(full) == dev["expected_ospf"] else FAIL,
                f"{len(full)}/{dev['expected_ospf']} " + ", ".join(
                    f"{n.get('neighbor_id')}={n.get('state')}" for n in nbrs)))
    v3 = cmd("show ipv6 ospf neighbor")
    v3_full = len(re.findall(r"\bFULL", v3))
    res.append(("OSPFv3 neighbors FULL", PASS if v3_full == dev["expected_ospf"] else FAIL,
                f"{v3_full}/{dev['expected_ospf']}"))

    # 3) IPsec
    ike = cmd("show crypto isakmp sa")
    qm = len(re.findall(r"QM_IDLE", ike))
    res.append(("IKE SA (QM_IDLE)", PASS if qm >= len(dev["tunnels"]) else FAIL,
                f"{qm}/{len(dev['tunnels'])} " + " ".join(sorted(set(re.findall(r"MM_\w+|AG_\w+", ike))))))
    enc = sum(int(x) for x in re.findall(r"#pkts encaps: (\d+)", cmd("show crypto ipsec sa")))
    res.append(("IPsec ESP encaps counter", PASS if enc > 0 else FAIL, f"{enc} pkts"))

    # 4) Data plane: ping loopback ของทุก site อื่น (IPv4 + IPv6) โดยใช้ Loopback0 เป็น source
    for other in inventory.values():
        if other["name"] == dev["name"] or other["role"] == "isp":
            continue
        v4 = _success_rate(cmd(f"ping {other['loopback']['ip']} source Loopback0 repeat 5"))
        res.append((f"Ping v4 -> {other['name']} Lo0", PASS if v4 >= 80 else FAIL, f"{v4}%"))
        v6_ip = other["loopback"]["ipv6"].split("/")[0]
        v6 = _success_rate(cmd(f"ping ipv6 {v6_ip} source Loopback0 repeat 5"))
        res.append((f"Ping v6 -> {other['name']} Lo0", PASS if v6 >= 80 else FAIL, f"{v6}%"))

    if not quick:
        # 5) Management & security plane
        ntp = cmd("show ntp status")
        res.append(("NTP synchronized", PASS if "Clock is synchronized" in ntp else WARN,
                    "sync อาจใช้เวลา 2-5 นาทีหลัง deploy" if "unsynchronized" in ntp else ntp.splitlines()[0]))
        copp = cmd("show policy-map control-plane")
        res.append(("CoPP attached", PASS if "PM-COPP" in copp else FAIL, ""))
        fnf = cmd("show flow monitor FNF-MONITOR")
        res.append(("Flexible NetFlow monitor", PASS if "allocated" in fnf.lower() else FAIL, ""))
        exp = cmd("show flow exporter FNF-EXPORTER statistics")
        res.append(("NetFlow exporter -> collector", PASS if dev["collector"] in cmd(
            "show flow exporter FNF-EXPORTER") else FAIL, " ".join(exp.split()[-6:])))
        logging = cmd("show logging | include Logging to|Trap logging")
        res.append(("Syslog host", PASS if dev["collector"] in logging else FAIL, dev["collector"]))
        snmp = cmd("show snmp user")
        res.append(("SNMPv3 user (authPriv)", PASS if dev["snmp_user"] in snmp and "AES128" in snmp else FAIL, ""))
        ssh = cmd("show ip ssh")
        res.append(("SSH version 2", PASS if "version 2.0" in ssh else FAIL, ""))
        acl = cmd("show ip access-lists ACL-WAN-IN")
        hits = sum(int(x) for x in re.findall(r"\((\d+) match", acl))
        res.append(("ACL-WAN-IN applied", PASS if "ACL-WAN-IN" in acl else FAIL, f"{hits} matches"))
        cmd("show ip route ospf")
        cmd("show ipv6 route ospf")
    conn.disconnect()
    return {"results": res, "raw": raw}


def run(devices: dict, inventory: dict, quick: bool = False) -> dict:
    return run_parallel(devices, lambda d: check_device(d, inventory, quick))


def report(results: dict, title: str, save: bool = True) -> int:
    banner(title)
    lines = [f"# {title}", "", "| Device | Check | Result | Detail |", "|---|---|---|---|"]
    fails = 0
    for name in sorted(results):
        r = results[name]
        if isinstance(r, Exception):
            fails += 1
            print(f"{name:8} {'CONNECT':34} FAIL  {r!s:.80}")
            lines.append(f"| {name} | SSH connect | **FAIL** | {str(r).splitlines()[0]} |")
            continue
        for check, status, detail in r["results"]:
            fails += status == FAIL
            print(f"{name:8} {check:34} {status:5} {detail}")
            lines.append(f"| {name} | {check} | {'**FAIL**' if status == FAIL else status} | {detail} |")
    total = sum(len(r["results"]) for r in results.values() if not isinstance(r, Exception))
    summary = f"\nสรุป: {total} checks, FAIL {fails}"
    print(summary)
    if save:
        EVIDENCE.mkdir(exist_ok=True)
        stamp = now()
        md = EVIDENCE / f"verify_{stamp}.md"
        md.write_text("\n".join(lines) + "\n" + summary + "\n", encoding="utf-8")
        raw = {n: r["raw"] for n, r in results.items() if not isinstance(r, Exception)}
        (EVIDENCE / f"verify_{stamp}_raw.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False),
                                                         encoding="utf-8")
        print(f"รายงาน: {md.relative_to(EVIDENCE.parent)}")
    return fails


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("devices", nargs="*")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    inv = load_inventory()
    fails = report(run(select(inv, args.devices), inv, args.quick), f"Verification {now()}")
    raise SystemExit(1 if fails else 0)


if __name__ == "__main__":
    main()
