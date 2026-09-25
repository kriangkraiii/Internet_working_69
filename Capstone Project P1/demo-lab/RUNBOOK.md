# คู่มือเดโม: Ansible + EEM บน Cisco Modeling Labs (กลุ่ม 9)

คู่มือนี้พาทำตั้งแต่จอง sandbox จนสาธิตจริงตามสไลด์ 10–18 (ส่วนที่ 3 ใช้เวลาประมาณ 7 นาที)
คำสั่งทุกบรรทัดคัดลอกไปวางได้ทันที ผลลัพธ์ที่แสดงเป็นตัวอย่าง รูปแบบจะตรงกับของจริง แต่เวลา ตัวเลข และช่องว่างอาจต่างเล็กน้อย

---

## 0. ภาพรวม

```
 Mac (ต่อ DevNet VPN)
   │  ssh grp9@10.10.20.190
   ▼
 [sandbox-bridge]──sbx0 ┌──────────────────┐ inet0──[internet-nat]
                        │ automation-host  │  (apt / pip)
                        │ Ubuntu + Ansible │
                        └──────┬───────────┘
                         mgmt0 │ 192.168.100.10
                        ┌──────┴──────┐
                        │   SW-MGMT   │  192.168.100.0/24
                        └──┬───────┬──┘
                Gi0/0 .11  │       │  Gi0/0 .12
                        ┌──┴──┐ ┌──┴──┐
                        │ R1  │ │ R2  │   IOSv 15.9
                        └──┬──┘ └──┬──┘
                   Gi0/1 .1└───────┘.2 Gi0/1   10.12.12.0/30  OSPF area 0
                   Lo0 1.1.1.1/32      Lo0 2.2.2.2/32
```

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `grp9-automation-lab.yaml` | import เข้า CML แล้วได้แลบครบชุด (R1, R2, switch, Ubuntu ที่ติดตั้ง Ansible ให้เอง) |
| `configs/R1-day0.cfg`, `R2-day0.cfg` | Day-0 ของ router (ฝังอยู่ในไฟล์ lab แล้ว) |
| `configs/R1-eem.cfg` | EEM applet สำหรับ Demo 2 (วางสดตอนสาธิต) |
| `ansible/` | โปรเจกต์ Ansible (ถูกคัดลอกไปไว้ที่ `~/lab/ansible` บนเครื่อง Ubuntu) |
| `tools/build_lab.py` | สร้าง `grp9-automation-lab.yaml` ใหม่หลังแก้ไฟล์ใด ๆ |

**รหัสผ่านในแลบ (ใช้ในแลบเท่านั้น)**

| ใช้กับ | ชื่อผู้ใช้ | รหัสผ่าน |
|---|---|---|
| Ubuntu automation-host | `grp9` | `Grp9@lab` |
| R1 / R2 (SSH) | `admin` | `Cisco@123` |
| ansible-vault (`-J`) | – | `grp9lab` |

---

## 1. เตรียมแลบ (ทำล่วงหน้าอย่างน้อย 1 วัน)

### 1.1 จอง sandbox
1. เข้า https://developer.cisco.com/site/sandbox/ แล้ว login ด้วยบัญชี Cisco
2. ค้นหา **Cisco Modeling Labs** → **Reserve** → เลือกช่วงเวลาให้ครอบคลุมเวลาซ้อมหรือเวลานำเสนอ
3. รออีเมลยืนยัน (ประมาณ 15–45 นาที) ในอีเมลจะมี **VPN host, username, password** และข้อมูลเข้า CML

> วันนำเสนอให้จองล่วงหน้าและเผื่อเวลาอย่างน้อย 1 ชั่วโมงก่อนขึ้นพูด

### 1.2 ต่อ VPN จาก Mac
- ใช้ **Cisco Secure Client** ตามลิงก์ในอีเมล หรือ `brew install openconnect` แล้วรัน
  `sudo openconnect <VPN host จากอีเมล>` ใส่ username/password จากอีเมล
- ทดสอบ: เปิดหน้า CML ตาม URL ในอีเมลแล้ว login ได้

### 1.3 Import แลบ
1. ใน CML: **Dashboard → Import** → เลือกไฟล์ `grp9-automation-lab.yaml`
2. เปิดแลบ `grp9-automation-demo` แล้วตรวจ external connector 2 ตัว:
   - `sandbox-bridge` → **System Bridge (bridge0)**
   - `internet-nat` → **NAT**
   ถ้าไม่ตรง ให้คลิกที่ node → แท็บ **Config** → เลือกให้ถูก
