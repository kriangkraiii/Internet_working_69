วางภาพหน้าจอตามชื่อไฟล์ด้านล่าง แล้วเปิด report/report.html ใน Chrome > Print > Save as PDF
(ภาพจะแทนกรอบ "แทรกภาพ" ให้อัตโนมัติ)

fig-02-lab2813.png         ผลรัน lab_28_1_3.py (Part 1-4)
fig-03-wireshark-ike.png   Wireshark ISAKMP Main/Quick Mode
fig-04-wireshark-ssh.png   TCP 3-way handshake ของ Netmiko SSH
fig-05-verify.png          verify.py สรุป FAIL 0
fig-06-ospf-ipsec.png      show ip ospf neighbor + show crypto isakmp sa (R1-HQ)
fig-07-netflow.png         show flow monitor FNF-MONITOR cache
fig-08-collector.png       collector.py รับ Syslog + NetFlow
fig-09-inc01-symptom.png   INC-01 MM_KEY_EXCH + IKMP_BAD_MESSAGE
fig-10-inc01-fixed.png     INC-01 QM_IDLE + OSPF FULL หลังแก้
fig-11-inc02-symptom.png   INC-02 EXSTART + debug "larger interface MTU"
fig-12-inc02-fixed.png     INC-02 neighbor FULL หลังแก้
fig-13-inc03.png           INC-03 SSH ถูกปฏิเสธ + กู้ผ่าน console
fig-14-inc04.png           INC-04 Syslog LINK/OSPF บน collector
