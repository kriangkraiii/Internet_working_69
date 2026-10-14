# Fault: ACL บน VTY drop ทราฟฟิก Management (R3-DC ถูกล็อก SSH)

- Target: **R3-DC**  Peer: **R1-HQ**
- อาการที่คาดไว้: SSH จาก automation host ถูกปฏิเสธ, %SEC-6-IPACCESSLOGS ... denied <devbox>, Data plane ยังปกติ


## [02:14:28] Baseline verification

**Baseline**

```
R0-ISP: Interface GigabitEthernet0/0 = PASS
R0-ISP: Interface GigabitEthernet0/1 = PASS
R0-ISP: Interface GigabitEthernet0/2 = PASS
R0-ISP: NTP master (stratum 3) = PASS
R3-DC: Interface GigabitEthernet0/0 = PASS
R3-DC: Interface GigabitEthernet0/1 = PASS
R3-DC: Interface Tunnel13 = PASS
R3-DC: OSPFv2 neighbors FULL = PASS
R3-DC: OSPFv3 neighbors FULL = PASS
R3-DC: IKE SA (QM_IDLE) = PASS
R3-DC: IPsec ESP encaps counter = PASS
R3-DC: Ping v4 -> R1-HQ Lo0 = PASS
R3-DC: Ping v6 -> R1-HQ Lo0 = PASS
R3-DC: Ping v4 -> R2-BR1 Lo0 = PASS
R3-DC: Ping v6 -> R2-BR1 Lo0 = PASS
R2-BR1: Interface GigabitEthernet0/0 = PASS
R2-BR1: Interface GigabitEthernet0/1 = PASS
R2-BR1: Interface Tunnel12 = PASS
R2-BR1: OSPFv2 neighbors FULL = PASS
R2-BR1: OSPFv3 neighbors FULL = PASS
R2-BR1: IKE SA (QM_IDLE) = PASS
R2-BR1: IPsec ESP encaps counter = PASS
R2-BR1: Ping v4 -> R1-HQ Lo0 = PASS
R2-BR1: Ping v6 -> R1-HQ Lo0 = PASS
R2-BR1: Ping v4 -> R3-DC Lo0 = PASS
R2-BR1: Ping v6 -> R3-DC Lo0 = PASS
R1-HQ: Interface GigabitEthernet0/0 = PASS
R1-HQ: Interface GigabitEthernet0/1 = PASS
R1-HQ: Interface Tunnel12 = PASS
R1-HQ: Interface Tunnel13 = PASS
R1-HQ: OSPFv2 neighbors FULL = PASS
R1-HQ: OSPFv3 neighbors FULL = PASS
R1-HQ: IKE SA (QM_IDLE) = PASS
R1-HQ: IPsec ESP encaps counter = PASS
R1-HQ: Ping v4 -> R2-BR1 Lo0 = PASS
R1-HQ: Ping v6 -> R2-BR1 Lo0 = PASS
R1-HQ: Ping v4 -> R3-DC Lo0 = PASS
R1-HQ: Ping v6 -> R3-DC Lo0 = PASS
```


## [02:15:03] INJECT fault

**R3-DC# show clock**

```
02:14:51.912 ICT Thu Oct 15 2026
```

**Injected config**

```
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R3-DC(config)#ip access-list standard ACL-VTY-LOCKOUT
R3-DC(config-std-nacl)#permit host 10.10.20.181
R3-DC(config-std-nacl)#deny any log
R3-DC(config-std-nacl)#line vty 0 4
R3-DC(config-line)#access-class ACL-VTY-LOCKOUT in
R3-DC(config-line)#end
R3-DC#
```


## [02:15:28] DIAGNOSE: เก็บอาการ (show / syslog / debug)

**SSH probe จาก automation host**

```
NetmikoTimeoutException: TCP connection to device failed.
```

**R3-DC# show running-config | section line vty**

```
line vty 0 4
 access-class ACL-VTY-LOCKOUT in
 logging synchronous
 transport input ssh
```

**R3-DC# show ip access-lists ACL-VTY-LOCKOUT**

```
Standard IP access list ACL-VTY-LOCKOUT
    10 permit 10.10.20.181
    20 deny   any log (1 match)
```

**R3-DC# show logging | include SEC|ACCESS|SSH**

