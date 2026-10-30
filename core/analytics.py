"""
InitiaPulse Core Analytics Engine
Implements the exact mathematical formulas for:
1. Enshrined Liquidity (EL) distribution: r_a = (w_a * r_total) / sum(w_i)
2. Vested Interest Program (VIP) 2-week stage distributions & Gauge Weights
3. Staker Yield Optimization (Pure INIT Staking vs. Enshrined LP Staking vs. VIP Voting)
4. Rollup Bribe ROI Calculator (Cost per gauge vote vs. VIP reward capture)
"""

from typing import Dict, Any, List
import time

class InitiaAnalyticsEngine:
    def __init__(self):
        # Global Initia Tokenomics Constants
        self.TOTAL_SUPPLY = 1_000_000_000.0  # 1B fixed
        self.EL_TOTAL_ALLOCATION = 250_000_000.0  # 25% Enshrined Liquidity
        self.VIP_TOTAL_ALLOCATION = 250_000_000.0  # 25% VIP
        
        # Annual Emissions
        self.EL_ANNUAL_EMISSION = 12_500_000.0  # 5% of 250M
        self.VIP_ANNUAL_EMISSION = 17_500_000.0  # 7% of 250M
        
        # VIP Stage Constants
        self.STAGES_PER_YEAR = 26  # 2-week intervals
        self.VIP_STAGE_TOTAL = self.VIP_ANNUAL_EMISSION / self.STAGES_PER_YEAR  # ~673,077 INIT
        self.POOL_SPLIT_RATIO = 0.20  # 20% to balance pool
        self.WEIGHT_POOL_PER_STAGE = self.VIP_STAGE_TOTAL * (1.0 - self.POOL_SPLIT_RATIO)  # ~538,461 INIT
        self.BALANCE_POOL_PER_STAGE = self.VIP_STAGE_TOTAL * self.POOL_SPLIT_RATIO  # ~134,615 INIT
        self.MAX_ROLLUP_WEIGHT_RATIO = 0.40  # 40% cap per single L2

        # Benchmark INIT Price Estimate (Conservative / Dynamic)
        self.init_price_usd = 2.40

    def get_tokenomics_overview(self) -> Dict[str, Any]:
        return {
            "total_supply": self.TOTAL_SUPPLY,
            "circulating_pct": "12.0%",
            "init_price_usd": self.init_price_usd,
            "market_cap_est": self.TOTAL_SUPPLY * 0.12 * self.init_price_usd,
            "fdv_est": self.TOTAL_SUPPLY * self.init_price_usd,
            "enshrined_liquidity": {
                "total_allocation": self.EL_TOTAL_ALLOCATION,
                "annual_emission": self.EL_ANNUAL_EMISSION,
                "annual_emission_usd": self.EL_ANNUAL_EMISSION * self.init_price_usd,
                "daily_emission": self.EL_ANNUAL_EMISSION / 365.0
            },
            "vip_rewards": {
                "total_allocation": self.VIP_TOTAL_ALLOCATION,
                "annual_emission": self.VIP_ANNUAL_EMISSION,
                "annual_emission_usd": self.VIP_ANNUAL_EMISSION * self.init_price_usd,
                "stage_interval_days": 14,
                "weight_pool_per_stage": self.WEIGHT_POOL_PER_STAGE,
                "weight_pool_usd_per_stage": self.WEIGHT_POOL_PER_STAGE * self.init_price_usd
            }
        }

    def get_enshrined_pools(self) -> List[Dict[str, Any]]:
        """
        Calculates r_a = (w_a * r_total) / sum(w_i) for whitelisted InitiaDEX pools.
        """
        raw_pools = [
            {"id": "pool-init-usdc", "pair": "INIT-USDC", "dex": "InitiaDEX (Balancer 50/50)", "weight": 40.0, "tvl_usd": 18_500_000.0, "swap_fee_24h_usd": 12_400.0},
            {"id": "pool-init-eth", "pair": "INIT-ETH", "dex": "InitiaDEX (Balancer 60/40)", "weight": 25.0, "tvl_usd": 14_200_000.0, "swap_fee_24h_usd": 8_900.0},
            {"id": "pool-init-tia", "pair": "INIT-TIA", "dex": "InitiaDEX (Balancer 50/50)", "weight": 15.0, "tvl_usd": 7_800_000.0, "swap_fee_24h_usd": 4_200.0},
            {"id": "pool-init-tuc", "pair": "INIT-TUC", "dex": "InitiaDEX (Balancer 50/50)", "weight": 12.0, "tvl_usd": 5_400_000.0, "swap_fee_24h_usd": 3_100.0},
            {"id": "pool-init-bkw", "pair": "INIT-BKW", "dex": "InitiaDEX (Balancer 50/50)", "weight": 8.0, "tvl_usd": 3_600_000.0, "swap_fee_24h_usd": 2_200.0},
        ]
        total_weight = sum(p["weight"] for p in raw_pools)
        
        pools = []
        for p in raw_pools:
            share = p["weight"] / total_weight
            annual_init_rewards = self.EL_ANNUAL_EMISSION * share
            annual_reward_usd = annual_init_rewards * self.init_price_usd
            annual_swap_fees_usd = p["swap_fee_24h_usd"] * 365.0
            total_annual_yield_usd = annual_reward_usd + annual_swap_fees_usd
            
            staking_apr = (annual_reward_usd / p["tvl_usd"]) * 100.0 if p["tvl_usd"] > 0 else 0.0
            fee_apr = (annual_swap_fees_usd / p["tvl_usd"]) * 100.0 if p["tvl_usd"] > 0 else 0.0
            blended_apr = staking_apr + fee_apr

            pools.append({
                "id": p["id"],
                "pair": p["pair"],
                "dex": p["dex"],
                "gov_weight": p["weight"],
                "weight_share_pct": round(share * 100.0, 2),
                "tvl_usd": p["tvl_usd"],
                "annual_init_rewards": round(annual_init_rewards, 0),
                "staking_apr": round(staking_apr, 2),
                "fee_apr": round(fee_apr, 2),
                "blended_apr": round(blended_apr, 2)
            })
        return pools

    def get_vip_gauges(self) -> List[Dict[str, Any]]:
        """
        VIP Gauge weight distributions and projected INIT rewards per 2-week cycle.
        """
        rollups = [
            {"id": "tucana", "name": "Tucana Network", "vm": "MiniEVM", "category": "DEX & Perps", "votes": 34_500_000, "active_users": 18_400, "bribe_pool_usd": 125_000.0},
            {"id": "blackwing", "name": "Blackwing", "vm": "MiniWasm", "category": "Modular Margin Trading", "votes": 28_200_000, "active_users": 14_100, "bribe_pool_usd": 90_000.0},
            {"id": "milkyway", "name": "MilkyWay Rollup", "vm": "MiniMove", "category": "Liquid Staking", "votes": 19_800_000, "active_users": 9_800, "bribe_pool_usd": 65_000.0},
            {"id": "lunch", "name": "Lunch App", "vm": "MiniEVM", "category": "Web3 Social & Loyalty", "votes": 12_500_000, "active_users": 22_500, "bribe_pool_usd": 35_000.0},
            {"id": "initia-native", "name": "Civitia / Gaming Minitia", "vm": "MiniMove", "category": "Strategy Gaming", "votes": 9_400_000, "active_users": 31_000, "bribe_pool_usd": 20_000.0},
        ]
        total_votes = sum(r["votes"] for r in rollups)

        gauges = []
        for r in rollups:
            raw_weight = r["votes"] / total_votes
            # Enforce maximum_weight_ratio = 40% cap
            effective_weight = min(raw_weight, self.MAX_ROLLUP_WEIGHT_RATIO)
            
            stage_init_reward = self.WEIGHT_POOL_PER_STAGE * effective_weight
            stage_usd_reward = stage_init_reward * self.init_price_usd
            
            # Bribe ROI for staker: (Bribe USD / Vote Cost) annualized
            vote_value_usd = r["votes"] * self.init_price_usd
            bribe_apr = (r["bribe_pool_usd"] * (self.STAGES_PER_YEAR) / vote_value_usd) * 100.0 if vote_value_usd > 0 else 0.0

            gauges.append({
                "id": r["id"],
                "name": r["name"],
                "vm": r["vm"],
                "category": r["category"],
                "votes": r["votes"],
                "vote_share_pct": round(raw_weight * 100.0, 2),
                "capped": raw_weight > self.MAX_ROLLUP_WEIGHT_RATIO,
                "active_users": r["active_users"],
                "bribe_pool_usd": r["bribe_pool_usd"],
                "bribe_apr": round(bribe_apr, 2),
                "projected_stage_init": round(stage_init_reward, 0),
                "projected_stage_usd": round(stage_usd_reward, 2),
                "annual_runrate_usd": round(stage_usd_reward * self.STAGES_PER_YEAR, 2)
            })
        return gauges

    def calculate_staker_strategy(self, capital_usd: float) -> Dict[str, Any]:
        """
        Optimal yield router for a staker holding $INIT or USD capital.
        Compares:
        1. Pure INIT Validator Staking
        2. Enshrined LP Staking (e.g. INIT-USDC)
        3. Enshrined LP + Active VIP Gauge Voting (Bribe Maximizer)
        """
        pure_init_apr = 14.2  # Base inflation staking APR
        
        # Enshrined LP (INIT-USDC top pool)
        el_pools = self.get_enshrined_pools()
        top_el = el_pools[0]
        el_apr = top_el["blended_apr"]
        
        # Bribe maximization from VIP gauges
        gauges = self.get_vip_gauges()
        top_bribe = max(gauges, key=lambda g: g["bribe_apr"])
        bribe_boost_apr = top_bribe["bribe_apr"]
        
        combined_max_apr = el_apr + (bribe_boost_apr * 0.75)  # Weighted voting power factor

        return {
            "capital_usd": capital_usd,
            "strategies": [
                {
                    "name": "Passive L1 INIT Staking",
                    "apr": pure_init_apr,
                    "annual_yield_usd": round(capital_usd * (pure_init_apr / 100.0), 2),
                    "risk": "Low (Standard 21-day unbonding, no impermanent loss)",
                    "effort": "Zero (Stake & Forget)"
                },
                {
                    "name": "Enshrined Liquidity Staking (INIT-USDC)",
                    "apr": el_apr,
                    "annual_yield_usd": round(capital_usd * (el_apr / 100.0), 2),
                    "risk": "Low-Medium (50/50 Balancer Pool, minimal IL, earns dual staking + swap fees)",
                    "effort": "Low"
                },
                {
                    "name": "InitiaPulse Maximizer (EL Staking + VIP Gauge Bribes)",
                    "apr": round(combined_max_apr, 2),
                    "annual_yield_usd": round(capital_usd * (combined_max_apr / 100.0), 2),
                    "risk": "Low-Medium (Dual yield + Minitia ecosystem tokens/bribes)",
                    "effort": "Automated via InitiaPulse"
                }
            ],
            "optimal_recommendation": "InitiaPulse Maximizer",
            "additional_annual_profit": round(capital_usd * ((combined_max_apr - pure_init_apr) / 100.0), 2)
        }

    def calculate_rollup_roi(self, target_reward_share_pct: float, current_total_votes: int = 104_400_000) -> Dict[str, Any]:
        """
        Calculates how much a Minitia rollup team needs to spend in bribes
        to capture their target percentage of the VIP Weight Pool.
        """
        target_share = min(target_reward_share_pct / 100.0, self.MAX_ROLLUP_WEIGHT_RATIO)
        needed_votes = int((target_share / (1.0 - target_share)) * current_total_votes)
        
        # Stage reward capture
        stage_init_captured = self.WEIGHT_POOL_PER_STAGE * target_share
        stage_usd_captured = stage_init_captured * self.init_price_usd
        
        # Benchmark market bribe efficiency: ~0.15 USD in bribe per 1.00 USD of reward capture
        est_bribe_cost_stage = stage_usd_captured * 0.18
        net_profit_to_rollup_stage = stage_usd_captured - est_bribe_cost_stage
        
        return {
            "target_reward_share_pct": round(target_share * 100.0, 2),
            "needed_gauge_votes": needed_votes,
            "stage_init_reward": round(stage_init_captured, 0),
            "stage_usd_reward": round(stage_usd_captured, 2),
            "est_bribe_cost_stage_usd": round(est_bribe_cost_stage, 2),
            "net_surplus_stage_usd": round(net_profit_to_rollup_stage, 2),
            "annualized_net_surplus_usd": round(net_profit_to_rollup_stage * self.STAGES_PER_YEAR, 2),
            "bribe_multiplier": "5.5x (Every $1 in bribe captures ~$5.55 in $INIT VIP incentives)"
        }
