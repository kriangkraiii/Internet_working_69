# Capstone P3 — Netmiko Network Automation บน Real IOS (Cisco Modeling Labs)

ต่อยอดจาก **Lab 28.1.3 Use the Netmiko Python Module to Configure a Router** จากการตั้งค่า router ตัวเดียว ไปเป็นการสร้าง, deploy, verify และ troubleshoot เครือข่ายองค์กรแบบ Multi-Branch (HQ + Branch + Data Center) บน Cisco IOSv ใน **Cisco DevNet Sandbox – CML** ด้วย Python ทั้งหมด

```
                         ┌──────────── R0-ISP (Internet/Underlay, NTP master) ────────────┐
                  Gi0/0  │ 203.0.113.0/30          Gi0/1 203.0.113.4/30        Gi0/2 203.0.113.8/30
                         │                                │                              │
   LAN 10.1.10.0/24 ── R1-HQ (Hub) ══Tunnel12 (GRE/IPsec)══ R2-BR1 ── LAN 10.2.10.0/24
                           ║
                           ╚══════Tunnel13 (GRE/IPsec)══ R3-DC ── LAN 10.3.10.0/24
   OSPFv2 + OSPFv3 area 0 วิ่งบน Tunnel เท่านั้น
   OOB Mgmt: Gi0/3 ทุกตัว -> SW-MGMT -> External Connector (bridge0) -> 10.10.20.0/24 ของ sandbox
   R0 .181 | R1 .182 | R2 .183 | R3 .184 | devbox (Netmiko + Syslog + NetFlow) .50 | CML .161
```

## โครงสร้างไฟล์

| ไฟล์ | หน้าที่ |
|---|---|
| `inventory.yaml` | Source of truth: IP, interface และ credential ทั้งหมด (router + CML) แก้ที่ไฟล์นี้ที่เดียว |
| `templates/*.j2` | Jinja2 config: `bootstrap` (Day-0), `base` (AAA/SSH/SNMPv3/Syslog/NTP), `site` (Dual-stack, GRE-IPsec, OSPFv2/v3, ACL, CoPP, NetFlow), `isp` |
| `scripts/cml_lab.py` | CML API: build topology + Day-0, status, export `.yaml`, packet capture → `.pcap`, flap link, stop/wipe/delete |
| `scripts/lab_28_1_3.py` | ทำตามใบงาน 28.1.3 ทุก Part บน IOSv |
| `scripts/deploy.py` | Render → Backup → Push แบบขนาน → Save → Diff (`--dry-run`, `--golden`) |
| `scripts/verify.py` | ตรวจ 62 รายการ (OSPF, IKE/IPsec, ping v4/v6, NTP, CoPP, FNF, SNMPv3 …) แล้วออกรายงาน PASS/FAIL |
| `scripts/fault.py` | 4 scenario: `mtu`, `psk`, `mgmt-acl`, `flap` ใช้ได้ทั้ง inject, diagnose และ recover/rollback และเก็บ timeline เป็นหลักฐาน RCA |
| `scripts/collector.py` | Syslog (UDP 514) + NetFlow v9 (UDP 2055) collector รันบน devbox |
| `report/` | Demo Runbook & Technical Report (HTML + PDF) |

## เริ่มใช้งาน (สรุป ดูรายละเอียดใน Runbook)

```bash
# 0) จอง sandbox "Cisco Modeling Labs" แล้วต่อ VPN จากนั้น copy โฟลเดอร์นี้ไปไว้บน devbox
scp -r "Capstone Project P3" developer@10.10.20.50:~/capstone && ssh developer@10.10.20.50
cd ~/capstone && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt "virl2-client==<เวอร์ชันเดียวกับ CML>.*"

python scripts/deploy.py --dry-run          # 1) ตรวจ config ที่จะ push (ไม่แตะอุปกรณ์)
python scripts/cml_lab.py build             # 2) สร้าง lab + Day-0 + start (รอประมาณ 5 นาที)
sudo .venv/bin/python scripts/collector.py  # 3) เปิด collector (terminal แยก)
python scripts/lab_28_1_3.py                # 4) ใบงาน 28.1.3
python scripts/deploy.py                    # 5) push config เต็ม
python scripts/verify.py                    # 6) ต้องได้ FAIL 0
python scripts/deploy.py --golden           # 7) เก็บ golden config
python scripts/fault.py run psk             # 8) fault injection + recovery + evidence
python scripts/cml_lab.py export            # 9) topology/Capstone-P3.yaml สำหรับส่งงาน
```

> Credential ในไฟล์เป็นค่าสำหรับแลปเท่านั้น ตอนเดโมควร override ด้วย `export NET_USER=… NET_PASS=… NET_SECRET=… CML_USER=… CML_PASS=…`
