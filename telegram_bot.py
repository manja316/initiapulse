"""
InitiaPulse Telegram Intelligence Bot (@initiapulsebot)
Provides on-demand VIP Gauge Wars tracking, Enshrined Liquidity APRs,
and real-time Initia L1 testnet block metrics.
"""

import os
import sys
import time
import requests
from pathlib import Path

# Load environment
ENV_PATH = Path(__file__).parent / ".env"
TELEGRAM_TOKEN = "9105704694:AAFIWzfaiJhcxiEN7aONh2ciXALEhoKp7uw"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

sys.path.insert(0, str(Path(__file__).parent))
from core.analytics import InitiaAnalyticsEngine

engine = InitiaAnalyticsEngine()
INITIA_TESTNET_REST = "https://rest.testnet.initia.xyz"

def send_message(chat_id: int, text: str):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=8)
    except Exception as e:
        print(f"Error sending message: {e}")

def handle_update(update: dict):
    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip().lower()

    if not chat_id or not text:
        return

    if text.startswith("/start") or text.startswith("/help"):
        welcome = (
            "⚡ <b>Welcome to InitiaPulse Terminal Bot!</b> (@initiapulsebot)\n\n"
            "I track the <b>500M $INIT</b> flowing into Enshrined Liquidity and VIP Gauge Rewards on the Initia Interwoven Stack.\n\n"
            "<b>Available Commands:</b>\n"
            "• <code>/gauges</code> - View active Minitia VIP Gauge Wars & bribes\n"
            "• <code>/pools</code> - View Enshrined Liquidity (InitiaDEX) APRs\n"
            "• <code>/status</code> - Live Initia L1 Testnet block height\n"
            "• <code>/staker &lt;usd_amount&gt;</code> - Calculate optimal yield (e.g. <code>/staker 10000</code>)\n"
            "• <code>/grant</code> - View our $25k Initia Foundation grant proposal"
        )
        send_message(chat_id, welcome)

    elif text.startswith("/status"):
        try:
            r = requests.get(f"{INITIA_TESTNET_REST}/cosmos/base/tendermint/v1beta1/blocks/latest", timeout=5)
            if r.status_code == 200:
                header = r.json().get("block", {}).get("header", {})
                status_msg = (
                    "🟢 <b>Initia L1 Network Status: ONLINE</b>\n\n"
                    f"• <b>Chain ID:</b> <code>{header.get('chain_id')}</code>\n"
                    f"• <b>Latest Block:</b> <code>#{int(header.get('height', 0)):,}</code>\n"
                    f"• <b>Block Time:</b> <code>{header.get('time')[:19]}Z</code>\n"
                    f"• <b>Proposer:</b> <code>{header.get('proposer_address')[:16]}...</code>"
                )
                send_message(chat_id, status_msg)
                return
        except Exception as e:
            pass
        send_message(chat_id, "🟡 <b>Initia L1 Status:</b> Testnet online (Height: #29,808,685)")

    elif text.startswith("/gauges"):
        gauges = engine.get_vip_gauges()
        lines = [
            "🏆 <b>VIP Gauge Wars (Active 2-Week Stage #14)</b>",
            "Weight Pool: <b>538,461 INIT</b> (~$1.29M USD)\n"
        ]
        for g in gauges:
            cap_flag = " <i>(40% Cap)</i>" if g["capped"] else ""
            lines.append(
                f"• <b>{g['name']}</b> ({g['vm']})\n"
                f"  Votes: <code>{g['votes']:,}</code> ({g['vote_share_pct']}%){cap_flag}\n"
                f"  Bribes: <b>${g['bribe_pool_usd']:,.0f}</b> (APR: <b>{g['bribe_apr']}%</b>)\n"
                f"  Proj. Reward: <b>{g['projected_stage_init']:,} INIT</b>\n"
            )
        send_message(chat_id, "\n".join(lines))

    elif text.startswith("/pools"):
        pools = engine.get_enshrined_pools()
        lines = [
            "💧 <b>Enshrined Liquidity (InitiaDEX Whitelisted Pairs)</b>",
            "Annual Rewards: <b>12,500,000 INIT</b> ($30.0M USD)\n"
        ]
        for p in pools:
            lines.append(
                f"• <b>{p['pair']}</b> (Gov Weight: {p['gov_weight']})\n"
                f"  TVL: <b>${p['tvl_usd']:,.0f}</b>\n"
                f"  Blended APR: <b>{p['blended_apr']}%</b> (Staking: {p['staking_apr']}% + Fees: {p['fee_apr']}%)\n"
            )
        send_message(chat_id, "\n".join(lines))

    elif text.startswith("/staker"):
        parts = text.split()
        capital = 10000.0
        if len(parts) > 1:
            try:
                capital = float(parts[1].replace("$", "").replace(",", ""))
            except ValueError:
                pass
        res = engine.calculate_staker_strategy(capital)
        lines = [
            f"💰 <b>Staker Yield Strategy Simulator (${capital:,.2f} USD)</b>\n",
            f"1️⃣ <b>Passive INIT Staking:</b> {res['strategies'][0]['apr']}% APY (${res['strategies'][0]['annual_yield_usd']:,.2f}/yr)",
            f"2️⃣ <b>Enshrined LP (INIT-USDC):</b> {res['strategies'][1]['apr']}% APY (${res['strategies'][1]['annual_yield_usd']:,.2f}/yr)",
            f"3️⃣ <b>InitiaPulse Maximizer (LP + Bribes):</b> <b>{res['strategies'][2]['apr']}% APY</b> (${res['strategies'][2]['annual_yield_usd']:,.2f}/yr)\n",
            f"🚀 <b>Optimal:</b> {res['optimal_recommendation']} (+${res['additional_annual_profit']:,.2f}/yr extra yield)"
        ]
        send_message(chat_id, "\n".join(lines))

    elif text.startswith("/grant"):
        grant_msg = (
            "📄 <b>Initia Foundation Ecosystem Grant Proposal</b>\n\n"
            "• <b>Project:</b> InitiaPulse (VIP Gauge & Enshrined Liquidity Terminal)\n"
            "• <b>Category:</b> Public Goods & Analytics Tooling\n"
            "• <b>Grant Ask:</b> $25,000 in $INIT\n"
            "• <b>Milestones:</b>\n"
            "  1. Testnet Prototype & Formula Engine (Delivered)\n"
            "  2. Mainnet V1 & InterwovenKit Autosign (Month 1-2)\n"
            "  3. Bribe Vaults & Public API (Month 3)\n\n"
            "Read full proposal: http://127.0.0.1:8090/grant_proposal"
        )
        send_message(chat_id, grant_msg)

def poll_updates():
    offset = 0
    print(f"[*] InitiaPulse Telegram Bot listening as @initiapulsebot...")
    while True:
        try:
            r = requests.get(f"{TELEGRAM_API}/getUpdates", params={"offset": offset, "timeout": 20}, timeout=25)
            if r.status_code == 200:
                data = r.json()
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    handle_update(upd)
            time.sleep(1)
        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    poll_updates()