3. ตรวจว่า IP `10.10.20.190` ยังไม่มีใครใช้: บน Mac รัน `ping -c 2 10.10.20.190` แล้ว**ต้องไม่มีการตอบกลับ**
   ถ้ามีการตอบกลับ ให้แก้ `SBX_IP` ใน `tools/build_lab.py` → รัน `python3 tools/build_lab.py` → import ใหม่

### 1.4 Start แลบ แล้วรอ
กด **Start Lab** แล้วรอประมาณ 5–8 นาที เครื่อง Ubuntu จะติดตั้ง Ansible เองระหว่างนี้

### 1.5 ตรวจความพร้อม (checklist)
บน Mac:
```bash
ssh grp9@10.10.20.190            # รหัส Grp9@lab
```
บน automation-host:
```bash
cat /etc/grp9-ready              # ต้องขึ้น READY ...
ip -br addr                      # mgmt0 192.168.100.10/24, sbx0 10.10.20.190/24, inet0 (DHCP)
ping -c 2 192.168.100.11
ping -c 2 192.168.100.12
ssh r1 'show ip ssh' | head -1   # SSH Enabled - version 2.0   (รหัส Cisco@123)
cd ~/lab/ansible
ansible-playbook precheck.yml -J # vault: grp9lab → ok ทั้ง R1 และ R2
```
ถ้ายังไม่มีไฟล์ `/etc/grp9-ready` ให้รัน `sudo cloud-init status --wait` แล้วรอ
ถ้า SSH จาก Mac ไม่ได้ ให้เปิด **Console** ของ automation-host ในหน้าเว็บ CML แทน (ดูหัวข้อ 7)

---

## 2. จัดหน้าจอก่อนขึ้นพูด

เปิด Terminal บน Mac 4 แท็บ และตั้งฟอนต์ ≥ 20pt:

| แท็บ | คำสั่ง | ใช้ในสไลด์ |
|---|---|---|
| 1 `ansible` | `ssh grp9@10.10.20.190` แล้ว `cd ~/lab/ansible` | 12–13, 16 |
| 2 `R1` | `ssh grp9@10.10.20.190` แล้ว `ssh r1` แล้ว `terminal monitor` | 14–15, 17 |
| 3 `syslog` | `ssh grp9@10.10.20.190` แล้ว `tail -f /var/log/network.log` | 15, 17 |
| 4 `R2` | **Console ของ R2 ในหน้าเว็บ CML** (ใช้ console เพราะ TS1 จะทำให้ SSH เข้า R2 ไม่ได้) | 16–17 |

> `terminal monitor` จำเป็นมาก ถ้าไม่สั่ง log และ debug จะไม่ขึ้นบนหน้าจอ SSH

ถ้าเคยซ้อมมาก่อน ให้ reset ก่อนขึ้นพูด (หัวข้อ 5)

---

## 3. สคริปต์การสาธิต (ประมาณ 7 นาที)

### 3.1 สไลด์ 10: Topology (30 วินาที)
- **ทำ:** สลับไปหน้า CML แล้วชี้ R1, R2, SW-MGMT และ automation-host
- **พูด:** "แลบรันบน Cisco Modeling Labs ของ DevNet Sandbox มี IOSv 2 ตัว และ Ubuntu ที่เป็น Ansible control node เครือข่ายจัดการ 192.168.100.0/24 แยกจากลิงก์ OSPF 10.12.12.0/30"

### 3.2 สไลด์ 11: Day-0 (30 วินาที) — แท็บ R1
```
show run | section line vty
show ip ssh
```
- **ต้องเห็น:** `transport input ssh` และ `SSH Enabled - version 2.0`
- **พูด:** "Agentless ไม่ได้แปลว่าไม่ต้องเตรียมอะไร router ต้องเปิด SSH ให้ได้ก่อน"

### 3.3 สไลด์ 12–13: Inventory, Playbook, Idempotency (2 นาที) — แท็บ ansible
```bash
cat inventory.yml
cat site.yml
ansible-inventory --graph
ansible-playbook site.yml -J --check -v
```
- **ชี้:** ผลของ `--check` ที่แสดงรายการ `commands` (เช่น `router ospf 1`) และ task Verify ที่ขึ้น `skipping`
- **พูด:** "dry-run บอกว่าจะส่งคำสั่งอะไร โดยยังไม่แตะอุปกรณ์"

