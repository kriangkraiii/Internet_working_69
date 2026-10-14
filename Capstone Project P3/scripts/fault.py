"""fault.py — Live Fault Injection & Recovery พร้อมเก็บหลักฐานสำหรับ RCA อัตโนมัติ

ใช้งาน:
  python scripts/fault.py list
  python scripts/fault.py run psk            ครบวงจร: baseline -> inject -> เก็บอาการ -> recover -> verify
  python scripts/fault.py inject mtu         ฉีดปัญหาอย่างเดียว (ตอน Live Demo ให้ไล่แก้เองบน CLI)
  python scripts/fault.py diagnose mtu       เก็บอาการ (show/logging) ของ scenario นั้น
  python scripts/fault.py recover mtu        แก้แบบเจาะจง (targeted fix)
  python scripts/fault.py recover mtu --rollback   กู้ด้วย configure replace flash:golden.cfg

หลักฐานทั้งหมดอยู่ที่ evidence/fault_<scenario>_<เวลา>/timeline.md -> ใช้แปะในรายงาน RCA
"""
from __future__ import annotations

import argparse
import datetime as dt
import time

import verify
from common import EVIDENCE, banner, connect, load_inventory, now

# ---------------------------------------------------------------------------
# นิยาม scenario: target, peer, คำสั่ง inject/recover, คำสั่งเก็บอาการ, เวลารอให้อาการแสดง
# ใช้ {psk} {peer_wan} แทนค่าจาก inventory ตอนรัน
# ---------------------------------------------------------------------------
SCENARIOS = {
    "mtu": {
        "title": "OSPF MTU mismatch บน Tunnel12 (R2-BR1)",
        "target": "R2-BR1", "peer": "R1-HQ",
        "pre_exec": ["debug ip ospf adj"],
        "inject": ["interface Tunnel12", "ip mtu 1300", "shutdown", "no shutdown"],
        "wait": 35,
        "symptom": ["show ip ospf neighbor", "show ip interface Tunnel12 | include MTU",
                    "show logging | include OSPF|MTU"],
        "peer_symptom": ["show ip ospf neighbor", "show ip interface Tunnel12 | include MTU"],
        "post_exec": ["undebug all"],
        "recover": ["interface Tunnel12", "ip mtu 1400"],
        "converge": 30,
        "expect": "neighbor ค้างที่ EXSTART/EXCHANGE, debug: 'Nbr 1.1.1.1 has larger interface MTU'",
    },
    "psk": {
        "title": "IPsec Pre-Shared Key ไม่ตรงกัน (R2-BR1 <-> R1-HQ)",
        "target": "R2-BR1", "peer": "R1-HQ",
        "pre_exec": ["debug crypto isakmp"],
        "inject": ["no crypto isakmp key {psk} address {peer_wan}",
                   "crypto isakmp key WRONG-KEY-2569 address {peer_wan}"],
        "inject_exec": ["clear crypto session"],
        "wait": 45,
        "symptom": ["show crypto isakmp sa", "show crypto session", "show ip ospf neighbor",
                    "show logging | include CRYPTO|ISAKMP|OSPF"],
        "peer_symptom": ["show crypto isakmp sa", "show logging | include CRYPTO|OSPF"],
        "post_exec": ["undebug all"],
        "recover": ["no crypto isakmp key WRONG-KEY-2569 address {peer_wan}",
                    "crypto isakmp key {psk} address {peer_wan}"],
        "recover_exec": ["clear crypto session"],
        "converge": 40,
        "expect": "IKE ค้าง MM_KEY_EXCH/MM_NO_STATE, peer log %CRYPTO-4-IKMP_BAD_MESSAGE, OSPF Tunnel12 down",
    },
    "mgmt-acl": {
        "title": "ACL บน VTY drop ทราฟฟิก Management (R3-DC ถูกล็อก SSH)",
        "target": "R3-DC", "peer": "R1-HQ",
        "inject": ["ip access-list standard ACL-VTY-LOCKOUT", "permit host {wrong_host}", "deny any log",
                   "line vty 0 4", "access-class ACL-VTY-LOCKOUT in"],
        "wait": 5,
        "probe_ssh": True,  # ลอง SSH จาก automation host เพื่อพิสูจน์ว่าโดนล็อก
        "symptom_via": "console",
        "symptom": ["show running-config | section line vty", "show ip access-lists ACL-VTY-LOCKOUT",
                    "show logging | include SEC|ACCESS|SSH"],
        "peer_symptom": ["show ip ospf neighbor"],
        "recover_via": "console",  # SSH ใช้ไม่ได้แล้ว -> กู้ผ่าน Console Server ของ CML (out-of-band)
        "recover": ["line vty 0 4", "access-class ACL-MGMT-SSH in", "exit",
                    "no ip access-list standard ACL-VTY-LOCKOUT"],
        "converge": 5,
        "expect": "SSH จาก automation host ถูกปฏิเสธ, %SEC-6-IPACCESSLOGS ... denied <devbox>, Data plane ยังปกติ",
    },
    "flap": {
        "title": "Link Flapping บน WAN ของ R2-BR1 (Gi0/0)",
        "target": "R2-BR1", "peer": "R1-HQ",
        "flap": {"interface": "GigabitEthernet0/0", "times": 3, "down": 8, "up": 12},
        "wait": 5,
        "symptom": ["show ip ospf neighbor", "show crypto isakmp sa", "show interfaces GigabitEthernet0/0 | include line protocol|resets|carrier",
                    "show logging | include LINK|LINEPROTO|OSPF|CRYPTO"],
        "peer_symptom": ["show logging | include OSPF|CRYPTO", "show ip route ospf"],
        "recover": ["interface GigabitEthernet0/0", "no shutdown"],
        "converge": 40,
        "expect": "%LINK-5-CHANGED/%LINEPROTO-5-UPDOWN ซ้ำๆ, %OSPF-5-ADJCHG FULL->DOWN, route 10.2.10.0/24 หายจาก R1",
    },
}


