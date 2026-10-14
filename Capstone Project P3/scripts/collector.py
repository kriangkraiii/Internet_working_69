"""collector.py — Syslog (UDP 514) + NetFlow v9 (UDP 2055) collector แบบเบาๆ สำหรับเดโม
รันบน devbox ของ sandbox (10.10.20.50) ก่อน deploy:

  sudo python3 scripts/collector.py                  (514 ต้องใช้ root)
  python3 scripts/collector.py --syslog-port 5514     (ถ้าไม่มี root — ต้องแก้ logging host ... transport udp port 5514)

- Syslog ทุกบรรทัด -> logs/syslog.log (+ แสดงบนจอ, ไฮไลต์ OSPF/CRYPTO/LINK/SEC)
- NetFlow v9 -> นับ packet/flow record ต่อ exporter แสดงทุก 30 วินาที (พิสูจน์ว่า FNF ส่งข้อมูลจริง)
  ดูรายละเอียด field ด้วย Wireshark: Decode As -> UDP 2055 -> CFLOW
"""
import argparse
import datetime as dt
import selectors
import socket
import struct
import time
from collections import Counter
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "logs" / "syslog.log"
HIGHLIGHT = ("OSPF", "CRYPTO", "LINK", "LINEPROTO", "SEC", "CONFIG_I", "PARSER")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bind", default="0.0.0.0")
    ap.add_argument("--syslog-port", type=int, default=514)
    ap.add_argument("--netflow-port", type=int, default=2055)
    args = ap.parse_args()

    LOG.parent.mkdir(exist_ok=True)
    sel = selectors.DefaultSelector()
    for port, kind in ((args.syslog_port, "syslog"), (args.netflow_port, "netflow")):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((args.bind, port))
        sel.register(s, selectors.EVENT_READ, kind)
        print(f"[*] {kind} listening on udp/{port}")

    nf_pkts, nf_flows = Counter(), Counter()
    last = time.time()
    with LOG.open("a", encoding="utf-8") as fh:
        while True:
            for key, _ in sel.select(timeout=1):
                data, (src, _) = key.fileobj.recvfrom(65535)
                if key.data == "syslog":
                    msg = data.decode(errors="replace").strip()
                    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {src} {msg}"
                    fh.write(line + "\n")
                    fh.flush()
                    mark = ">>" if any(h in msg for h in HIGHLIGHT) else "  "
                    print(f"{mark} {line}")
                elif len(data) >= 20:
                    version, count = struct.unpack("!HH", data[:4])
                    if version == 9:
                        nf_pkts[src] += 1
                        nf_flows[src] += count
            if time.time() - last >= 30 and nf_pkts:
                last = time.time()
                summary = ", ".join(f"{ip}: {nf_pkts[ip]} pkts/{nf_flows[ip]} records" for ip in sorted(nf_pkts))
                print(f"[NetFlow v9] {summary}")


if __name__ == "__main__":
    main()
