"""Network detector: classify current network, write status JSON.

Net types:
  LAN       - wired ethernet
  HOTSPOT   - WiFi SSID matches phone hotspot keywords
  WIFI      - other WiFi
  UNKNOWN   - fallback

Override with env var NETWORK_TYPE for testing.
"""
import json
import os
import sys
import platform
from datetime import datetime, timezone

HOTSPOT_KEYWORDS = ("iphone", "android", "热点", "hotspot", "mobile",
                    "samsung", "xiaomi", "redmi", "huawei", "poco")

# Windows: write to logs/network_status.json (not /tmp)
_ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS_PATH = os.path.join(_ROOT, "logs", "network_status.json")


def detect_windows() -> str:
    import subprocess
    try:
        raw = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"],
            stderr=subprocess.DEVNULL, timeout=5,
        )
        # netsh output codepage varies by console (GBK/UTF-8), decode both ways
        try:
            out = raw.decode("utf-8")
        except UnicodeDecodeError:
            out = raw.decode("gbk", errors="ignore")
        ssid = ""
        for line in out.splitlines():
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":", 1)[1].strip()
                break
        if not ssid:
            return "LAN"
        low = ssid.lower()
        if any(k in low for k in HOTSPOT_KEYWORDS):
            return "HOTSPOT"
        return "WIFI"
    except subprocess.CalledProcessError:
        # netsh wlan query failing typically means no wireless stack -> wired
        return "LAN"
    except Exception:
        return "UNKNOWN"


def detect_linux() -> str:
    try:
        import subprocess
        out = subprocess.check_output(
            ["nmcli", "-t", "-f", "TYPE,DEVICE", "device", "status"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        )
        for line in out.splitlines():
            if line.startswith("ethernet"):
                return "LAN"
        # crude: no ethernet -> assume wifi
        return "WIFI"
    except Exception:
        return "UNKNOWN"


def detect() -> str:
    override = os.environ.get("NETWORK_TYPE", "").upper()
    if override in ("LAN", "WIFI", "HOTSPOT", "UNKNOWN"):
        return override
    system = platform.system()
    if system == "Windows":
        return detect_windows()
    if system == "Linux":
        return detect_linux()
    return "UNKNOWN"


def write_status(net_type: str) -> dict:
    status = {
        "net_type": net_type,
        "detected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hotspot": net_type == "HOTSPOT",
        "allow_heavy_sync": net_type in ("LAN", "WIFI"),
        "allow_full_backtest_upload": net_type in ("LAN", "WIFI"),
    }
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    return status


def read_status() -> dict:
    if not os.path.exists(STATUS_PATH):
        return {"net_type": "UNKNOWN", "allow_heavy_sync": True}
    with open(STATUS_PATH, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--simulate", choices=["LAN", "WIFI", "HOTSPOT", "UNKNOWN"],
                   help="override detected network type")
    args = p.parse_args()
    if args.simulate:
        os.environ["NETWORK_TYPE"] = args.simulate
        nt = args.simulate
    else:
        nt = detect()
    s = write_status(nt)
    print(json.dumps(s, indent=2, ensure_ascii=False))
