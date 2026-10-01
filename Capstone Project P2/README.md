# Capstone Project Part II — AAA Authentication (กลุ่ม 9)

CP353301 Internetworking · Simulation Demo บน Cisco Packet Tracer
ต่อยอดแลบ 26.2.5 *Configure AAA Authentication on Cisco Routers*: R1 ใช้ local AAA + SSH, R2 ใช้ TACACS+, R3 ใช้ RADIUS พร้อม IPv6 dual-stack และการฉีดข้อผิดพลาด

## สิ่งที่ต้องส่ง
| ไฟล์ | สถานะ |
|---|---|
| `grp9-AAA-Capstone.pkt` | **กลุ่มต้องสร้างเอง** ใน Packet Tracer ตาม [RUNBOOK.md](RUNBOOK.md) หัวข้อ 1.1 |
| `configs/running/*.txt` (running-config ทุก router) | **กลุ่มต้องเก็บเอง** หลังวางสคริปต์แล้ว |
| `grp9-AAA-Runbook.pdf` | สคริปต์การสาธิต / รันบุ๊ก (สร้างจาก `RUNBOOK.md`) |
| `grp9-AAA-Technical-Report.pdf` | รายงานสรุปทางเทคนิค (สร้างจาก `report/report.html`) |
| สไลด์ Canva | ลิงก์ Canva + `grp9-AAA-Slides.pdf` |

## โครงสร้าง
```
RUNBOOK.md                  คู่มือเดโมฉบับแก้ไขได้ (ต้นฉบับของ grp9-AAA-Runbook.pdf)
configs/R1.txt R2.txt R3.txt สคริปต์วางทั้งไฟล์ (คำสั่งของแลบ + SSH บน R2/R3 + IPv6)
configs/hosts-ipv6.md       ค่าที่ต้องกรอกผ่าน GUI ของ PC/Server และผู้ใช้ netops2/netops3
configs/faults/             TS1 TACACS+ key ไม่ตรง, TS2 ลิงก์ RADIUS ล่ม, TS3 SSH ถูกปิด
configs/running/            ที่เก็บ show running-config หลังทำเสร็จ
report/report.html          ต้นฉบับรายงาน
report/runbook.html         RUNBOOK.md ที่แปลงเป็น HTML แล้ว
report/topology.svg / .png  แผนภาพโทโพโลยี (ลาก .png ใส่สไลด์หน้า 4)
```

## สร้าง PDF ใหม่หลังแก้ไข
```bash
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless --no-pdf-header-footer --virtual-time-budget=8000 \
  --print-to-pdf="$PWD/grp9-AAA-Technical-Report.pdf" "file://$PWD/report/report.html"
"$CH" --headless --no-pdf-header-footer --virtual-time-budget=8000 \
  --print-to-pdf="$PWD/grp9-AAA-Runbook.pdf" "file://$PWD/report/runbook.html"
```
ต้องต่ออินเทอร์เน็ตเพื่อโหลดฟอนต์ Sarabun ถ้าแก้ `RUNBOOK.md` ต้องแปลงเป็น `report/runbook.html` ใหม่ก่อน (ใช้ตัวแปลง Markdown ใดก็ได้ แล้วคง `<style>` เดิมไว้)

## สิ่งที่ยังไม่ได้ทดสอบ
สคริปต์ตรวจไวยากรณ์เทียบกับสคริปต์ของแลบแล้ว แต่**ยังไม่ได้รันใน Packet Tracer** สิ่งที่ต้องยืนยันตอนซ้อม (checklist ใน RUNBOOK หัวข้อ 1.2):
- พฤติกรรมของ `Admin2` ระหว่างที่ TACACS+ key ผิด (fallback ไป local หรือไม่)
- คำสั่ง `debug aaa authentication`, `debug tacacs`, `debug radius` ใช้ได้ใน Packet Tracer หรือไม่
- SSH ผ่าน IPv6 จาก PC (T12)
- Check Results ยังได้ 100% หลังเพิ่มส่วนขยาย
- ผลจริงในรายงานหัวข้อ 6 ยังเว้นว่างไว้ให้กรอกหลังซ้อม