```bash
ansible-playbook site.yml -J
```
- **ต้องเห็น:** `R1 : ok=4 changed=3 ... failed=0` และ R2 เหมือนกัน
  task Verify อาจใช้เวลา 10–40 วินาที เพราะรอ OSPF ขึ้นเป็น FULL ระหว่างรอให้อธิบาย `wait_for`

```bash
ansible-playbook site.yml -J
```
- **ต้องเห็น:** `changed=0` ทั้งสองเครื่อง
- **พูด:** "รันซ้ำแล้วไม่มีการเปลี่ยนแปลง นี่คือ idempotency เพราะโมดูลเทียบกับ running-config ก่อนส่ง"

### 3.4 สไลด์ 14: ตรวจผลบนอุปกรณ์ (1 นาที) — แท็บ R1
```
show ip ospf neighbor
show ip route ospf
show archive log config all
show logging | include CONFIG_I
```
- **ต้องเห็น:**
  - `2.2.2.2 ... FULL/...` (DR/BDR ขึ้นกับว่าเครื่องไหนเปิดก่อน)
  - `O 2.2.2.2 [110/2] via 10.12.12.2`
  - คำสั่งจาก `admin@vty0`
  - `Configured from console by admin on vty0 (192.168.100.10)`
- **Packet capture (ถ้ามีเวลา):** ดูหัวข้อ 4

### 3.5 สไลด์ 15: EEM (1 นาที) — แท็บ R1
```bash
# แท็บ ansible: แสดงไฟล์ที่จะวาง
cat ~/lab/configs/R1-eem.cfg
```
แท็บ R1 (วางทีละบล็อก):
```
configure terminal
event manager applet OSPF-NBR-DOWN
 event syslog pattern "OSPF-5-ADJCHG.*FULL to DOWN" ratelimit 60 maxrun 60
 action 1.0 cli command "enable"
 action 1.5 cli command "delete /force flash0:ospf-ev.txt"
 action 2.0 cli command "show ip ospf neighbor | redirect flash0:ospf-ev.txt"
 action 2.5 wait 6
 action 3.0 cli command "show ip route ospf | append flash0:ospf-ev.txt"
 action 4.0 syslog priority critical msg "OSPF nbr lost - evidence saved"
end
show event manager policy registered
debug event manager action cli
```
- **พูด:** "applet นี้รอ syslog ว่า neighbor หลุดจาก FULL แล้วเก็บหลักฐานลง flash ทันที ส่วน `ratelimit 60` กันไม่ให้ทำงานรัวตอนลิงก์ flap"
- **ถ้าถูกถามเรื่อง `wait 6`:** "IOS รอ SPF ประมาณ 5 วินาที (SPF throttle) ก่อนถอน route ถ้าเก็บ routing table ทันที จะยังเห็น route เดิมอยู่"
- ส่วนที่ applet ทำงานจริงจะเห็นใน 3.7

### 3.6 สไลด์ 16: Troubleshooting #1 — Misconfiguration (1.5 นาที)
**ทำให้เสีย** (แท็บ R2 / console):
```
configure terminal
crypto key zeroize rsa
yes
end
```
ต้องเห็น `%SSH-5-DISABLED: SSH 2.0 has been disabled`

**อาการ** (แท็บ ansible):
```bash
ansible-playbook site.yml -J
```
- **ต้องเห็น:** `fatal: [R2]: FAILED! ... Unable to connect to port 22 ...` (ข้อความอาจต่างเล็กน้อยตามเวอร์ชัน) ส่วน R1 ยังผ่าน

**วินิจฉัยไล่ทีละชั้น:**
```bash
ping -c 2 192.168.100.12          # ผ่าน → Layer 3 ปกติ
nc -zv 192.168.100.12 22          # Connection refused → ไม่มีบริการที่ port 22
```
แท็บ R2:
```
show ip ssh                       ! SSH Disabled ... Please create RSA keys
show crypto key mypubkey rsa      ! ไม่มี key
```
- **พูด:** "ping ผ่านแต่ port 22 refused แปลว่าไม่ใช่ปัญหาเส้นทาง แต่เป็นบริการบนอุปกรณ์ ถ้าเป็นปัญหาเส้นทางจะเห็นเป็น timeout"