def _fmt(cmds, ctx):
    return [c.format(**ctx) for c in cmds]


def _ctx(sc, inv):
    tgt, peer = inv[sc["target"]], inv[sc["peer"]]
    return {"psk": tgt["ipsec_psk"], "peer_wan": peer["wan"]["ip"],
            "wrong_host": inv["R0-ISP"]["mgmt_ip"]}  # host ที่ "ไม่ใช่" automation host


class Timeline:
    def __init__(self, key, sc):
        self.dir = EVIDENCE / f"fault_{key}_{now()}"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.md = [f"# Fault: {sc['title']}", "", f"- Target: **{sc['target']}**  Peer: **{sc['peer']}**",
                   f"- อาการที่คาดไว้: {sc['expect']}", ""]

    def step(self, text):
        t = dt.datetime.now().strftime("%H:%M:%S")
        print(f"[{t}] {text}")
        self.md.append(f"\n## [{t}] {text}\n")

    def block(self, title, content):
        self.md.append(f"**{title}**\n\n```\n{content.strip()}\n```\n")

    def save(self):
        p = self.dir / "timeline.md"
        p.write_text("\n".join(self.md), encoding="utf-8")
        print(f"\nหลักฐาน: {p.relative_to(EVIDENCE.parent)}")


def _exec(conn, cmds, tl=None):
    for c in cmds:
        out = conn.send_command_timing(c, read_timeout=30)
        if tl:
            tl.block(f"{conn.base_prompt}# {c}", out or "(no output)")


def _collect(dev, cmds, tl, via="ssh"):
    conn = connect(dev, via=via, tag="diagnose")
    for c in cmds:
        out = conn.send_command(c, read_timeout=60)
        if "show logging" in c:  # เก็บเฉพาะ 25 บรรทัดล่าสุด
            out = "\n".join(out.splitlines()[-25:])
        tl.block(f"{dev['name']}# {c}", out)
    conn.disconnect()


def inject(key, sc, inv, tl):
    ctx, tgt = _ctx(sc, inv), inv[sc["target"]]
    conn = connect(tgt, via="ssh", tag=f"fault_{key}")
    tl.block(f"{tgt['name']}# show clock", conn.send_command("show clock"))
    _exec(conn, sc.get("pre_exec", []), tl)
    if "flap" in sc:
        f = sc["flap"]
        for i in range(f["times"]):
            conn.send_config_set([f"interface {f['interface']}", "shutdown"])
            tl.step(f"flap {i + 1}/{f['times']}: {f['interface']} shutdown")
            time.sleep(f["down"])
            conn.send_config_set([f"interface {f['interface']}", "no shutdown"])
            tl.step(f"flap {i + 1}/{f['times']}: {f['interface']} no shutdown")
            time.sleep(f["up"])
    else:
        out = conn.send_config_set(_fmt(sc["inject"], ctx))
        tl.block("Injected config", out)
    _exec(conn, sc.get("inject_exec", []), tl)
    conn.disconnect()


