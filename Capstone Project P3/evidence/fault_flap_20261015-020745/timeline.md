# Fault: Link Flapping บน WAN ของ R2-BR1 (Gi0/0)

- Target: **R2-BR1**  Peer: **R1-HQ**
- อาการที่คาดไว้: %LINK-5-CHANGED/%LINEPROTO-5-UPDOWN ซ้ำๆ, %OSPF-5-ADJCHG FULL->DOWN, route 10.2.10.0/24 หายจาก R1


## [02:07:45] Baseline verification

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


## [02:08:29] INJECT fault

**R2-BR1# show clock**

```
02:08:18.414 ICT Thu Oct 15 2026
```


## [02:08:46] flap 1/3: GigabitEthernet0/0 shutdown


## [02:08:59] flap 1/3: GigabitEthernet0/0 no shutdown


## [02:09:16] flap 2/3: GigabitEthernet0/0 shutdown


## [02:09:29] flap 2/3: GigabitEthernet0/0 no shutdown


## [02:09:46] flap 3/3: GigabitEthernet0/0 shutdown


## [02:10:02] flap 3/3: GigabitEthernet0/0 no shutdown


## [02:10:20] DIAGNOSE: เก็บอาการ (show / syslog / debug)

**R2-BR1# show ip ospf neighbor**

```
Neighbor ID     Pri   State           Dead Time   Address         Interface
1.1.1.1           0   FULL/  -        00:00:17    172.16.12.1     Tunnel12
```

**R2-BR1# show crypto isakmp sa**

```
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id status
203.0.113.5     203.0.113.1     QM_IDLE           1012 ACTIVE

IPv6 Crypto ISAKMP SA
```

**R2-BR1# show interfaces GigabitEthernet0/0 | include line protocol|resets|carrier**

```
GigabitEthernet0/0 is up, line protocol is up 
     0 output errors, 0 collisions, 5 interface resets
     2 lost carrier, 0 no carrier, 0 pause output
```

**R2-BR1# show logging | include LINK|LINEPROTO|OSPF|CRYPTO**

```
Oct 15 02:08:37.478 ICT: %LINK-3-UPDOWN: Interface GigabitEthernet0/0, changed state to up
Oct 15 02:08:38.479 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to up
Oct 15 02:08:41.843 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel12, changed state to up
Oct 15 02:08:46.713 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:08:52.429 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:08:52.913 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel12, changed state to down
Oct 15 02:08:52.913 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:08:52.913 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:08:54.483 ICT: %LINK-5-CHANGED: Interface GigabitEthernet0/0, changed state to administratively down
Oct 15 02:08:55.483 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to down
Oct 15 02:09:07.779 ICT: %LINK-3-UPDOWN: Interface GigabitEthernet0/0, changed state to up
Oct 15 02:09:08.780 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to up
Oct 15 02:09:12.924 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel12, changed state to up
Oct 15 02:09:12.965 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:09:13.942 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:09:22.929 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel12, changed state to down
Oct 15 02:09:22.929 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:09:22.929 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 02:09:24.572 ICT: %LINK-5-CHANGED: Interface GigabitEthernet0/0, changed state to administratively down
Oct 15 02:09:25.572 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to down
Oct 15 02:09:39.502 ICT: %LINK-3-UPDOWN: Interface GigabitEthernet0/0, changed state to up
Oct 15 02:09:40.503 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to up
Oct 15 02:09:42.945 ICT: %LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel12, changed state to up
Oct 15 02:09:42.985 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 02:09:43.965 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 1.1.1.1 on Tunnel12 from LOADING to FULL, Loading Done
```

**R1-HQ# show logging | include OSPF|CRYPTO**

```
Oct 15 01:54:48.054 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:54:48.953 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 01:54:49.958 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 01:56:45.778 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:56:45.779 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
Oct 15 01:56:46.827 ICT: %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 01:56:47.830 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from LOADING to FULL, Loading Done
Oct 15 01:59:34.336 ICT: %OSPFv3-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Tunnel12 from FULL to DOWN, Neighbor Down: Interface down or detached
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
```

**R1-HQ# show ip route ospf**

```
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is 203.0.113.2 to network 0.0.0.0

      10.0.0.0/8 is variably subnetted, 10 subnets, 3 masks
O        10.0.0.2/32 [110/1001] via 172.16.12.2, 00:01:40, Tunnel12
O        10.0.0.3/32 [110/1001] via 172.16.13.2, 00:36:04, Tunnel13
O        10.2.10.0/24 [110/1001] via 172.16.12.2, 00:01:40, Tunnel12
O        10.3.10.0/24 [110/1001] via 172.16.13.2, 00:36:04, Tunnel13
```


## [02:10:57] RECOVER (targeted fix)

**Recovery config (via ssh)**

```
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R2-BR1(config)#interface GigabitEthernet0/0
R2-BR1(config-if)#no shutdown
R2-BR1(config-if)#end
R2-BR1#
```


## [02:12:00] POST-RECOVERY verification

**Post-recovery**

```
R0-ISP: Interface GigabitEthernet0/0 = PASS
R0-ISP: Interface GigabitEthernet0/1 = PASS
R0-ISP: Interface GigabitEthernet0/2 = PASS
R0-ISP: NTP master (stratum 3) = PASS
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
FAIL = 0
```
