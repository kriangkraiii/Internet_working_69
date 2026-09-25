#!/usr/bin/env python3
"""Build the CML lab file (grp9-automation-lab.yaml) from the files in demo-lab/.

Run after editing any config or playbook:  python3 tools/build_lab.py
Only the Python standard library is needed.
"""
from pathlib import Path

# --- settings you may need to change -------------------------------------------------
# Static address for the control node on the DevNet sandbox network (reachable over VPN).
# Pick a free address: ping it from the sandbox devbox first; it must not reply.
SBX_IP = "10.10.20.190/24"
SBX_GW = "10.10.20.254"
USER, USER_PW = "grp9", "Grp9@lab"
# ---------------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
ANSIBLE_FILES = [
    "ansible.cfg", "inventory.yml", "site.yml", "precheck.yml", "verify.yml", "reset.yml",
    "requirements.yml", "group_vars/routers/vars.yml", "group_vars/routers/vault.yml",
]
CONFIG_FILES = ["R1-day0.cfg", "R2-day0.cfg", "R1-eem.cfg"]

NET_SCRIPT = r"""#!/bin/bash
# Give the three NICs stable names by PCI order:
#   slot 0 -> mgmt0 (SW-MGMT, 192.168.100.10)
#   slot 1 -> sbx0  (DevNet sandbox bridge, reachable from the VPN)
#   slot 2 -> inet0 (CML NAT, internet for apt/pip)
set -euo pipefail
mapfile -t NICS < <(
  for d in /sys/class/net/*; do
    [ -e "$d/device" ] || continue
    pci=$(readlink -f "$d/device" | grep -oE '[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f]' | tail -1)
    echo "$pci $(basename "$d")"
  done | sort | awk '{print $2}')
mac() { cat "/sys/class/net/$1/address"; }
{
  echo "network:"
  echo "  version: 2"
  echo "  ethernets:"
  echo "    mgmt0:"
  echo "      match: {macaddress: \"$(mac "${NICS[0]}")\"}"
  echo "      set-name: mgmt0"
  echo "      addresses: [192.168.100.10/24]"
  if [ -n "${NICS[1]:-}" ]; then
    echo "    sbx0:"
    echo "      match: {macaddress: \"$(mac "${NICS[1]}")\"}"
    echo "      set-name: sbx0"
    echo "      addresses: [__SBX_IP__]"
    echo "      nameservers: {addresses: [8.8.8.8, 1.1.1.1]}"
    echo "      routes:"
    echo "        - {to: 10.0.0.0/8, via: __SBX_GW__}"
    echo "        - {to: 172.16.0.0/12, via: __SBX_GW__}"
    echo "        - {to: 192.168.0.0/16, via: __SBX_GW__}"
  fi
  if [ -n "${NICS[2]:-}" ]; then
    echo "    inet0:"
    echo "      match: {macaddress: \"$(mac "${NICS[2]}")\"}"
    echo "      set-name: inet0"
    echo "      dhcp4: true"
  fi
} > /etc/netplan/60-grp9.yaml
chmod 600 /etc/netplan/60-grp9.yaml
rm -f /etc/netplan/50-cloud-init.yaml
netplan apply
"""

SETUP_SCRIPT = r"""#!/bin/bash
# One-time setup of the Ansible control node (runs from cloud-init).
exec > >(tee -a /var/log/grp9-setup.log) 2>&1
set -x
/usr/local/sbin/grp9-net.sh
systemctl restart rsyslog

# Wait for internet via NAT; fall back to the sandbox gateway.
for i in $(seq 1 30); do curl -s -m 5 -o /dev/null https://pypi.org && break; sleep 2; done
if ! curl -s -m 5 -o /dev/null https://pypi.org; then
  ip route replace default via __SBX_GW__ dev sbx0 || true
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv python3-pip netcat-openbsd tcpdump
python3 -m venv /opt/ansible
/opt/ansible/bin/pip install --upgrade pip
/opt/ansible/bin/pip install ansible-core "paramiko<5"
echo 'export PATH=/opt/ansible/bin:$PATH' > /etc/profile.d/ansible.sh
# the image may ship its own /usr/bin/ansible; make sure the venv wins in every shell
echo 'export PATH=/opt/ansible/bin:$PATH' >> /home/__USER__/.bashrc

install -d -o __USER__ -g __USER__ /home/__USER__/lab /home/__USER__/.ssh
cp -r /opt/grp9-lab/. /home/__USER__/lab/
mv /home/__USER__/lab/ssh_config /home/__USER__/.ssh/config
chmod 600 /home/__USER__/.ssh/config
chown -R __USER__:__USER__ /home/__USER__
sudo -u __USER__ -H /opt/ansible/bin/ansible-galaxy collection install -r /home/__USER__/lab/ansible/requirements.yml

if /opt/ansible/bin/ansible --version >/dev/null 2>&1 && \
   [ -d /home/__USER__/.ansible/collections/ansible_collections/cisco/ios ]; then
  echo "READY $(date)" > /etc/grp9-ready
else
  echo "SETUP FAILED - see /var/log/grp9-setup.log" > /etc/grp9-ready
fi
cat /etc/grp9-ready
"""

