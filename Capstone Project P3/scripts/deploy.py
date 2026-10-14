"""deploy.py — Render Jinja2 -> Backup -> Push (send_config_set) -> Save -> Golden copy -> Diff

ใช้งาน:
  python scripts/deploy.py --dry-run           render อย่างเดียว เก็บที่ configs/rendered/ (ไม่แตะอุปกรณ์)
  python scripts/deploy.py                     push ทุกเครื่องพร้อมกัน (parallel)
  python scripts/deploy.py R2-BR1 R3-DC        push เฉพาะบางเครื่อง
  python scripts/deploy.py --golden            หลัง verify ผ่าน: เก็บ running-config เป็น flash:golden.cfg
                                              (ใช้ rollback ด้วย configure replace ใน fault.py)
"""
import argparse
import difflib

from common import (CONFIGS, banner, config_lines, connect, load_inventory, now, render,
                    run_parallel, select)


def backup(conn, name: str, label: str) -> str:
    cfg = conn.send_command("show running-config", read_timeout=60)
    d = CONFIGS / "backups"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}_{label}.cfg").write_text(cfg, encoding="utf-8")
    return cfg


def push(dev: dict, golden: bool = False) -> str:
    stamp = now()
    conn = connect(dev, via="ssh", tag="deploy")
    before = backup(conn, dev["name"], f"{stamp}_before")
    if golden:
        out = conn.send_command(f"copy running-config {dev['flash']}golden.cfg", read_timeout=60)
    else:
        out = conn.send_config_set(config_lines(render(dev)), read_timeout=300, exit_config_mode=True, cmd_verify=False)
        out += conn.save_config()
    after = backup(conn, dev["name"], f"{stamp}_after")
    conn.disconnect()

    # เก็บฉบับล่าสุด (deliverable: running-config ฉบับเต็มของทุกอุปกรณ์)
    (CONFIGS / "running").mkdir(parents=True, exist_ok=True)
    (CONFIGS / "running" / f"{dev['name']}.cfg").write_text(after, encoding="utf-8")
    diff = difflib.unified_diff(before.splitlines(), after.splitlines(), "before", "after", lineterm="", n=0)
    changes = [ln for ln in diff if ln[:1] in "+-" and not ln.startswith(("+++", "---"))
               and "Last configuration change" not in ln and "NVRAM config last updated" not in ln]
    (CONFIGS / "backups" / f"{dev['name']}_{stamp}.diff").write_text("\n".join(changes), encoding="utf-8")
    errors = [ln.strip() for ln in out.splitlines()
              if ln.strip().startswith("%") and any(k in ln for k in ("Invalid", "Incomplete", "Ambiguous"))]
    return f"{len(changes)} changed lines" + (f" | IOS errors: {errors}" if errors else "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("devices", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--golden", action="store_true")
    args = ap.parse_args()
    devs = select(load_inventory(), args.devices)

    if args.dry_run:
        out_dir = CONFIGS / "rendered"
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, dev in devs.items():
            text = render(dev)
            (out_dir / f"{name}.cfg").write_text(text, encoding="utf-8")
            print(f"[render] {name}: {len(config_lines(text))} lines -> configs/rendered/{name}.cfg")
        return

    banner(("Save golden config" if args.golden else "Deploy") + f": {', '.join(devs)}")
    results = run_parallel(devs, lambda d: push(d, args.golden))
    failed = 0
    for name in devs:
        res = results[name]
        ok = not isinstance(res, Exception) and "IOS errors" not in str(res)
        failed += not ok
        print(f"[{' OK ' if ok else 'FAIL'}] {name:8} {res}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