**แก้และยืนยัน:**
```
configure terminal
crypto key generate rsa modulus 2048
end
```
ต้องเห็น `%SSH-5-ENABLED: SSH 2.0 has been enabled`
```bash
nc -zv 192.168.100.12 22          # succeeded
ssh-keygen -R 192.168.100.12      # key ใหม่ = host key ใหม่ → ลบ key เก่าที่ control node จำไว้
ansible-playbook site.yml -J      # R2: failed=0 (changed=0 เพราะ config เดิมยังอยู่)
```
- **พูด:** "สร้าง key ใหม่แล้ว fingerprint ของ R2 เปลี่ยน ถ้าไม่ลบ key เก่า Ansible จะปฏิเสธด้วย `host key mismatch` ซึ่งเป็นกลไกกันการปลอมตัว (MITM)"

### 3.7 สไลด์ 17: Troubleshooting #2 — Network Failure (1.5 นาที)
**ทำให้ลิงก์ล่ม** (แท็บ R2):
```
configure terminal
interface GigabitEthernet0/1
shutdown
end
```
- R2 ขึ้น log `... from FULL to DOWN, Neighbor Down: Interface down or detached` ทันที
- **ระหว่างรอ (สูงสุด 40 วินาที) ให้พูด:**
  "ฝั่ง R1 ลิงก์ยัง up เพราะเป็นลิงก์เสมือน R1 จึงรู้ได้จาก Hello ที่หายไปเท่านั้น ต้องรอ Dead timer 40 วินาที (4 เท่าของ Hello) พอหมดเวลา R1 จะสร้าง Router LSA ใหม่ รัน SPF และถอน 2.2.2.2 ออกจาก routing table"
- แท็บ R1 จะเห็น:
  - `%OSPF-5-ADJCHG: ... Nbr 2.2.2.2 ... from FULL to DOWN, Neighbor Down: Dead timer expired`
  - บรรทัด `%HA_EM-6-LOG: OSPF-NBR-DOWN : DEBUG(cli_lib) ...` (EEM ทำงาน)
- แท็บ syslog จะเห็น `%HA_EM-2-LOG: OSPF-NBR-DOWN: OSPF nbr lost - evidence saved`

**วินิจฉัย** (แท็บ R1):
```
undebug all
show ip ospf neighbor
show ip route 2.2.2.2
show ip ospf interface brief
show event manager history events
more flash0:ospf-ev.txt
```
แท็บ R2:
```
show ip interface brief | include 0/1
```
ต้องเห็น `administratively down`

**แก้และยืนยัน** (แท็บ R2):
```
configure terminal
interface GigabitEthernet0/1
no shutdown
end
```
แท็บ R1:
```
show ip route ospf
ping 2.2.2.2 source loopback0
```
- **ต้องเห็น:**
  - log `from LOADING to FULL, Loading Done`
  - `O 2.2.2.2 [110/2]`
  - ping ได้ `!!!!!`

---

## 4. Packet capture (สไลด์ 14)
1. ในหน้า CML คลิกลิงก์ `automation-host ↔ SW-MGMT` แล้วเลือก **Packet Capture → Start**
2. รัน `ansible-playbook precheck.yml -J` ในแท็บ ansible
3. **Stop → Download PCAP** แล้วเปิดใน Wireshark บน Mac ใช้ filter `tcp.port == 22`
4. ชี้ให้ผู้ฟังดู 3 จุด:
   - TCP handshake จาก `.10` ไป `.11:22`
   - `SSH-2.0` / Key Exchange
   - payload ที่ถูกเข้ารหัสทั้งหมด และไม่มี port อื่นของ agent เลย

---

## 5. ซ้อมซ้ำ / reset
แท็บ ansible:
```bash
ansible-playbook reset.yml -J     # ลบ OSPF + IP ของ Lo0/Gi0/1 และ shutdown Gi0/1
```
แท็บ R1:
```
configure terminal
no event manager applet OSPF-NBR-DOWN
end
delete /force flash0:ospf-ev.txt
```
แท็บ R2: ตรวจว่า `show ip ssh` ขึ้น Enabled (ถ้าไม่ใช่ ให้สร้าง key ใหม่)
แล้วเริ่มจากหัวข้อ 3.3 ได้เลย `site.yml` จะกลับมาให้ผล `changed=3` อีกครั้ง

---

