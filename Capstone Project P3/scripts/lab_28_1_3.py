"""lab_28_1_3.py — ทำตามใบงาน 28.1.3 "Use the Netmiko Python Module to Configure a Router"
แต่ชี้ไปที่ Real IOS (vIOS) บน GNS3 แทน CSR1kv ใน DEVASC VM

Part 1  เชื่อมต่อ SSH ด้วย ConnectHandler
Part 2  ส่ง show command  (send_command) + แปลงผลเป็น structured data ด้วย TextFSM
Part 3  ส่ง config command (send_config_set) — สร้าง Loopback + description
Part 4  ตรวจผลลัพธ์ แล้ว save config

ใช้งาน:  python scripts/lab_28_1_3.py               (ค่าเริ่มต้น = R1-HQ)
         python scripts/lab_28_1_3.py --device R2-BR1 --cleanup
"""
import argparse
from pprint import pprint

from common import banner, connect, load_inventory, select

LAB_LOOPBACKS = [
    # (ชื่อ interface, IPv4, คำอธิบาย) — ใช้เลข 101/102 เพื่อไม่ชน Loopback0 ที่ OSPF ใช้
    ("Loopback101", "192.168.101.1", "Netmiko Lab 28.1.3 - loopback A"),
    ("Loopback102", "192.168.102.1", "Netmiko Lab 28.1.3 - loopback B"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="R1-HQ")
    ap.add_argument("--cleanup", action="store_true", help="ลบ loopback ของแลปออกหลังทดสอบ")
    args = ap.parse_args()
    dev = select(load_inventory(), [args.device])[args.device]

    banner(f"Part 1: Connect to {dev['name']} ({dev['mgmt_ip']}) via SSH")
    conn = connect(dev, via="ssh", tag="lab2813")
    print("Prompt:", conn.find_prompt())

    banner("Part 2: send_command('show ip interface brief')")
    print(conn.send_command("show ip interface brief"))
    parsed = conn.send_command("show ip interface brief", use_textfsm=True)
    print("\n-- TextFSM structured output (list of dict) --")
    pprint(parsed)
    up = [i["interface"] for i in parsed if isinstance(i, dict) and i.get("status") == "up"]
    print(f"\nInterface ที่ status=up: {up}")

    banner("Part 3: send_config_set() — create loopbacks")
    cmds = []
    for ifname, ip, desc in LAB_LOOPBACKS:
        cmds += [f"interface {ifname}", f"description {desc}", f"ip address {ip} 255.255.255.0"]
    print(conn.send_config_set(cmds))

    banner("Part 4: Verify + save")
    print(conn.send_command("show ip interface brief | include Loopback"))
    print(conn.send_command("show running-config | section interface Loopback10"))

    if args.cleanup:
        banner("Cleanup: remove lab loopbacks")
        print(conn.send_config_set([f"no interface {i}" for i, _, _ in LAB_LOOPBACKS]))
    print(conn.save_config())
    conn.disconnect()
    print("\n[OK] Lab 28.1.3 complete — session log อยู่ที่ logs/")


if __name__ == "__main__":
    main()
