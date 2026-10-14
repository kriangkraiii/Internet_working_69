# Fault: OSPF MTU mismatch บน Tunnel12 (R2-BR1)

- Target: **R2-BR1**  Peer: **R1-HQ**
- อาการที่คาดไว้: neighbor ค้างที่ EXSTART/EXCHANGE, debug: 'Nbr 1.1.1.1 has larger interface MTU'


## [02:01:26] Baseline verification

**Baseline**

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
```


## [02:02:04] INJECT fault

**R2-BR1# show clock**

```
02:01:56.343 ICT Thu Oct 15 2026
```

**R2-BR1# debug ip ospf adj**

```
OSPF adjacency debugging is on
```

**Injected config**

```
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R2-BR1(config)#interface Tunnel12
R2-BR1(config-if)#ip mtu 1300
R2-BR1(config-if)#shutdown
R2-BR1(config-if)#no shutdown
R2-BR1(config-if)#end
R2-BR1#
```


## [02:03:00] DIAGNOSE: เก็บอาการ (show / syslog / debug)

**R2-BR1# show ip ospf neighbor**

```
Neighbor ID     Pri   State           Dead Time   Address         Interface
1.1.1.1           0   EXSTART/  -     00:00:17    172.16.12.1     Tunnel12
```

**R2-BR1# show ip interface Tunnel12 | include MTU**

```
MTU is 1300 bytes
```

**R2-BR1# show logging | include OSPF|MTU**

```
Oct 15 02:02:31.251 ICT: OSPF-1 ADJ   Tu12: Nbr 1.1.1.1 has larger interface MTU
Oct 15 02:02:36.216 ICT: OSPF-1 ADJ   Tu12: Send DBD to 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x7 len 32
Oct 15 02:02:36.216 ICT: OSPF-1 ADJ   Tu12: Retransmitting DBD to 1.1.1.1 [7]
Oct 15 02:02:36.220 ICT: OSPF-1 ADJ   Tu12: Rcv DBD from 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x2 len 92  mtu 1400 state EXSTART
Oct 15 02:02:36.220 ICT: OSPF-1 ADJ   Tu12: Nbr 1.1.1.1 has larger interface MTU
Oct 15 02:02:40.932 ICT: OSPF-1 ADJ   Tu12: Send DBD to 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x7 len 32
Oct 15 02:02:40.932 ICT: OSPF-1 ADJ   Tu12: Retransmitting DBD to 1.1.1.1 [8]
Oct 15 02:02:40.936 ICT: OSPF-1 ADJ   Tu12: Rcv DBD from 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x2 len 92  mtu 1400 state EXSTART
Oct 15 02:02:40.936 ICT: OSPF-1 ADJ   Tu12: Nbr 1.1.1.1 has larger interface MTU
Oct 15 02:02:45.702 ICT: OSPF-1 ADJ   Tu12: Send DBD to 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x7 len 32
Oct 15 02:02:45.702 ICT: OSPF-1 ADJ   Tu12: Retransmitting DBD to 1.1.1.1 [9]
Oct 15 02:02:45.709 ICT: OSPF-1 ADJ   Tu12: Rcv DBD from 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x2 len 92  mtu 1400 state EXSTART
Oct 15 02:02:45.709 ICT: OSPF-1 ADJ   Tu12: Nbr 1.1.1.1 has larger interface MTU
Oct 15 02:02:50.569 ICT: OSPF-1 ADJ   Tu12: Send DBD to 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x7 len 32
Oct 15 02:02:50.569 ICT: OSPF-1 ADJ   Tu12: Retransmitting DBD to 1.1.1.1 [10]
Oct 15 02:02:50.573 ICT: OSPF-1 ADJ   Tu12: Rcv DBD from 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x2 len 92  mtu 1400 state EXSTART
Oct 15 02:02:50.573 ICT: OSPF-1 ADJ   Tu12: Nbr 1.1.1.1 has larger interface MTU
Oct 15 02:02:55.338 ICT: OSPF-1 ADJ   Tu12: Send DBD to 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x7 len 32
Oct 15 02:02:55.338 ICT: OSPF-1 ADJ   Tu12: Retransmitting DBD to 1.1.1.1 [11]
Oct 15 02:02:55.341 ICT: OSPF-1 ADJ   Tu12: Rcv DBD from 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x2 len 92  mtu 1400 state EXSTART
Oct 15 02:02:55.341 ICT: OSPF-1 ADJ   Tu12: Nbr 1.1.1.1 has larger interface MTU
Oct 15 02:03:00.303 ICT: OSPF-1 ADJ   Tu12: Send DBD to 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x7 len 32
Oct 15 02:03:00.303 ICT: OSPF-1 ADJ   Tu12: Retransmitting DBD to 1.1.1.1 [12]
Oct 15 02:03:00.307 ICT: OSPF-1 ADJ   Tu12: Rcv DBD from 1.1.1.1 seq 0xEB7 opt 0x52 flag 0x2 len 92  mtu 1400 state EXSTART
Oct 15 02:03:00.307 ICT: OSPF-1 ADJ   Tu12: Nbr 1.1.1.1 has larger interface MTU
```

**R1-HQ# show ip ospf neighbor**

```
Neighbor ID     Pri   State           Dead Time   Address         Interface
3.3.3.3           0   FULL/  -        00:00:17    172.16.13.2     Tunnel13
2.2.2.2           0   EXCHANGE/  -    00:00:17    172.16.12.2     Tunnel12
```

**R1-HQ# show ip interface Tunnel12 | include MTU**

```
MTU is 1400 bytes
```


## [02:03:55] RECOVER (targeted fix)

**Recovery config (via ssh)**

```
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R2-BR1(config)#interface Tunnel12
R2-BR1(config-if)#ip mtu 1400
R2-BR1(config-if)#end
R2-BR1#
```


## [02:04:46] POST-RECOVERY verification

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
