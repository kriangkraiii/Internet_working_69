# Fault: IPsec Pre-Shared Key ไม่ตรงกัน (R2-BR1 <-> R1-HQ)

- Target: **R2-BR1**  Peer: **R1-HQ**
- อาการที่คาดไว้: IKE ค้าง MM_KEY_EXCH/MM_NO_STATE, peer log %CRYPTO-4-IKMP_BAD_MESSAGE, OSPF Tunnel12 down


## [01:48:37] Baseline verification

**Baseline**

```
R0-ISP: Interface GigabitEthernet0/0 = PASS
R0-ISP: Interface GigabitEthernet0/1 = PASS
R0-ISP: Interface GigabitEthernet0/2 = PASS
R0-ISP: NTP master (stratum 3) = PASS
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
```


## [01:49:14] INJECT fault

**R2-BR1# show clock**

```
01:49:04.642 ICT Thu Oct 15 2026
```

**R2-BR1# debug crypto isakmp**

```
Crypto ISAKMP debugging is on
```

**Injected config**

```
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R2-BR1(config)#no crypto isakmp key KKU-Capstone-PSK address 203.0.113.1
R2-BR1(config)#crypto isakmp key WRONG-KEY-2569 address 203.0.113.1
R2-BR1(config)#end
R2-BR1#
```

**R2-BR1# clear crypto session**

```
(no output)
```


## [01:50:27] DIAGNOSE: เก็บอาการ (show / syslog / debug)

**R2-BR1# show crypto isakmp sa**

```
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id status
203.0.113.1     203.0.113.5     MM_NO_STATE       1003 ACTIVE (deleted)
203.0.113.5     203.0.113.1     MM_NO_STATE       1004 ACTIVE (deleted)

IPv6 Crypto ISAKMP SA
```

**R2-BR1# show crypto session**

```
Crypto session current status

Interface: Tunnel12
Session status: DOWN-NEGOTIATING
Peer: 203.0.113.1 port 500 
  Session ID: 0  
  IKEv1 SA: local 203.0.113.5/500 remote 203.0.113.1/500 Inactive 
  Session ID: 0  
  IKEv1 SA: local 203.0.113.5/500 remote 203.0.113.1/500 Inactive 
  Session ID: 0  
  IKEv1 SA: local 203.0.113.5/500 remote 203.0.113.1/500 Inactive 
  IPSEC FLOW: permit 47 host 203.0.113.5 host 203.0.113.1 
        Active SAs: 0, origin: crypto map
```

**R2-BR1# show ip ospf neighbor**

```

```

**R2-BR1# show logging | include CRYPTO|ISAKMP|OSPF**

```
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):processing vendor id payload
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):vendor ID is DPD
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):processing vendor id payload
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):speaking to another IOS box!
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):received payload type 20
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):His hash no match - this node outside NAT
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):received payload type 20
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):No NAT Found for self or peer
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):Input = IKE_MESG_INTERNAL, IKE_PROCESS_MAIN_MODE
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):Old State = IKE_I_MM4  New State = IKE_I_MM4 
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):Send initial contact
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):SA is doing 
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):pre-shared key authentication using id type ID_IPV4_ADDR
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):ID payload 
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):	address      : 203.0.113.5
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):	protocol     : 17 
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):Total payload length: 12
Oct 15 01:50:18.155 ICT: ISAKMP-PAK: (1005):sending packet to 203.0.113.1 my_port 500 peer_port 500 (I) MM_KEY_EXCH
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):Sending an IKE IPv4 Packet.
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):Input = IKE_MESG_INTERNAL, IKE_PROCESS_COMPLETE
Oct 15 01:50:18.155 ICT: ISAKMP: (1005):Old State = IKE_I_MM4  New State = IKE_I_MM5 
Oct 15 01:50:19.148 ICT: ISAKMP-PAK: (1005):received packet from 203.0.113.1 dport 500 sport 500 Global (I) MM_KEY_EXCH
Oct 15 01:50:19.149 ICT: ISAKMP: (1005):phase 1 packet is a duplicate of a previous packet.
Oct 15 01:50:19.149 ICT: ISAKMP: (1005):retransmission skipped for phase 1 (time since last transmission 993)
Oct 15 01:50:19.561 ICT: ISAKMP-ERROR: (0):No peer struct to get peer description
```

**R1-HQ# show crypto isakmp sa**

```
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id status
203.0.113.1     203.0.113.5     MM_KEY_EXCH       1007 ACTIVE
203.0.113.1     203.0.113.5     MM_NO_STATE       1005 ACTIVE (deleted)
203.0.113.5     203.0.113.1     MM_KEY_EXCH       1008 ACTIVE
203.0.113.5     203.0.113.1     MM_NO_STATE       1006 ACTIVE (deleted)
203.0.113.1     203.0.113.9     QM_IDLE           1003 ACTIVE
203.0.113.9     203.0.113.1     QM_IDLE           1002 ACTIVE

IPv6 Crypto ISAKMP SA
```

**R1-HQ# show logging | include CRYPTO|OSPF**

```
.Oct 15 01:34:13.720 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
.Oct 15 01:34:18.992 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
.Oct 15 01:34:18.993 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from FULL to DOWN, Neighbor Down: Interface down or detached
.Oct 15 01:34:19.548 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
.Oct 15 01:34:20.566 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from LOADING to FULL, Loading Done
.Oct 15 01:34:25.227 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
.Oct 15 01:34:25.227 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from FULL to DOWN, Neighbor Down: Interface down or detached
.Oct 15 01:34:26.204 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
.Oct 15 01:34:27.113 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from LOADING to FULL, Loading Done
.Oct 15 01:41:33.262 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
.Oct 15 01:41:33.760 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from LOADING to FULL, Loading Done
.Oct 15 01:41:38.891 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
.Oct 15 01:41:38.891 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from LOADING to FULL, Loading Done
.Oct 15 01:41:43.467 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
.Oct 15 01:41:43.467 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from FULL to DOWN, Neighbor Down: Interface down or detached
.Oct 15 01:41:44.493 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
.Oct 15 01:41:44.990 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from LOADING to FULL, Loading Done
Oct 15 01:41:50.544 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:41:50.544 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:41:51.566 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 01:41:52.076 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 3.3.3.3 on Tunnel13 from LOADING to FULL, Loading Done
Oct 15 01:49:14.322 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:49:14.322 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:49:15.233 ICT: %CRYPTO-4-IKMP_BAD_MESSAGE: IKE message from 203.0.113.5 failed its sanity check or is malformed
Oct 15 01:50:16.029 ICT: %CRYPTO-4-IKMP_BAD_MESSAGE: IKE message from 203.0.113.5 failed its sanity check or is malformed
```


## [01:51:17] RECOVER (targeted fix)

**Recovery config (via ssh)**

```
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R2-BR1(config)#no crypto isakmp key WRONG-KEY-2569 address 203.0.113.1
R2-BR1(config)#crypto isakmp key KKU-Capstone-PSK address 203.0.113.1
R2-BR1(config)#end
R2-BR1#
```

**R2-BR1# clear crypto session**

```
(no output)
```


## [01:52:21] POST-RECOVERY verification

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
