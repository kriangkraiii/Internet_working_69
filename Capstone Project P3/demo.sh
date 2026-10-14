#!/usr/bin/env bash
# demo.sh — รันเดโม Capstone P3 ตั้งแต่ต้นจนจบ พร้อมคำบรรยายแต่ละขั้น (ใช้อัดคลิปสำรอง)
#
#   ./demo.sh            เดโมหลัก: Lab 28.1.3 -> Deploy -> Verify -> PSK -> ACL lockout  (~12 นาที)
#   ./demo.sh --full     + MTU mismatch + Link flap                                      (~20 นาที)
#   VOICE=1 ./demo.sh    อ่านคำบรรยายออกเสียงด้วย (ต้องมีเสียงไทย "Kanya" ใน macOS)
#
# อัดคลิป: กด ⌘⇧5 -> Record Selected Portion (คลุมหน้าต่าง Terminal) -> Record แล้วค่อยรันสคริปต์
set -u
cd "$(dirname "$0")"
[ -f .venv/bin/activate ] && source .venv/bin/activate
FULL=0; [ "${1:-}" = "--full" ] && FULL=1
B=$'\e[1m'; C=$'\e[38;5;81m'; Y=$'\e[38;5;221m'; G=$'\e[38;5;114m'; D=$'\e[2m'; R=$'\e[0m'
STEP=0

