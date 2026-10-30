# ⚡ InitiaPulse Terminal
### The VIP Gauge War & Enshrined Liquidity Intelligence Hub for Initia L1 & Minitias

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Network: Initia Testnet](https://img.shields.io/badge/Initia_Testnet-initiation--2-blue)](https://rest.testnet.initia.xyz)
[![Telegram Bot](https://img.shields.io/badge/Telegram_Bot-@initiapulsebot-0088cc)](https://t.me/initiapulsebot)
[![Hosting: Vercel](https://img.shields.io/badge/Hosted_on-Vercel-black)](https://initiapulse-phi.vercel.app)

---

## 🧭 Executive Summary

Under Initia's tokenomics, **500,000,000 $INIT (50% of the total 1B fixed supply)** is dedicated to two interdependent mechanisms:
1. **Enshrined Liquidity (25% / 250M $INIT)**: Protocol-owned liquidity backing the inter-rollup routing architecture.
2. **VIP (Validator Investment Program) Rewards (25% / 250M $INIT)**: Bi-weekly gauge emissions directed toward high-performing Minitia rollups and liquidity pairs.

Because VIP allocations are determined by periodic token-weighted gauge votes, Initia naturally creates a **high-stakes Gauge War** (analogous to the Curve Wars on Ethereum). Minitia rollup operators compete for gauge weights to lower their cost of capital, stakers seek yield optimization across pools, and rollups deploy bribe incentives to capture maximum emissions.

**InitiaPulse** is the first dedicated, public-goods analytics terminal designed to model, track, and maximize capital efficiency across Initia's VIP gauge cycles and Enshrined Liquidity pools.

---

## 🚀 Key Modules

### 1. VIP Gauge War Tracker & Forecasting
- Real-time tracking of current 14-day VIP Stages.
- Live gauge weights ($w_i$), vote distribution, and historical shifts across Minitia ecosystems (e.g., MiniEVM, MiniMove, MiniWasm).
- Forward emission projections based on stage decay curves ($17.5M $INIT / year baseline, ~538,461 $INIT per 14-day epoch).

### 2. Enshrined Liquidity Engine & APR Maximizer
- Mathematical calculation of pool weight factors:
  $$r_a = \frac{w_a \cdot r_{\text{total}}}{\sum_{i} w_i}$$
- Real-time comparison between staking native $INIT vs. pairing in Enshrined LP (INIT-USDC, INIT-ETH, INIT-TIA).
- Impermanent loss risk-adjusted yield indices.

### 3. Rollup Bribe ROI Calculator
- Enables Minitia founders and treasuries to compute the exact **Bribe Efficiency Ratio**:
  $$\text{Bribe ROI} = \frac{\text{Emissions Captured Value (\USD)}}{\text{Bribe Capital Spent (\USD)}}$$
- Simulates how much bribe funding is needed to flip a competitor rollup's gauge rank.

### 4. Autonomous Telegram Bot (`@initiapulsebot`)
- Instant queries for `/gauges`, `/pools`, `/status`, `/staker`, and `/grant`.
- Automated epoch threshold alerts: notifies subscribers when a gauge battle shifts within 48 hours of stage epoch close.

---

## 🛠️ Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Initia L1 Network                    │
│             (RPC / REST: initiation-2)                 │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               InitiaPulse Backend Engine               │
│  - FastAPI REST API & Mathematical Analytics (core/)   │
│  - Gauge Cycle Emission Forecaster                     │
│  - Real-time Blockchain Client & Fallback Cache        │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────┐    ┌─────────────────────────┐
│     Web UI Dashboard     │    │  Telegram Sentinel Bot  │
│ - Glassmorphic Dark UI   │    │ - Bot: @initiapulsebot  │
│ - Gauge Simulator        │    │ - Instant alerts & stats│
│ - Staker Yield Engine    │    └─────────────────────────┘
└──────────────────────────┘
```

---

## 📦 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ (for Vercel CLI deployment)

### Local Setup
```bash
# Clone the repository
git clone https://github.com/manja316/initiapulse.git
cd initiapulse

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Telegram and Initia RPC settings

# Launch the local dashboard
python app.py
```
Open [http://localhost:8090](http://localhost:8090) in your browser.

---

## 📜 Initia Foundation Ecosystem Grant Proposal

InitiaPulse is built as a zero-rent, neutral public utility for the entire Initia ecosystem. 
The comprehensive **$25,000 Ecosystem Grant Proposal** detailing technical milestones, community deliverables, and economic impact is accessible at:
- Local/Deployed URL: `/grant_proposal`
- Source: [grant_proposal/initia_foundation_grant.html](grant_proposal/initia_foundation_grant.html)

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