def diagnose(key, sc, inv, tl):
    tgt, peer = inv[sc["target"]], inv[sc["peer"]]
    if sc.get("probe_ssh"):
        try:
            c = connect(tgt, via="ssh", tag="probe")
            c.disconnect()
            tl.block("SSH probe จาก automation host", "SSH ยังเข้าได้ (inject ไม่ได้ผล?)")
        except Exception as exc:  # noqa: BLE001
            tl.block("SSH probe จาก automation host", f"{type(exc).__name__}: {str(exc).splitlines()[0]}")
    _collect(tgt, sc["symptom"], tl, via=sc.get("symptom_via", "ssh"))
    _collect(peer, sc.get("peer_symptom", []), tl)
    if sc.get("post_exec"):
        conn = connect(tgt, via=sc.get("symptom_via", "ssh"), tag="diagnose")
        _exec(conn, sc["post_exec"])
        conn.disconnect()


def recover(key, sc, inv, tl, rollback=False):
    ctx, tgt = _ctx(sc, inv), inv[sc["target"]]
    via = sc.get("recover_via", "ssh")
    conn = connect(tgt, via=via, tag=f"recover_{key}")
    if rollback:
        out = conn.send_command(f"configure replace {tgt['flash']}golden.cfg force", read_timeout=120)
        tl.block(f"{tgt['name']}# configure replace {tgt['flash']}golden.cfg force  (via {via})", out)
    else:
        out = conn.send_config_set(_fmt(sc["recover"], ctx))
        tl.block(f"Recovery config (via {via})", out)
        _exec(conn, sc.get("recover_exec", []), tl)
    try:
        conn.save_config()
    except Exception:  # console มี syslog แทรก prompt -> สั่ง write memory ตรงๆ
        conn.write_channel("\r")
        conn.send_command_timing("end")
        conn.send_command_timing("write memory", read_timeout=30)
    conn.disconnect()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["list", "run", "inject", "diagnose", "recover"])
    ap.add_argument("scenario", nargs="?", choices=list(SCENARIOS))
    ap.add_argument("--rollback", action="store_true", help="กู้ด้วย configure replace golden.cfg")
    args = ap.parse_args()

    if args.action == "list" or not args.scenario:
        for k, s in SCENARIOS.items():
            print(f"{k:9} {s['title']}\n{'':9} คาดว่า: {s['expect']}")
        return

    inv = load_inventory()
    sc = SCENARIOS[args.scenario]
    tl = Timeline(args.scenario, sc)
    banner(f"{args.action.upper()} — {sc['title']}")

    if args.action == "run":
        tl.step("Baseline verification")
        base = verify.run(inv, inv, quick=True)
        verify.report(base, "Baseline (before fault)", save=False)
        tl.block("Baseline", "\n".join(f"{n}: {c} = {s}" for n, r in base.items() if not isinstance(r, Exception)
                                       for c, s, _ in r["results"]))
    if args.action in ("run", "inject"):
        tl.step("INJECT fault")
        inject(args.scenario, sc, inv, tl)
        if args.action == "run":
            print(f"   รอ {sc['wait']} วินาทีให้อาการแสดง...")
            time.sleep(sc["wait"])
    if args.action in ("run", "diagnose"):
        tl.step("DIAGNOSE: เก็บอาการ (show / syslog / debug)")
        diagnose(args.scenario, sc, inv, tl)
    if args.action in ("run", "recover"):
        tl.step("RECOVER " + ("(configure replace golden)" if args.rollback else "(targeted fix)"))
        recover(args.scenario, sc, inv, tl, args.rollback)
        print(f"   รอ {sc['converge']} วินาทีให้ converge...")
        time.sleep(sc["converge"])
        tl.step("POST-RECOVERY verification")
        post = verify.run(inv, inv, quick=True)
        fails = verify.report(post, "After recovery", save=False)
        tl.block("Post-recovery", "\n".join(f"{n}: {c} = {s}" for n, r in post.items() if not isinstance(r, Exception)
                                            for c, s, _ in r["results"]) + f"\nFAIL = {fails}")
    tl.save()


if __name__ == "__main__":
    main()
