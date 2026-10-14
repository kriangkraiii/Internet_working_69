# Fault: IPsec Pre-Shared Key ไม่ตรงกัน (R2-BR1 <-> R1-HQ)

- Target: **R2-BR1**  Peer: **R1-HQ**
- อาการที่คาดไว้: IKE ค้าง MM_KEY_EXCH/MM_NO_STATE, peer log %CRYPTO-4-IKMP_BAD_MESSAGE, OSPF Tunnel12 down


## [02:48:46] Baseline verification

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


## [02:49:17] INJECT fault

**R2-BR1# show clock**

```
02:49:04.434 ICT Thu Oct 15 2026
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


## [02:50:28] DIAGNOSE: เก็บอาการ (show / syslog / debug)

**R2-BR1# show crypto isakmp sa**

```
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id status
203.0.113.1     203.0.113.5     MM_NO_STATE       1013 ACTIVE (deleted)
203.0.113.5     203.0.113.1     MM_KEY_EXCH       1014 ACTIVE
203.0.113.5     203.0.113.1     MM_NO_STATE       1012 ACTIVE (deleted)

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
  IPSEC FLOW: permit 47 host 203.0.113.5 host 203.0.113.1 
        Active SAs: 0, origin: crypto map

Interface: GigabitEthernet0/0
Session status: DOWN-NEGOTIATING
Peer: 203.0.113.1 port 500 
  Session ID: 0  
  IKEv1 SA: local 203.0.113.5/500 remote 203.0.113.1/500 Inactive
```

**R2-BR1# show ip ospf neighbor**

```

```

**R2-BR1# show logging | include CRYPTO|ISAKMP|OSPF**

```
Oct 15 02:50:17.170 ICT: ISAKMP: (1015):speaking to another IOS box!
Oct 15 02:50:17.170 ICT: ISAKMP: (1015):received payload type 20
Oct 15 02:50:17.170 ICT: ISAKMP: (1015):His hash no match - this node outside NAT
Oct 15 02:50:17.170 ICT: ISAKMP: (1015):received payload type 20
Oct 15 02:50:17.170 ICT: ISAKMP: (1015):No NAT Found for self or peer
Oct 15 02:50:17.171 ICT: ISAKMP: (1015):Input = IKE_MESG_INTERNAL, IKE_PROCESS_MAIN_MODE
Oct 15 02:50:17.171 ICT: ISAKMP: (1015):Old State = IKE_I_MM4  New State = IKE_I_MM4 
Oct 15 02:50:17.172 ICT: ISAKMP: (1015):SA is doing 
Oct 15 02:50:17.172 ICT: ISAKMP: (1015):pre-shared key authentication using id type ID_IPV4_ADDR
Oct 15 02:50:17.172 ICT: ISAKMP: (1015):ID payload 
Oct 15 02:50:17.172 ICT: ISAKMP: (1015):	address      : 203.0.113.5
Oct 15 02:50:17.172 ICT: ISAKMP: (1015):	protocol     : 17 
Oct 15 02:50:17.173 ICT: ISAKMP: (1015):Total payload length: 12
Oct 15 02:50:17.173 ICT: ISAKMP-PAK: (1015):sending packet to 203.0.113.1 my_port 500 peer_port 500 (I) MM_KEY_EXCH
Oct 15 02:50:17.173 ICT: ISAKMP: (1015):Sending an IKE IPv4 Packet.
Oct 15 02:50:17.174 ICT: ISAKMP: (1015):Input = IKE_MESG_INTERNAL, IKE_PROCESS_COMPLETE
Oct 15 02:50:17.174 ICT: ISAKMP: (1015):Old State = IKE_I_MM4  New State = IKE_I_MM5 
Oct 15 02:50:18.176 ICT: ISAKMP-PAK: (1015):received packet from 203.0.113.1 dport 500 sport 500 Global (I) MM_KEY_EXCH
Oct 15 02:50:18.177 ICT: ISAKMP: (1015):phase 1 packet is a duplicate of a previous packet.
Oct 15 02:50:18.177 ICT: ISAKMP: (1015):retransmitting due to retransmit phase 1
Oct 15 02:50:18.678 ICT: ISAKMP: (1015):retransmitting phase 1 MM_KEY_EXCH...
Oct 15 02:50:18.678 ICT: ISAKMP: (1015):: incrementing error counter on sa, attempt 1 of 5: retransmit phase 1
Oct 15 02:50:18.678 ICT: ISAKMP: (1015):retransmitting phase 1 MM_KEY_EXCH
Oct 15 02:50:18.678 ICT: ISAKMP-PAK: (1015):sending packet to 203.0.113.1 my_port 500 peer_port 500 (I) MM_KEY_EXCH
Oct 15 02:50:18.678 ICT: ISAKMP: (1015):Sending an IKE IPv4 Packet.
```

**R1-HQ# show crypto isakmp sa**

```
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id status
203.0.113.1     203.0.113.5     MM_KEY_EXCH       1017 ACTIVE
203.0.113.1     203.0.113.5     MM_NO_STATE       1015 ACTIVE (deleted)
203.0.113.5     203.0.113.1     MM_KEY_EXCH       1016 ACTIVE
203.0.113.1     203.0.113.9     QM_IDLE           1003 ACTIVE
203.0.113.9     203.0.113.1     QM_IDLE           1002 ACTIVE

IPv6 Crypto ISAKMP SA
```

**R1-HQ# show logging | include CRYPTO|OSPF**

```
Oct 15 01:59:34.337 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:59:35.150 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 01:59:36.141 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:02:02.266 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:02:02.267 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:02:03.801 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:03:53.279 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:08:37.827 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:08:37.828 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:08:47.211 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:08:52.932 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:09:12.022 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Dead timer expired
Oct 15 02:09:13.637 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:09:14.619 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:09:42.854 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Dead timer expired
Oct 15 02:09:43.815 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:09:44.806 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:39:29.210 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:39:34.285 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:44:58.949 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:45:03.600 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:49:16.310 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:49:16.310 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:49:17.284 ICT: %CRYPTO-4-IKMP_BAD_MESSAGE: IKE message from 203.0.113.5 failed its sanity check or is malformed
Oct 15 02:50:17.876 ICT: %CRYPTO-4-IKMP_BAD_MESSAGE: IKE message from 203.0.113.5 failed its sanity check or is malformed
```


## [02:51:13] RECOVER (targeted fix)

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


## [02:52:16] POST-RECOVERY verification

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
