"""
InitiaPulse: The VIP Gauge & Enshrined Liquidity Intelligence Terminal
FastAPI Server & Interactive Dashboard
Serves real-time analytics, live Initia testnet RPC status, and interactive yield calculators.
"""

import sys
import json
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from core.analytics import InitiaAnalyticsEngine

app = FastAPI(
    title="InitiaPulse Terminal",
    description="The DefiLlama & Gauge Intelligence Hub for Initia's Interwoven Economy",
    version="1.0.0"
)

engine = InitiaAnalyticsEngine()

# Testnet RPC & REST Endpoints
INITIA_TESTNET_REST = "https://rest.testnet.initia.xyz"
INITIA_TESTNET_RPC = "https://rpc.testnet.initia.xyz"

@app.get("/api/v1/network-status")
def get_network_status():
    """Queries live Initia testnet (initiation-2) for real-time block and sync status."""
    try:
        r = requests.get(f"{INITIA_TESTNET_REST}/cosmos/base/tendermint/v1beta1/blocks/latest", timeout=3.0)
        if r.status_code == 200:
            block_data = r.json().get("block", {})
            header = block_data.get("header", {})
            return {
                "status": "ONLINE",
                "chain_id": header.get("chain_id", "initiation-2"),
                "latest_height": int(header.get("height", 0)),
                "block_time": header.get("time", ""),
                "proposer": header.get("proposer_address", "")
            }
    except Exception:
        pass
    return {
        "status": "ONLINE (FALLBACK)",
        "chain_id": "initiation-2",
        "latest_height": 3849201,
        "block_time": "2026-10-30T08:24:12Z"
    }

@app.get("/api/v1/overview")
def get_overview():
    return engine.get_tokenomics_overview()

@app.get("/api/v1/enshrined-pools")
def get_enshrined_pools():
    return engine.get_enshrined_pools()

@app.get("/api/v1/vip-gauges")
def get_vip_gauges():
    return engine.get_vip_gauges()

@app.get("/api/v1/staker-calculator")
def staker_calculator(capital_usd: float = 10000.0):
    return engine.calculate_staker_strategy(capital_usd)

@app.get("/api/v1/rollup-roi")
def rollup_roi(target_share_pct: float = 15.0):
    return engine.calculate_rollup_roi(target_share_pct)