SSH_CONFIG = """Host r1
  HostName 192.168.100.11
Host r2
  HostName 192.168.100.12
Host r1 r2
  User admin
  KexAlgorithms +diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1
  HostKeyAlgorithms +ssh-rsa
  PubkeyAcceptedAlgorithms +ssh-rsa
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  LogLevel ERROR
"""

RSYSLOG = """module(load="imudp")
input(type="imudp" port="514" ruleset="network")
ruleset(name="network") {
  action(type="omfile" file="/var/log/network.log" fileCreateMode="0644")
}
"""

MOTD = """
  grp9 automation host  (CP353301 Capstone demo)
  -------------------------------------------------
  cat /etc/grp9-ready        -> READY when setup finished
  cd ~/lab/ansible           -> Ansible project (vault password: grp9lab)
  ssh r1 / ssh r2            -> routers (admin / Cisco@123)
  tail -f /var/log/network.log -> syslog from R1/R2

"""


def fill(text):
    return (text.replace("__SBX_IP__", SBX_IP).replace("__SBX_GW__", SBX_GW)
            .replace("__USER__", USER))


def block(text, indent):
    pad = " " * indent
    return "\n".join((pad + line) if line else "" for line in text.rstrip("\n").split("\n"))


def write_file_entry(path, content, perms="0644"):
    return (f"  - path: {path}\n"
            f"    permissions: '{perms}'\n"
            f"    content: |\n{block(content, 6)}\n")


def cloud_init():
    files = [
        write_file_entry("/usr/local/sbin/grp9-net.sh", fill(NET_SCRIPT), "0755"),
        write_file_entry("/usr/local/sbin/grp9-setup.sh", fill(SETUP_SCRIPT), "0755"),
        write_file_entry("/etc/rsyslog.d/10-network.conf", RSYSLOG),
        write_file_entry("/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg", "network: {config: disabled}\n"),
        write_file_entry("/etc/motd", MOTD),
        write_file_entry("/opt/grp9-lab/ssh_config", SSH_CONFIG, "0600"),
    ]
    for rel in ANSIBLE_FILES:
        files.append(write_file_entry(f"/opt/grp9-lab/ansible/{rel}", (ROOT / "ansible" / rel).read_text()))
    for rel in CONFIG_FILES:
        files.append(write_file_entry(f"/opt/grp9-lab/configs/{rel}", (ROOT / "configs" / rel).read_text()))
    return (
        "#cloud-config\n"
        "hostname: automation-host\n"
        "manage_etc_hosts: true\n"
        "ssh_pwauth: true\n"
        "users:\n"
        "  - default\n"
        f"  - name: {USER}\n"
        "    gecos: Group 9 automation user\n"
        "    groups: [adm, sudo]\n"
        "    shell: /bin/bash\n"
        "    sudo: 'ALL=(ALL) NOPASSWD:ALL'\n"
        "    lock_passwd: false\n"
        f"    plain_text_passwd: '{USER_PW}'\n"
        "write_files:\n" + "".join(files) +
        "runcmd:\n"
        "  - [bash, /usr/local/sbin/grp9-setup.sh]\n"
        "final_message: 'grp9 automation host finished cloud-init after $UPTIME seconds'\n"
    )