## 6. แผนสำรอง (สำคัญ)
- **อัดวิดีโอตอนซ้อม:** ใช้ QuickTime → File → New Screen Recording ครอบทั้งหัวข้อ 3 ตามคำแนะนำของวิชาที่ให้มีวิดีโอเห็น log สด
- **เก็บ screenshot แทนตัวอย่างในสไลด์:**
  - สไลด์ 13: `--graph`, `--check -v`, การรัน 2 รอบ
  - สไลด์ 14: `show` ทั้ง 4 คำสั่ง
  - สไลด์ 15: `policy registered`, debug และ `history events`
  - สไลด์ 16: ทั้งแท็บ ansible และ R2
  - สไลด์ 17: ช่วงวินิจฉัยและช่วงแก้
- **ถ้า sandbox หรือ VPN ใช้ไม่ได้ในวันนำเสนอ:** เปิดวิดีโอที่อัดไว้ แล้วอธิบายตามสไลด์
- **ระยะเวลาจอง:** sandbox มีเวลาจำกัด ตรวจเวลาหมดอายุก่อนขึ้นพูด และต่อเวลาถ้าจำเป็น

---

## 7. ปัญหาที่พบบ่อยตอนตั้งแลบ

| อาการ | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|---|---|---|
| `ssh grp9@10.10.20.190` timeout | VPN หลุด, connector ไม่ใช่ System Bridge หรือ IP ชนกับเครื่องอื่น | ตรวจ VPN และ connector แล้วใช้ Console ในเว็บ CML แทนไปก่อน |
| ไม่มี `/etc/grp9-ready` | cloud-init ยังไม่เสร็จ | `sudo cloud-init status --wait` แล้วดู `/var/log/grp9-setup.log` |
| `SETUP FAILED` | ออกอินเทอร์เน็ตไม่ได้ | `curl -I https://pypi.org` → `sudo ip route replace default via 10.10.20.254 dev sbx0` → `sudo bash /usr/local/sbin/grp9-setup.sh` |
| `ip -br addr` ไม่มี `mgmt0` หรือ IP อยู่ผิดการ์ด | ลำดับ NIC ต่างจากที่คาด | แก้ MAC ใน `/etc/netplan/60-grp9.yaml` ให้ตรงกับการ์ดที่ต่อกับ SW-MGMT → `sudo netplan apply` |
| precheck: `Unable to connect to port 22` | router ยังไม่มี RSA key | บน router: `conf t` → `crypto key generate rsa modulus 2048` |
| `host key mismatch for 192.168.100.x` | router สร้าง RSA key ใหม่ แต่ control node ยังจำ key เก่า | `ssh-keygen -R 192.168.100.x` แล้วรันใหม่ |
| precheck: `Authentication failed` | ใส่ vault password ผิด หรือ user บน router ไม่ตรง | ใช้ vault `grp9lab` และตรวจด้วย `show run \| include username` |
| task Verify ค้างจน timeout | R2 ยังไม่ได้ตั้งค่า หรือ Gi0/1 ยัง shutdown | `ansible-playbook verify.yml -J` แล้วดูฝั่ง R2 |
| EEM ไม่ทำงาน | ยังไม่ได้ลงทะเบียน applet หรือ pattern ไม่ตรงกับ log จริง | `show event manager policy registered` และ `show logging \| include ADJCHG` แล้วเทียบกับ pattern |
| `history events` ขึ้น `abort` | action ค้างรอคำตอบ เช่น `redirect` ถามก่อนเขียนทับไฟล์เดิม (ดูด้วย debug) หรือ vty เต็ม | `debug event manager action cli` ดูว่าค้างที่ action ไหน → ลบไฟล์ก่อนด้วย `delete /force` (action 1.5) · `show users` / `clear line vty <n>` |
| `redirect flash0:` error | ชื่อ filesystem ต่างไป | ดูชื่อจริงด้วย `dir` (IOSv ใช้ `flash0:`) |
| ไม่เห็น log หรือ debug ในแท็บ SSH | ยังไม่ได้สั่ง `terminal monitor` | สั่ง `terminal monitor` บน router |

---

## 8. แก้ไฟล์แล้วสร้างแลบใหม่
แก้ไฟล์ใน `configs/` หรือ `ansible/` แล้วรัน:
```bash
python3 tools/build_lab.py
```
จากนั้น import `grp9-automation-lab.yaml` ใหม่เข้า CML (แลบเดิมให้ Stop → Wipe → Delete ก่อน)
ถ้าจะเปลี่ยนรหัส vault: `cd ansible && ansible-vault rekey group_vars/routers/vault.yml`