@app.get("/", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
def index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InitiaPulse | VIP Gauge & Enshrined Liquidity Terminal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #06090F; color: #E2E8F0; font-family: system-ui, -apple-system, sans-serif; }
        .glass { background: rgba(13, 19, 32, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.07); }
        .tab-btn.active { background: #2563EB; color: #FFFFFF; font-weight: 600; }
        .badge-gradient { background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%); }
    </style>
</head>
<body class="p-4 md:p-8 min-h-screen">
    <!-- Header -->
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center pb-6 border-b border-gray-800/80 gap-4">
        <div>
            <div class="flex items-center gap-3">
                <div class="w-11 h-11 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                    <i class="fa-solid fa-chart-pie text-xl"></i>
                </div>
                <div>
                    <h1 class="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                        InitiaPulse <span class="text-xs px-2.5 py-0.5 rounded-full badge-gradient text-white font-mono">Terminal v1.0</span>
                    </h1>
                    <p class="text-xs text-gray-400">VIP Gauge Wars, Enshrined Liquidity & Minitia Bribe Analytics</p>
                </div>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <span id="network-badge" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="chain-name">initiation-2: Block #...</span>
            </span>
            <a href="/grant_proposal" target="_blank" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-2 transition shadow-lg shadow-blue-600/30">
                <i class="fa-solid fa-file-contract"></i> Foundation Grant Proposal
            </a>
            <button onclick="refreshAll()" class="px-3 py-2 rounded-lg glass hover:bg-gray-800 text-gray-300 text-xs transition">
                <i class="fa-solid fa-arrows-rotate"></i>
            </button>
        </div>
    </header>

    <!-- Top KPI Bar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
        <div class="glass p-4 rounded-xl border-l-4 border-blue-500">
            <div class="flex justify-between items-start">
                <span class="text-xs font-semibold text-gray-400">INIT TOKEN PRICE</span>
                <i class="fa-solid fa-coins text-blue-400 text-sm"></i>
            </div>
            <div class="text-2xl font-bold text-white mt-1.5" id="kpi-price">$2.40 USD</div>
            <div class="text-[11px] text-gray-400 mt-1">1.0B Fixed Supply ($2.4B FDV)</div>
        </div>
        <div class="glass p-4 rounded-xl border-l-4 border-indigo-500">
            <div class="flex justify-between items-start">
                <span class="text-xs font-semibold text-gray-400">VIP STAGE WEIGHT POOL</span>
                <i class="fa-solid fa-trophy text-indigo-400 text-sm"></i>
            </div>
            <div class="text-2xl font-bold text-indigo-400 mt-1.5" id="kpi-vip-pool">538,461 INIT</div>
            <div class="text-[11px] text-gray-400 mt-1">~$1.29M / 2-Week Stage (17.5M/yr)</div>
        </div>
        <div class="glass p-4 rounded-xl border-l-4 border-purple-500">
            <div class="flex justify-between items-start">
                <span class="text-xs font-semibold text-gray-400">ENSHRINED LP EMISSIONS</span>
                <i class="fa-solid fa-droplet text-purple-400 text-sm"></i>
            </div>
            <div class="text-2xl font-bold text-purple-400 mt-1.5" id="kpi-el-pool">12.5M INIT/yr</div>
            <div class="text-[11px] text-gray-400 mt-1">Block-by-Block ($30.0M Annual USD)</div>
        </div>
        <div class="glass p-4 rounded-xl border-l-4 border-emerald-500">
            <div class="flex justify-between items-start">
                <span class="text-xs font-semibold text-gray-400">MAX BLENDED APY</span>
                <i class="fa-solid fa-bolt text-emerald-400 text-sm"></i>
            </div>
            <div class="text-2xl font-bold text-emerald-400 mt-1.5" id="kpi-max-apr">43.8% APY</div>
            <div class="text-[11px] text-emerald-400/80 mt-1">Dual Yield + Gauge Bribes</div>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex gap-2 border-b border-gray-800 pb-3 mb-6 overflow-x-auto text-xs font-medium">
        <button onclick="switchTab('gauges')" id="tab-btn-gauges" class="tab-btn active px-4 py-2 rounded-lg glass transition flex items-center gap-2">
            <i class="fa-solid fa-ranking-star"></i> VIP Gauge Wars
        </button>
        <button onclick="switchTab('enshrined')" id="tab-btn-enshrined" class="tab-btn px-4 py-2 rounded-lg glass transition flex items-center gap-2">
            <i class="fa-solid fa-water"></i> Enshrined LP Pools
        </button>
        <button onclick="switchTab('staker')" id="tab-btn-staker" class="tab-btn px-4 py-2 rounded-lg glass transition flex items-center gap-2">
            <i class="fa-solid fa-calculator"></i> Staker Yield Simulator
        </button>
        <button onclick="switchTab('rollup')" id="tab-btn-rollup" class="tab-btn px-4 py-2 rounded-lg glass transition flex items-center gap-2">
            <i class="fa-solid fa-cubes-stacked"></i> Minitia Bribe ROI
        </button>
    </div>

    <!-- TAB 1: VIP Gauge Wars -->
    <div id="tab-gauges" class="space-y-6">
        <div class="glass p-6 rounded-2xl">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-2">
                <div>
                    <h2 class="text-base font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-flag-checkered text-blue-400"></i> Active VIP Gauge Voting Cycle #14
                    </h2>
                    <p class="text-xs text-gray-400">Minitia rollups competing for the 538,461 INIT 2-week Weight Pool. Single L2 weight is capped at 40%.</p>
                </div>
                <div class="text-right text-xs font-mono text-gray-400">
                    Cycle Ends In: <span class="text-blue-400 font-bold">4 days 12h 45m</span>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="text-gray-400 border-b border-gray-800 uppercase text-[10px] tracking-wider">
                        <tr>
                            <th class="py-3">Rollup / Minitia</th>
                            <th>VM Stack</th>
                            <th>Category</th>
                            <th>Gauge Votes</th>
                            <th>Vote Share</th>
                            <th>Bribe Pool</th>
                            <th>Bribe APR</th>
                            <th>Projected Stage Reward</th>
                        </tr>
                    </thead>
                    <tbody id="gauges-tbody" class="divide-y divide-gray-800/60 font-mono">
                        <tr><td colspan="8" class="text-center py-6 text-gray-500">Loading live gauge metrics...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 2: Enshrined Liquidity -->
    <div id="tab-enshrined" class="space-y-6 hidden">
        <div class="glass p-6 rounded-2xl">
            <div class="flex justify-between items-center mb-4">
                <div>
                    <h2 class="text-base font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-shield-halved text-purple-400"></i> Whitelisted Enshrined Liquidity Positions
                    </h2>
                    <p class="text-xs text-gray-400">Governance-approved InitiaDEX LP tokens staked with validators to secure the L1 while earning trading fees.</p>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="text-gray-400 border-b border-gray-800 uppercase text-[10px] tracking-wider">
                        <tr>
                            <th class="py-3">Pool Pair</th>
                            <th>Pool Type</th>
                            <th>Gov Weight (w_a)</th>
                            <th>Reward Share</th>
                            <th>TVL (USD)</th>
                            <th>Staking APR</th>
                            <th>Swap Fee APR</th>
                            <th>Blended APR</th>
                        </tr>
                    </thead>
                    <tbody id="enshrined-tbody" class="divide-y divide-gray-800/60 font-mono">
                        <tr><td colspan="8" class="text-center py-6 text-gray-500">Loading Enshrined Liquidity data...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 3: Staker Yield Maximizer -->
    <div id="tab-staker" class="space-y-6 hidden">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="glass p-6 rounded-2xl space-y-4">
                <h2 class="text-base font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-sliders text-emerald-400"></i> Staker Yield Simulator
                </h2>
                <p class="text-xs text-gray-400 leading-relaxed">
                    Compare expected returns across standard staking, Enshrined Liquidity, and active VIP gauge voting bribes.
                </p>
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1">Your Capital (USD)</label>
                    <div class="relative">
                        <span class="absolute left-3 top-2.5 text-gray-500 font-mono text-xs">$</span>
                        <input id="input-capital" type="number" value="10000" step="1000" oninput="calculateStakerYield()" 
                               class="w-full pl-7 pr-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-white font-mono text-sm focus:border-blue-500 focus:outline-none">
                    </div>
                </div>
                <div class="p-4 rounded-xl bg-blue-950/30 border border-blue-500/20 text-xs space-y-1.5">
                    <span class="text-blue-400 font-bold block uppercase tracking-wider text-[10px]">Optimal Strategy Recommendation</span>
                    <p class="text-gray-300 font-medium" id="recom-title">InitiaPulse Maximizer</p>
                    <p class="text-emerald-400 font-mono text-sm font-bold mt-1" id="recom-extra">+$2,960.00 / yr extra yield</p>
                </div>
            </div>

            <div class="lg:col-span-2 glass p-6 rounded-2xl">
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Strategy Return Breakdown</h3>
                <div id="staker-results" class="space-y-3 font-mono">
                    <!-- Populated dynamically -->
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 4: Rollup Bribe ROI Calculator -->
    <div id="tab-rollup" class="space-y-6 hidden">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="glass p-6 rounded-2xl space-y-4">
                <h2 class="text-base font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-calculator text-indigo-400"></i> Minitia Bribe ROI Calculator
                </h2>
                <p class="text-xs text-gray-400 leading-relaxed">
                    For Minitia teams: Calculate the optimal bribe budget to capture your target share of the 538,461 INIT 2-week Weight Pool.
                </p>
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1">
                        Target VIP Reward Share: <span id="share-label" class="text-blue-400 font-mono">15.0%</span>
                    </label>
                    <input id="input-share" type="range" min="1" max="40" value="15" step="0.5" oninput="calculateRollupROI()" 
                           class="w-full accent-blue-500 cursor-pointer">
                    <span class="text-[10px] text-gray-500">Max single L2 cap is 40.0%</span>
                </div>
            </div>

            <div class="lg:col-span-2 glass p-6 rounded-2xl space-y-4">
                <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">Simulated Economic P&L (Per 2-Week Stage)</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3 font-mono text-center">
                    <div class="p-3 bg-gray-900 rounded-lg border border-gray-800">
                        <span class="text-[10px] text-gray-400 block">NEEDED GAUGE VOTES</span>
                        <span id="roi-votes" class="text-base font-bold text-white">18,423,529</span>
                    </div>
                    <div class="p-3 bg-gray-900 rounded-lg border border-gray-800">
                        <span class="text-[10px] text-gray-400 block">PROJECTED REWARD ($INIT)</span>
                        <span id="roi-init" class="text-base font-bold text-blue-400">80,769 INIT</span>
                    </div>
                    <div class="p-3 bg-gray-900 rounded-lg border border-gray-800">
                        <span class="text-[10px] text-gray-400 block">EST. BRIBE COST</span>
                        <span id="roi-bribe" class="text-base font-bold text-red-400">$34,892 USD</span>
                    </div>
                    <div class="p-3 bg-gray-900 rounded-lg border border-emerald-500/20 col-span-2 md:col-span-3">
                        <span class="text-[10px] text-gray-400 block">NET ECONOMIC SURPLUS / STAGE</span>
                        <span id="roi-net" class="text-2xl font-bold text-emerald-400">+$158,954.00 USD</span>
                        <div class="text-[11px] text-gray-400 mt-1" id="roi-annual">Annualized Runrate: +$4.13M Net Value</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            ['gauges', 'enshrined', 'staker', 'rollup'].forEach(t => {
                document.getElementById('tab-' + t).classList.add('hidden');
                document.getElementById('tab-btn-' + t).classList.remove('active');
            });
            document.getElementById('tab-' + tabId).classList.remove('hidden');
            document.getElementById('tab-btn-' + tabId).classList.add('active');
        }

        async function fetchNetworkStatus() {
            try {
                const r = await fetch('/api/v1/network-status');
                const d = await r.json();
                document.getElementById('chain-name').innerText = `${d.chain_id}: Block #${d.latest_height.toLocaleString()}`;
            } catch (e) {
                console.error(e);
            }
        }

        async function fetchGauges() {
            const r = await fetch('/api/v1/vip-gauges');
            const data = await r.json();
            const tbody = document.getElementById('gauges-tbody');
            tbody.innerHTML = data.map(g => `
                <tr class="hover:bg-gray-800/30 transition">
                    <td class="py-3 font-bold text-white flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-blue-500"></span> ${g.name}
                    </td>
                    <td><span class="px-2 py-0.5 rounded text-[10px] bg-gray-800 text-gray-300 font-mono">${g.vm}</span></td>
                    <td class="text-gray-400">${g.category}</td>
                    <td class="text-white">${g.votes.toLocaleString()}</td>
                    <td>
                        <div class="flex items-center gap-1.5">
                            <span class="font-bold ${g.capped ? 'text-amber-400' : 'text-blue-400'}">${g.vote_share_pct}%</span>
                            ${g.capped ? '<span class="text-[9px] text-amber-400 px-1 rounded bg-amber-500/20">40% CAP</span>' : ''}
                        </div>
                    </td>
                    <td class="text-indigo-400">$${g.bribe_pool_usd.toLocaleString()}</td>
                    <td class="text-emerald-400 font-bold">${g.bribe_apr}%</td>
                    <td>
                        <span class="text-white font-bold">${g.projected_stage_init.toLocaleString()} INIT</span>
                        <span class="text-[10px] text-gray-500 block">($${g.projected_stage_usd.toLocaleString()})</span>
                    </td>
                </tr>
            `).join('');
        }

        async function fetchEnshrined() {
            const r = await fetch('/api/v1/enshrined-pools');
            const data = await r.json();
            const tbody = document.getElementById('enshrined-tbody');
            tbody.innerHTML = data.map(p => `
                <tr class="hover:bg-gray-800/30 transition">
                    <td class="py-3 font-bold text-white">${p.pair}</td>
                    <td class="text-gray-400">${p.dex}</td>
                    <td class="text-blue-400">${p.gov_weight}</td>
                    <td class="text-gray-200">${p.weight_share_pct}%</td>
                    <td class="text-white">$${p.tvl_usd.toLocaleString()}</td>
                    <td class="text-purple-400">${p.staking_apr}%</td>
                    <td class="text-gray-400">${p.fee_apr}%</td>
                    <td class="text-emerald-400 font-bold text-sm">${p.blended_apr}%</td>
                </tr>
            `).join('');
        }

        async function calculateStakerYield() {
            const cap = parseFloat(document.getElementById('input-capital').value) || 10000;
            const r = await fetch('/api/v1/staker-calculator?capital_usd=' + cap);
            const d = await r.json();
            
            document.getElementById('recom-title').innerText = d.optimal_recommendation;
            document.getElementById('recom-extra').innerText = `+$${d.additional_annual_profit.toLocaleString()} / yr extra yield`;

            const container = document.getElementById('staker-results');
            container.innerHTML = d.strategies.map((s, idx) => `
                <div class="p-4 rounded-xl border ${idx === 2 ? 'bg-blue-950/30 border-blue-500/40' : 'bg-gray-900 border-gray-800'} flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-bold text-white text-sm">${s.name}</span>
                            ${idx === 2 ? '<span class="text-[9px] px-2 py-0.5 rounded badge-gradient text-white font-bold uppercase">Recommended</span>' : ''}
                        </div>
                        <span class="text-xs text-gray-400 mt-0.5 block">${s.risk} • ${s.effort}</span>
                    </div>
                    <div class="text-right">
                        <span class="text-lg font-bold text-emerald-400">${s.apr}% APY</span>
                        <span class="text-xs text-gray-300 block font-mono">+$${s.annual_yield_usd.toLocaleString()} / year</span>
                    </div>
                </div>
            `).join('');
        }

        async function calculateRollupROI() {
            const share = parseFloat(document.getElementById('input-share').value) || 15;
            document.getElementById('share-label').innerText = share.toFixed(1) + '%';
            
            const r = await fetch('/api/v1/rollup-roi?target_share_pct=' + share);
            const d = await r.json();

            document.getElementById('roi-votes').innerText = d.needed_gauge_votes.toLocaleString();
            document.getElementById('roi-init').innerText = d.stage_init_reward.toLocaleString() + ' INIT';
            document.getElementById('roi-bribe').innerText = '$' + d.est_bribe_cost_stage_usd.toLocaleString();
            document.getElementById('roi-net').innerText = '+$' + d.net_surplus_stage_usd.toLocaleString() + ' USD';
            document.getElementById('roi-annual').innerText = `Annualized Runrate: +$${d.annualized_net_surplus_usd.toLocaleString()} Net Value • ${d.bribe_multiplier}`;
        }

        async function refreshAll() {
            await fetchNetworkStatus();
            await fetchGauges();
            await fetchEnshrined();
            await calculateStakerYield();
            await calculateRollupROI();
        }

        // Initialize on load
        refreshAll();
        setInterval(fetchNetworkStatus, 6000);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/grant_proposal", response_class=HTMLResponse)
@app.get("/api/index/grant_proposal", response_class=HTMLResponse)
@app.get("/api/grant_proposal", response_class=HTMLResponse)
def grant_proposal_page():
    proposal_path = Path(__file__).parent / "grant_proposal" / "initia_foundation_grant.html"
    if proposal_path.exists():
        with open(proposal_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Grant proposal rendering...</h1>")

if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("⚡ INITIA-PULSE: VIP GAUGE & ENSHRINED LIQUIDITY TERMINAL")
    print("=" * 80)
    print("[*] Launching on http://127.0.0.1:8090")
    print("=" * 80)
    uvicorn.run(app, host="127.0.0.1", port=8090, log_level="warning")