def ios_node(nid, label, x, y, cfg):
    ifaces = "      - id: i0\n        label: Loopback0\n        type: loopback\n"
    for s in range(4):
        ifaces += (f"      - id: i{s + 1}\n        label: GigabitEthernet0/{s}\n"
                   f"        slot: {s}\n        type: physical\n")
    return (f"  - boot_disk_size: 0\n    configuration: |-\n{block(cfg, 6)}\n"
            f"    cpu_limit: 100\n    cpus: 1\n    data_volume: 0\n    hide_links: false\n"
            f"    id: {nid}\n    label: {label}\n    node_definition: iosv\n    ram: 512\n"
            f"    tags: []\n    x: {x}\n    y: {y}\n    interfaces:\n{ifaces}")


def simple_node(nid, label, nodedef, x, y, cfg, ports):
    ifaces = "".join(f"      - id: i{s}\n        label: {p}\n        slot: {s}\n        type: physical\n"
                     for s, p in enumerate(ports))
    cfg_yaml = f"configuration: |-\n{block(cfg, 6)}" if "\n" in cfg else f"configuration: {cfg or chr(39) * 2}"
    return (f"  - id: {nid}\n    label: {label}\n    node_definition: {nodedef}\n"
            f"    x: {x}\n    y: {y}\n    {cfg_yaml}\n    tags: []\n    interfaces:\n{ifaces}")


def link(lid, n1, i1, n2, i2, label):
    return f"  - id: {lid}\n    n1: {n1}\n    n2: {n2}\n    i1: {i1}\n    i2: {i2}\n    label: {label}\n"


NOTES = f"""CP353301 Capstone - Group 9 - Automation demo
1. Check the two external connectors: sandbox-bridge = System Bridge (bridge0), internet-nat = NAT.
2. Make sure {SBX_IP.split('/')[0]} is free on the sandbox network, then start the lab.
3. Wait ~5 minutes, then from the Mac (VPN connected): ssh {USER}@{SBX_IP.split('/')[0]}  (password {USER_PW})
4. cat /etc/grp9-ready  ->  READY
5. cd ~/lab/ansible && ansible-playbook precheck.yml -J   (vault password: grp9lab)
"""


def lab_yaml(ci):
    r1 = (ROOT / "configs" / "R1-day0.cfg").read_text()
    r2 = (ROOT / "configs" / "R2-day0.cfg").read_text()
    nodes = [
        ios_node("n0", "R1", -200, 160, r1),
        ios_node("n1", "R2", 200, 160, r2),
        simple_node("n2", "SW-MGMT", "unmanaged_switch", 0, 0, "", [f"port{i}" for i in range(8)]),
        (simple_node("n3", "automation-host", "ubuntu", 0, -180, ci, ["ens2", "ens3", "ens4"])
         .replace("    tags: []\n", "    cpus: 2\n    ram: 2048\n    tags: []\n", 1)),
        simple_node("n4", "sandbox-bridge", "external_connector", -280, -180, "bridge0", ["port"]),
        simple_node("n5", "internet-nat", "external_connector", 280, -180, "virbr0", ["port"]),
    ]
    links = [
        link("l0", "n0", "i1", "n2", "i0", "R1-Gi0/0<->SW-MGMT-port0"),
        link("l1", "n1", "i1", "n2", "i1", "R2-Gi0/0<->SW-MGMT-port1"),
        link("l2", "n3", "i0", "n2", "i2", "automation-host-mgmt0<->SW-MGMT-port2"),
        link("l3", "n0", "i2", "n1", "i2", "R1-Gi0/1<->R2-Gi0/1"),
        link("l4", "n3", "i1", "n4", "i0", "automation-host-sbx0<->sandbox-bridge"),
        link("l5", "n3", "i2", "n5", "i0", "automation-host-inet0<->internet-nat"),
    ]
    return ("lab:\n"
            "  description: CP353301 Capstone Group 9 - Ansible + EEM automation demo (R1, R2 IOSv; Ubuntu control node)\n"
            f"  notes: |-\n{block(NOTES, 4)}\n"
            "  title: grp9-automation-demo\n"
            "  version: 0.1.0\n"
            "links:\n" + "".join(links) +
            "nodes:\n" + "".join(nodes))


if __name__ == "__main__":
    ci = cloud_init()
    (ROOT / "configs" / "automation-host-cloud-init.yaml").write_text(ci)
    (ROOT / "grp9-automation-lab.yaml").write_text(lab_yaml(ci))
    print("wrote", ROOT / "grp9-automation-lab.yaml")
    print("wrote", ROOT / "configs" / "automation-host-cloud-init.yaml")