say_th() { [ "${VOICE:-0}" = "1" ] && say -v Kanya "$1" 2>/dev/null; }
scene() {               # scene "หัวข้อ" "คำบรรยาย..." [วินาทีที่ค้างไว้ให้อ่าน]
  STEP=$((STEP+1)); clear
  printf "\n${C}${B}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}\n"
  printf "${C}${B}   ขั้นที่ %d │ %s${R}\n" "$STEP" "$1"
  printf "${C}${B}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}\n\n"
  printf "${Y}%s${R}\n\n" "$2" | fold -s -w 100 | sed 's/^/   /'
  say_th "$2"
  sleep "${3:-6}"
}
run() {                 # แสดงคำสั่งแบบพิมพ์ทีละตัว แล้วรันจริง
  printf "${G}\$ ${R}"
  for ((i=0; i<${#1}; i++)); do printf "%s" "${1:i:1}"; sleep 0.02; done
  printf "\n"; eval "$1"; printf "\n"
}
cli() {                 # รันคำสั่ง show บน router ผ่าน Netmiko แล้วแสดงแบบ CLI
  PYTHONPATH=scripts python - "$@" <<'PY'
import sys
from common import load_inventory, connect
dev, cmds = sys.argv[1], sys.argv[2:]
c = connect(load_inventory()[dev], tag="demo")
for cmd in cmds:
    print(f"\033[38;5;81m{dev}#\033[1m{cmd}\033[0m")
    print(c.send_command(cmd, read_timeout=60)); print()
c.disconnect()
PY
}
pause() { sleep "${1:-4}"; }

# ───────────────────────────────────────────────────────────────────────────
scene "Capstone Project Part III — Network Automation ด้วย Netmiko บน Real IOS" \
"โปรเจคนี้ต่อยอดจาก Lab 28.1.3 ที่ใช้ Netmiko ตั้งค่า router ตัวเดียว ไปเป็นการ deploy, verify และ troubleshoot เครือข่ายองค์กร 3 site บน Cisco IOSv ใน Cisco Modeling Labs ของ DevNet Sandbox ด้วย Python ทั้งหมด" 8
cat <<'TOPO'
                    ┌──────── R0-ISP (Internet / NTP master) ────────┐
                    │ 203.0.113.0/30      203.0.113.4/30      203.0.113.8/30
   10.1.10.0/24 ── R1-HQ (Hub) ══ Tunnel12 GRE/IPsec ══ R2-BR1 ── 10.2.10.0/24
                     ║
                     ╚═══════════ Tunnel13 GRE/IPsec ══ R3-DC  ── 10.3.10.0/24
     OSPFv2 + OSPFv3 วิ่งในอุโมงค์เท่านั้น │ OOB Mgmt Gi0/3 → 10.10.20.181-184
TOPO
pause 10

scene "Source of Truth: inventory.yaml + Jinja2 template" \
"ค่าทุกอย่างอยู่ในไฟล์ inventory.yaml ไฟล์เดียว ส่วน template ไม่มี IP ฝังอยู่เลย config ของ router ทุกตัวจึงสร้างจากแม่แบบเดียวกัน ไม่มีความผิดพลาดจากการพิมพ์มือ" 7
run "sed -n '/R2-BR1:/,/R3-DC:/p' inventory.yaml | head -14"
pause 5
run "python scripts/deploy.py --dry-run"
pause 3
run "grep -A6 'interface Tunnel12' configs/rendered/R2-BR1.cfg"
pause 6

scene "Lab 28.1.3 — Use the Netmiko Python Module to Configure a Router" \
"ทำตามใบงานต้นฉบับบน IOSv จริง ได้แก่ เชื่อมต่อด้วย ConnectHandler, ส่ง show ip interface brief ด้วย send_command, แปลงผลเป็นข้อมูลด้วย TextFSM แล้วสร้าง Loopback ด้วย send_config_set" 8
run "python scripts/lab_28_1_3.py --device R1-HQ --cleanup 2>&1 | tail -40"
pause 6

scene "Deploy — Backup → Push → Save → Diff" \
"สคริปต์ deploy สำรอง running-config ก่อนและหลังเปลี่ยนทุกครั้ง แล้วทำ diff ไว้ การรันซ้ำจึงปลอดภัย ถ้า config ตรงกับ template อยู่แล้ว จำนวนบรรทัดที่เปลี่ยนจะเป็นศูนย์" 7
run "time python scripts/deploy.py R2-BR1"
pause 5

scene "Verification อัตโนมัติ 62 รายการ" \
"ตรวจทั้ง Control plane คือ OSPFv2, OSPFv3 และ IKE, ทั้ง Data plane คือ ESP และ ping IPv4 IPv6 ข้าม site และทั้ง Management plane คือ NTP, CoPP, NetFlow, Syslog, SNMPv3 และ ACL ผลต้องได้ FAIL 0" 8
run "python scripts/verify.py"
pause 8

scene "ยืนยันด้วย CLI จริงบน R1-HQ" \
"ดู OSPF neighbor ทั้งสอง spoke อยู่ในสถานะ FULL, IKE SA อยู่ในสถานะ QM_IDLE และตัวนับ ESP encaps เพิ่มขึ้น แปลว่าทราฟฟิกระหว่าง site ถูกเข้ารหัสจริง" 7
cli R1-HQ "show ip ospf neighbor" "show crypto isakmp sa" "show crypto ipsec sa | include interface|encaps|decaps" "show policy-map control-plane | include Class-map|conformed|exceeded"
pause 10

scene "Fault Injection #1 — IPsec Pre-Shared Key ไม่ตรงกัน" \
"จำลองว่ามีคนแก้ PSK บน R2-BR1 ผิด แล้ว clear crypto session สคริปต์จะเก็บอาการ แก้ไขแบบเจาะจงจุด และตรวจซ้ำอัตโนมัติ อาการที่คาดว่าจะเห็นคือ IKE ค้างที่ MM_KEY_EXCH และ R1 แจ้ง IKMP_BAD_MESSAGE" 9
run "python scripts/fault.py run psk"
pause 3
scene "RCA — INC-01 PSK mismatch" \
"Root cause: Phase 1 ล้มที่ข้อความ MM5/MM6 ซึ่งเป็นจุดแรกที่ใช้ key ที่สร้างจาก PSK ส่วน tunnel interface ยัง up อยู่ จึงต้องไล่ดูทีละ layer และ PARSER-5-CFGLOG ระบุได้ว่ามีการแก้ key การป้องกันคือให้ทุกการเปลี่ยน config ผ่าน pipeline และในระยะยาวเปลี่ยนไปใช้ IKEv2 กับ certificate" 6
run "grep -E 'MM_KEY_EXCH|IKMP_BAD_MESSAGE|DOWN-NEGOTIATING' \$(ls -td evidence/fault_psk_* | head -1)/timeline.md | head -6"
pause 10

scene "Fault Injection #2 — ACL บน VTY ตัดช่องทาง Management (R3-DC)" \
"ผูก access-class ที่อนุญาตผิด host เข้ากับ VTY ทำให้ SSH จาก automation host เข้าไม่ได้ จากนั้นกู้คืนผ่าน Console Server ของ CML ซึ่งเป็นช่องทาง Out-of-Band โดยให้ Netmiko ใช้ terminal_server แล้ว redispatch เป็น cisco_ios ระหว่างนั้น Data plane ยังทำงานปกติ" 9
run "python scripts/fault.py run mgmt-acl"
pause 3
run "grep -E 'NetmikoTimeout|denied|access-class' \$(ls -td evidence/fault_mgmt-acl_* | head -1)/timeline.md | head -6"
pause 10

if [ "$FULL" = "1" ]; then
scene "Fault Injection #3 — OSPF MTU mismatch บน Tunnel12" \
"ตั้ง ip mtu เป็น 1300 ฝั่ง R2 ส่วน R1 เป็น 1400 Hello ยังผ่าน แต่ DBD ถูกปฏิเสธ adjacency จึงค้างที่ EXSTART และ EXCHANGE ตาม RFC 2328 วิธีแก้ที่ถูกคือทำให้ MTU ตรงกัน ไม่ใช้ mtu-ignore" 9
run "python scripts/fault.py run mtu"
run "grep -E 'EXSTART|EXCHANGE|larger interface MTU' \$(ls -td evidence/fault_mtu_* | head -1)/timeline.md | head -5"
pause 8

scene "Fault Injection #4 — WAN link flapping" \
"สั่ง Gi0/0 ของ R2 down/up สลับกัน 3 รอบ ทุกครั้งที่ link down ทั้ง tunnel, OSPF และ IKE ต้องสร้างใหม่ การป้องกันคือใช้ interface dampening, BFD และมี ISP สำรอง" 8
run "python scripts/fault.py run flap"
pause 6
fi

scene "สรุป" \
"ระบบนี้สร้างและตั้งค่าเครือข่ายทั้งองค์กรจากไฟล์เดียว ตรวจสอบได้ 62 รายการภายในไม่ถึงหนึ่งนาที และจำลองความล้มเหลวพร้อมกู้คืนได้ซ้ำ โดยเก็บหลักฐานสำหรับ RCA ไว้ในโฟลเดอร์ evidence ขอบคุณครับ" 6
run "ls evidence/"
pause 8
printf "\n${D}— จบการเดโม —${R}\n"
