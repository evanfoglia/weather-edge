#!/usr/bin/env python3
"""
Weather Arbitrage Simulation

Simulates trading with a $1000 account using realistic scenarios.
Since actual opportunities are rare and timing-dependent, this simulation
demonstrates what would happen when opportunities DO appear.

Run: python -m src.simulation
"""
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

@dataclass
class SimulatedTrade:
    timestamp: datetime
    city: str
    ticker: str
    action: str
    entry_price: float  # Price paid (0-1)
    edge: float  # Expected edge
    contracts: int
    cost: float
    payout: float
    profit: float
    certainty: str

def run_simulation(
    starting_balance: float = 1000.0,
    days: int = 30,
    opportunities_per_day: float = 0.5,  # Realistic: ~1 opportunity every 2 days
    max_position_pct: float = 0.10  # Max 10% of balance per trade
):
    """
    Simulate weather arbitrage trading.
    
    Based on realistic assumptions:
    - Opportunities are rare (maybe 0-2 per day across all cities)
    - When threshold is crossed, edge is typically 1-10%
    - Not all opportunities get filled (liquidity constraints)
    """
    print("=" * 70)
    print("🌤️  WEATHER ARBITRAGE SIMULATION")
    print("=" * 70)
    print(f"Starting Balance: ${starting_balance:,.2f}")
    print(f"Simulation Period: {days} days")
    print(f"Expected Opportunities: ~{opportunities_per_day}/day")
    print(f"Max Position Size: {max_position_pct*100:.0f}% of balance")
    print("=" * 70)
    print()
    
    balance = starting_balance
    trades: List[SimulatedTrade] = []
    cities = ["NYC", "Chicago", "Miami"]
    
    # Simulate each day
    start_date = datetime.now()
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Random number of opportunities (Poisson-like distribution)
        num_opps = 0
        if random.random() < opportunities_per_day:
            num_opps = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]
        
        for _ in range(num_opps):
            # Simulate an opportunity
            city = random.choice(cities)
            
            # Edge distribution (realistic: usually small, occasionally larger)
            edge = random.choices(
                [0.02, 0.03, 0.05, 0.08, 0.10, 0.15],
                weights=[0.3, 0.25, 0.2, 0.15, 0.07, 0.03]
            )[0]
            
            # Entry price (if edge is 5%, we're buying at ~94-95 cents)
            entry_price = 0.99 - edge
            
            # Position sizing: use max_position_pct of current balance
            max_position = balance * max_position_pct
            contracts = int(max_position / entry_price)
            
            if contracts < 1:
                continue  # Balance too low
            
            # Cost and expected payout
            cost = contracts * entry_price
            
            # Simulate execution: 90% of trades execute successfully
            if random.random() > 0.90:
                continue  # Didn't get filled (liquidity issue)
            
            # These are "certain" trades (threshold already crossed)
            # Win rate should be ~99% (rarely the data source is wrong)
            if random.random() < 0.99:
                payout = contracts * 1.0  # $1 per contract
                profit = payout - cost
                balance += profit
            else:
                # Rare loss (data discrepancy, settlement dispute, etc.)
                payout = 0
                profit = -cost
                balance -= cost
            
            trade = SimulatedTrade(
                timestamp=current_date,
                city=city,
                ticker=f"KX{city[:3].upper()}-{current_date.strftime('%d%b').upper()}",
                action="BUY_YES",
                entry_price=entry_price,
                edge=edge,
                contracts=contracts,
                cost=cost,
                payout=payout,
                profit=profit,
                certainty="CERTAIN"
            )
            trades.append(trade)
            
            # Log the trade
            result = "✅ WIN" if profit > 0 else "❌ LOSS"
            print(f"Day {day+1:2d} | {city:8s} | {result} | "
                  f"Edge: {edge*100:4.1f}% | "
                  f"Contracts: {contracts:3d} | "
                  f"Profit: ${profit:+7.2f} | "
                  f"Balance: ${balance:,.2f}")
    
    # Summary
    print()
    print("=" * 70)
    print("📊 SIMULATION SUMMARY")
    print("=" * 70)
    
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.profit > 0)
    total_profit = balance - starting_balance
    roi = (total_profit / starting_balance) * 100
    
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {winning_trades}/{total_trades} ({winning_trades/max(total_trades,1)*100:.1f}%)")
    print(f"Starting Balance: ${starting_balance:,.2f}")
    print(f"Ending Balance: ${balance:,.2f}")
    print(f"Total Profit: ${total_profit:+,.2f}")
    print(f"ROI: {roi:+.1f}%")
    print(f"Avg Profit/Trade: ${total_profit/max(total_trades,1):+.2f}")
    print()
    
    # Risk-adjusted metrics
    if trades:
        avg_edge = sum(t.edge for t in trades) / len(trades)
        print(f"Average Edge: {avg_edge*100:.1f}%")
    
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT CAVEATS:")
    print("   - Real opportunities may be rarer than simulated")
    print("   - Liquidity constraints may limit position sizes")
    print("   - Market efficiency means edges may be smaller")
    print("   - This simulation assumes 'certain' (threshold crossed) trades only")
    print()
    
    return balance, trades


if __name__ == "__main__":
    # Run with $1000 starting balance, 30 day simulation
    final_balance, trades = run_simulation(
        starting_balance=1000.0,
        days=30,
        opportunities_per_day=0.5,  # Conservative estimate
        max_position_pct=0.10
    )
