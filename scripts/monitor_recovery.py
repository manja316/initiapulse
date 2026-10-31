"""
InitiaPulse Sentinel: Recovery & Unhalt Monitor
Polls:
1. app.initia.xyz for maintenance/404 lifting
2. rest.initia.xyz (mainnet) for block production resumption
3. initia-labs/initia GitHub releases/tags for validator patch releases
4. Binance Spot INIT/USDT for market liquidity signals
Logs output to recovery_status.json and alerts via Telegram bot.
"""

import sys
import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATUS_FILE = BASE_DIR / "recovery_status.json"

TELEGRAM_BOT_TOKEN = "9105704694:AAFIWzfaiJhcxiEN7aONh2ciXALEhoKp7uw"
TELEGRAM_CHAT_ID = "257190241"

def send_alert(text: str):
    print(f"[ALERT] {text}")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=8)
    except Exception as e:
        print(f"[ALERT SEND ERROR] {e}")

def check_all() -> dict:
    now_str = datetime.now(timezone.utc).isoformat()
    result = {
        "timestamp": now_str,
        "app_status": "UNKNOWN",
        "app_maintenance": True,
        "mainnet_rpc_online": False,
        "mainnet_latest_height": 0,
        "github_latest_release": None,
        "binance_price_usd": 0.0,
        "signals": []
    }

    # 1. Check app.initia.xyz
    try:
        r = requests.get("https://app.initia.xyz", timeout=6)
        result["app_status"] = f"HTTP_{r.status_code}"
        result["app_maintenance"] = ("404" in r.text or "halted" in r.text)
    except Exception as e:
        result["app_status"] = f"ERROR: {str(e)[:40]}"

    # 2. Check mainnet REST
    try:
        r = requests.get("https://rest.initia.xyz/cosmos/base/tendermint/v1beta1/blocks/latest", timeout=5)
        if r.status_code == 200:
            data = r.json()
            height = int(data.get("block", {}).get("header", {}).get("height", 0))
            result["mainnet_rpc_online"] = True
            result["mainnet_latest_height"] = height
            result["signals"].append(f"MAINNET_RPC_ONLINE: Height #{height}")
    except Exception:
        pass

    # 3. Check GitHub releases
    try:
        r = requests.get("https://api.github.com/repos/initia-labs/initia/releases", timeout=5, headers={"User-Agent": "InitiaPulse-Monitor"})
        if r.status_code == 200:
            rels = r.json()
            if rels:
                latest = rels[0].get("tag_name")
                result["github_latest_release"] = latest
    except Exception:
        pass

    # 4. Check Binance Spot Price
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=INITUSDT", timeout=4)
        if r.status_code == 200:
            price = float(r.json().get("price", 0.0))
            result["binance_price_usd"] = price
    except Exception:
        pass

    # Compare with previous state
    prev = {}
    if STATUS_FILE.exists():
        try:
            prev = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Check for state changes / unhalt signals
    if result["mainnet_rpc_online"] and not prev.get("mainnet_rpc_online"):
        msg = (
            "🚨 <b>INITIA MAINNET RECOVERY DETECTED!</b>\n\n"
            f"• Mainnet RPC is producing blocks at height #{result['mainnet_latest_height']}.\n"
            f"• Binance Price: ${result['binance_price_usd']:.4f}\n"
            "Check Explorer: https://scan.initia.xyz/interwoven-1"
        )
        send_alert(msg)

    if prev.get("github_latest_release") and result["github_latest_release"] != prev.get("github_latest_release"):
        msg = (
            "🛠️ <b>INITIA PATCH RELEASE DETECTED!</b>\n\n"
            f"New release tag published: <b>{result['github_latest_release']}</b>\n"
            "Validators are likely upgrading now."
        )
        send_alert(msg)

    # Save current status
    STATUS_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    res = check_all()
    print("Monitor check complete:")
    print(json.dumps(res, indent=2))