```
.Oct 15 01:41:18.712 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:crypto ipsec profile IPSEC-PROFILE

.Oct 15 01:41:31.761 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:tunnel protection ipsec profile IPSEC-PROFILE
.Oct 15 01:41:56.924 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:ip access-list extended CoPP-IPSEC
.Oct 15 01:42:09.858 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:class-map match-all CM-COPP-IPSEC
.Oct 15 01:42:10.873 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:match access-group name CoPP-IPSEC
.Oct 15 01:42:18.079 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:class CM-COPP-IPSEC
Oct 15 01:43:30.987 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 01:43:30 ICT Thu Oct 15 2026
Oct 15 01:46:25.934 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 01:46:25 ICT Thu Oct 15 2026
Oct 15 01:47:55.813 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 01:47:55 ICT Thu Oct 15 2026
Oct 15 01:48:21.713 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 01:48:21 ICT Thu Oct 15 2026
Oct 15 01:52:06.286 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 01:52:06 ICT Thu Oct 15 2026
Oct 15 02:01:14.464 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:01:14 ICT Thu Oct 15 2026
Oct 15 02:04:33.867 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:04:33 ICT Thu Oct 15 2026
Oct 15 02:05:08.194 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:05:08 ICT Thu Oct 15 2026
Oct 15 02:05:45.480 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:05:45 ICT Thu Oct 15 2026
Oct 15 02:06:07.508 ICT: %SEC-6-IPACCESSLOGNP: list ACL-VTY-LOCKOUT denied 0 192.168.254.11 -> 0.0.0.0, 1 packet  
Oct 15 02:06:20.502 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: UNKNOWN] [localport: 0] at 02:06:20 ICT Thu Oct 15 2026
Oct 15 02:07:09.385 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: UNKNOWN] [localport: 0] at 02:07:09 ICT Thu Oct 15 2026
Oct 15 02:07:20.405 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:access-class ACL-MGMT-SSH in 
Oct 15 02:07:30.168 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:07:30 ICT Thu Oct 15 2026
Oct 15 02:11:44.537 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:11:44 ICT Thu Oct 15 2026
Oct 15 02:13:49.379 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:13:49 ICT Thu Oct 15 2026
Oct 15 02:14:12.379 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:14:12 ICT Thu Oct 15 2026
Oct 15 02:14:46.602 ICT: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 192.168.254.11] [localport: 22] at 02:14:46 ICT Thu Oct 15 2026
```

**R1-HQ# show ip ospf neighbor**

```
Neighbor ID     Pri   State           Dead Time   Address         Interface
3.3.3.3           0   FULL/  -        00:00:15    172.16.13.2     Tunnel13
2.2.2.2           0   FULL/  -        00:00:18    172.16.12.2     Tunnel12
```


## [02:16:09] RECOVER (targeted fix)

**Recovery config (via console)**

```
configure terminal
R3-DC(config)#line vty 0 4
R3-DC(config-line)#access-class ACL-MGMT-SSH in
R3-DC(config-line)#exit
R3-DC(config)#
Oct 15 02:16:10.002 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:line vty 0 4
Oct 15 02:16:10.518 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:access-class ACL-MGMT-SSH in 
R3-DC(config)#no ip access-list standard ACL-VTY-LOCKOUT
Oct 15 02:16:11.056 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:exit 
Oct 15 02:16:11.598 ICT: %PARSER-5-CFGLOG_LOGGEDCMD: User:admin  logged command:no ip access-list standard ACL-VTY-LOCKOUT
R3-DC(config)#
R3-DC(config)#end
R3-DC#
```


## [02:16:54] POST-RECOVERY verification

**Post-recovery**

```
R0-ISP: Interface GigabitEthernet0/0 = PASS
R0-ISP: Interface GigabitEthernet0/1 = PASS
R0-ISP: Interface GigabitEthernet0/2 = PASS
R0-ISP: NTP master (stratum 3) = PASS
R3-DC: Interface GigabitEthernet0/0 = PASS
R3-DC: Interface GigabitEthernet0/1 = PASS
R3-DC: Interface Tunnel13 = PASS
R3-DC: OSPFv2 neighbors FULL = PASS
R3-DC: OSPFv3 neighbors FULL = PASS
R3-DC: IKE SA (QM_IDLE) = PASS
R3-DC: IPsec ESP encaps counter = PASS
R3-DC: Ping v4 -> R1-HQ Lo0 = PASS
R3-DC: Ping v6 -> R1-HQ Lo0 = PASS
R3-DC: Ping v4 -> R2-BR1 Lo0 = PASS
R3-DC: Ping v6 -> R2-BR1 Lo0 = PASS
R1-HQ: Interface GigabitEthernet0/0 = PASS
R1-HQ: Interface GigabitEthernet0/1 = PASS
R1-HQ: Interface Tunnel12 = PASS
R1-HQ: Interface Tunnel13 = PASS
R1-HQ: OSPFv2 neighbors FULL = PASS
R1-HQ: OSPFv3 neighbors FULL = PASS
R1-HQ: IKE SA (QM_IDLE) = PASS
R1-HQ: IPsec ESP encaps counter = PASS
R1-HQ: Ping v4 -> R2-BR1 Lo0 = PASS
R1-HQ: Ping v6 -> R2-BR1 Lo0 = PASS
R1-HQ: Ping v4 -> R3-DC Lo0 = PASS
R1-HQ: Ping v6 -> R3-DC Lo0 = PASS
R2-BR1: Interface GigabitEthernet0/0 = PASS
R2-BR1: Interface GigabitEthernet0/1 = PASS
R2-BR1: Interface Tunnel12 = PASS
R2-BR1: OSPFv2 neighbors FULL = PASS
R2-BR1: OSPFv3 neighbors FULL = PASS
R2-BR1: IKE SA (QM_IDLE) = PASS
R2-BR1: IPsec ESP encaps counter = PASS
R2-BR1: Ping v4 -> R1-HQ Lo0 = PASS
R2-BR1: Ping v6 -> R1-HQ Lo0 = PASS
R2-BR1: Ping v4 -> R3-DC Lo0 = PASS
R2-BR1: Ping v6 -> R3-DC Lo0 = PASS
FAIL = 0
```
