"""common.py — โค้ดกลางที่ทุกสคริปต์ใช้ร่วมกัน"""
from __future__ import annotations

import datetime as dt
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from netmiko import ConnectHandler, redispatch

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
LOGS = ROOT / "logs"
EVIDENCE = ROOT / "evidence"
CONFIGS = ROOT / "configs"

TEMPLATE_BY_ROLE = {"isp": "isp.j2", "hub": "site.j2", "spoke": "site.j2"}


def now() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def load_inventory(path: Path | None = None) -> dict[str, dict]:
    path = path or ROOT / "inventory.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    defaults = data.get("defaults", {})
    env_override = {
        "username": os.getenv("NET_USER"),
        "password": os.getenv("NET_PASS"),
        "secret": os.getenv("NET_SECRET"),
    }
    devices = {}
    for name, dev in data["devices"].items():
        merged = {**defaults, **dev, "name": name}
        merged.update({k: v for k, v in env_override.items() if v})
        if "cml" in merged:
            merged["cml"] = {
                **merged["cml"],
                "username": os.getenv("CML_USER", merged["cml"].get("username")),
                "password": os.getenv("CML_PASS", merged["cml"].get("password")),
            }
        devices[name] = merged
    return devices


def select(devices: dict, names: list[str] | None) -> dict:
    if not names:
        return devices
    unknown = [n for n in names if n not in devices]
    if unknown:
        sys.exit(f"[!] ไม่พบอุปกรณ์ใน inventory: {', '.join(unknown)}")
    return {n: devices[n] for n in names}


def render(dev: dict, template: str | None = None) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    tpl = env.get_template(template or TEMPLATE_BY_ROLE[dev["role"]])
    return tpl.render(**dev)


def config_lines(text: str) -> list[str]:
    return [ln.rstrip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("!") and ln.strip() != "end"]


def connect(dev: dict, via: str = "ssh", tag: str = "session"):
    LOGS.mkdir(exist_ok=True)
    log = str(LOGS / f"{dev['name']}_{tag}_{via}.log")
    if via == "ssh":
        conn = ConnectHandler(
            device_type=dev["device_type"],
            host=dev["mgmt_ip"],
            username=dev["username"],
            password=dev["password"],
            secret=dev["secret"],
            session_log=log,
            fast_cli=False,
            conn_timeout=20,
            disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
        )
        conn.enable()
    elif via == "console":
        conn = _cml_console(dev, log)
    else:
        raise ValueError(via)
    return conn


def _cml_console(dev: dict, log: str):
    cml = dev["cml"]
    conn = ConnectHandler(
        device_type="terminal_server",
        host=cml["host"],
        username=cml["username"],
        password=cml["password"],
        secret=dev["secret"],
        session_log=log,
        fast_cli=False,
        conn_timeout=20,
    )
    conn.write_channel(f"open /{cml['lab']}/{dev['name']}/0\r")
    time.sleep(2)
    for _ in range(6):
        conn.write_channel("\r")
        time.sleep(1.5)
        out = conn.read_channel()
        if "Username" in out:
            conn.write_channel(dev["username"] + "\r")
            time.sleep(1)
            conn.write_channel(dev["password"] + "\r")
            time.sleep(2)
            out = conn.read_channel()
        if "Password" in out:
            conn.write_channel(dev["secret"] + "\r")
            time.sleep(1.5)
            out = conn.read_channel()
        if f"{dev['name']}#" in out:
            break
        if f"{dev['name']}>" in out:
            conn.write_channel("enable\r")
            time.sleep(1)
            conn.write_channel(dev["secret"] + "\r")
            time.sleep(1.5)
            break
    conn.write_channel("end\r")
    time.sleep(0.5)
    conn.write_channel("terminal length 0\r")
    conn.write_channel("terminal width 511\r")
    time.sleep(1)
    conn.read_channel()
    redispatch(conn, device_type="cisco_ios", session_prep=False)
    conn.find_prompt()
    return conn


def run_parallel(devices: dict, func, max_workers: int = 8) -> dict:
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(func, dev): name for name, dev in devices.items()}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                results[name] = fut.result()
            except Exception as exc:
                results[name] = exc
    return results


def banner(text: str) -> None:
    print("\n" + "=" * 72 + f"\n  {text}\n" + "=" * 72)
