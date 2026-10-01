# ค่าที่ต้องตั้งผ่าน GUI ใน Packet Tracer

เครื่อง PC และ Server ใน Packet Tracer ตั้งค่าผ่านหน้าต่าง GUI เท่านั้น ใช้ค่าในตารางนี้ (ค่า IPv4 ในแลบตั้งไว้แล้ว ไม่ต้องแก้)

## 1. IPv6 ของ end device
เปิดเครื่อง → **Desktop → IP Configuration** → ส่วน IPv6 เลือก **Static**

| อุปกรณ์ | IPv6 Address / Prefix | IPv6 Gateway |
|---|---|---|
| PC-A | `2001:db8:acad:1::3` / 64 | `fe80::1` |
| PC-B | `2001:db8:acad:2::3` / 64 | `fe80::2` |
| TACACS+ Server | `2001:db8:acad:2::2` / 64 | `fe80::2` |
| PC-C | `2001:db8:acad:3::3` / 64 | `fe80::3` |
| RADIUS Server | `2001:db8:acad:3::2` / 64 | `fe80::3` |

> gateway ใช้ link-local ของ router (fe80::1/2/3) เพราะเป็นค่าคงที่และไม่เปลี่ยนแม้จะเปลี่ยน prefix global

## 2. ผู้ใช้ที่มีเฉพาะบนเซิร์ฟเวอร์ (ใช้พิสูจน์ว่าเซิร์ฟเวอร์ตอบจริง)
เปิดเซิร์ฟเวอร์ → **Services → AAA** → ส่วน **User Setup** → กรอก Username/Password → **Add**

| เซิร์ฟเวอร์ | Username | Password | หมายเหตุ |
|---|---|---|---|
| TACACS+ Server | `netops2` | `netops2pa55` | ไม่มีใน local database ของ R2 |
| RADIUS Server | `netops3` | `netops3pa55` | ไม่มีใน local database ของ R3 |

ทำไมต้องมี: `Admin2`/`Admin3` มีอยู่ทั้งบนเซิร์ฟเวอร์และใน local database ของ router ถ้าเซิร์ฟเวอร์ล่ม ผู้ใช้สองคนนี้ยัง login ได้ผ่าน fallback `local` จึงบอกไม่ได้ว่าใครเป็นผู้ตรวจสอบสิทธิ์ ส่วน `netops2`/`netops3` login ได้**ก็ต่อเมื่อเซิร์ฟเวอร์ตอบเท่านั้น**

## 3. ค่าที่แลบตั้งไว้แล้ว (ตรวจให้ตรงก่อนเดโม)
| เซิร์ฟเวอร์ | Network Configuration (Client) | Secret | Server Type | User เดิม |
|---|---|---|---|---|
| TACACS+ Server | R2 – `192.168.2.1` | `tacacspa55` | TACACS | `Admin2` / `admin2pa55` |
| RADIUS Server | R3 – `192.168.3.1` | `radiuspa55` | Radius | `Admin3` / `admin3pa55` |

ส่วน **Service** ด้านบนของหน้า AAA ต้องเป็น **On**
