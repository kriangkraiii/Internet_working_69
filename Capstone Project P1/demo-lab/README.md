# demo-lab — ชุดเดโม Automation (กลุ่ม 9)

ชุดไฟล์นี้ใช้สร้างแลบสาธิต Ansible + EEM ของสไลด์ส่วนที่ 3 บน **Cisco Modeling Labs (DevNet Sandbox)**

## เริ่มใช้ใน 5 ขั้นตอน
1. จอง sandbox **Cisco Modeling Labs** ที่ https://developer.cisco.com/site/sandbox/ แล้วต่อ VPN ตามอีเมล
2. ใน CML: **Import** ไฟล์ `grp9-automation-lab.yaml` → ตรวจ connector (`sandbox-bridge` = System Bridge, `internet-nat` = NAT) → **Start**
3. รอประมาณ 5–8 นาที แล้วรัน `ssh grp9@10.10.20.190` (รหัส `Grp9@lab`) → `cat /etc/grp9-ready` ต้องขึ้น `READY`
4. `cd ~/lab/ansible && ansible-playbook precheck.yml -J` (vault: `grp9lab`)
5. ทำตาม [RUNBOOK.md](RUNBOOK.md) หัวข้อ 3 (สคริปต์การสาธิต)

## โครงสร้าง
```
grp9-automation-lab.yaml     ไฟล์ import เข้า CML (สร้างจาก tools/build_lab.py)
RUNBOOK.md                   คู่มือละเอียด: เตรียมแลบ, สคริปต์เดโม, TS1/TS2, reset, แผนสำรอง
configs/                     Day-0 ของ R1/R2, EEM applet, cloud-init ของ automation-host
ansible/                     inventory, site.yml, precheck/verify/reset, vault (รหัส grp9lab)
tools/build_lab.py           สร้างไฟล์ lab ใหม่หลังแก้ config หรือ playbook
```

## สิ่งที่ทดสอบแล้ว
- **Playbook ทุกไฟล์:** ผ่าน `--syntax-check` และ option ของทุก task ตรงกับเอกสารโมดูล (ansible-core 2.21.4, cisco.ios 11.5.1)
- **Resource module แบบ offline** (`state: rendered`): ได้คำสั่ง `interface loopback0`, `ip address 1.1.1.1 255.255.255.255`, `no shutdown` และ `router ospf 1`
- **cloud-init ของ automation-host:** ผ่าน `cloud-init schema` และ script ติดตั้งจบที่ `READY` ใน Ubuntu 24.04
- **ไฟล์ lab:** parse ได้ และ link ทุกเส้นชี้ไปยัง interface ที่มีอยู่จริง

## สิ่งที่ยังไม่ได้ทดสอบ
การรันกับ IOSv จริงใน sandbox ยังไม่ได้ทดสอบ ให้ใช้ checklist ใน RUNBOOK หัวข้อ 1.5 ตรวจก่อนนำเสนอ
