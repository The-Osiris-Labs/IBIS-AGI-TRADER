#!/usr/bin/env python3
"""
🦅 IBIS SYSTEM HEALTH CHECK
============================
Comprehensive validation of system configuration and positions.
Run this to ensure all components are coherent and properly configured.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from ibis.core.trading_constants import TRADING


class SystemHealthCheck:
    """Validates IBIS system health and configuration coherence"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def log_error(self, msg: str):
        self.errors.append(f"❌ {msg}")
        
    def log_warning(self, msg: str):
        self.warnings.append(f"⚠️  {msg}")
        
    def log_info(self, msg: str):
        self.info.append(f"✅ {msg}")
        
    def check_configuration(self) -> bool:
        """Validate configuration values"""
        print("\n📋 CONFIGURATION CHECK")
        print("=" * 50)
        
        # Check TP/SL ratio
        tp = TRADING.RISK.TAKE_PROFIT_PCT
        sl = TRADING.RISK.STOP_LOSS_PCT
        
        if tp <= 0 or sl <= 0:
            self.log_error(f"Invalid TP/SL values: TP={tp}, SL={sl}")
            return False
            
        rr_ratio = tp / sl if sl > 0 else 0
        self.log_info(f"Risk/Reward Ratio: 1:{rr_ratio:.2f} (TP: {tp*100:.1f}%, SL: {sl*100:.1f}%)")
        
        if rr_ratio < 0.5:
            self.log_warning(f"Risk/Reward ratio {rr_ratio:.2f} is unfavorable (need 4 wins per loss)")
        elif rr_ratio < 1.0:
            self.log_info(f"Risk/Reward ratio {rr_ratio:.2f} is acceptable but not ideal")
        else:
            self.log_info(f"Risk/Reward ratio {rr_ratio:.2f} is excellent (1:1 or better)")
            
        # Check score threshold
        min_score = TRADING.SCORE.MIN_THRESHOLD
        if min_score < 50:
            self.log_warning(f"Score threshold {min_score} may be too low (too many trades)")
        elif min_score > 85:
            self.log_warning(f"Score threshold {min_score} may be too high (too few trades)")
        else:
            self.log_info(f"Score threshold {min_score} is reasonable")
            
        # Check position sizing
        min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE
        base_pct = TRADING.POSITION.BASE_POSITION_PCT
        
        if min_trade < 5:
            self.log_warning(f"Min trade ${min_trade} may be too small (dust risk)")
        else:
            self.log_info(f"Min trade ${min_trade} is appropriate")
            
        self.log_info(f"Base position: {base_pct}% of capital")
        
        return len(self.errors) == 0
        
    def check_positions(self) -> bool:
        """Validate existing positions"""
        print("\n📊 POSITION VALIDATION")
        print("=" * 50)
        
        state_file = Path("data/ibis_true_state.json")
        if not state_file.exists():
            self.log_error("State file not found: data/ibis_true_state.json")
            return False
            
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except Exception as e:
            self.log_error(f"Failed to load state: {e}")
            return False
            
        positions = state.get('positions', {})
        if not positions:
            self.log_info("No active positions")
            return True
            
        expected_tp = TRADING.RISK.TAKE_PROFIT_PCT
        expected_sl = TRADING.RISK.STOP_LOSS_PCT
        
        issues_found = 0
        
        for symbol, pos in positions.items():
            entry = pos.get('buy_price', 0)
            tp = pos.get('tp', 0)
            sl = pos.get('sl', 0)
            
            if entry <= 0:
                self.log_error(f"{symbol}: Invalid entry price ${entry}")
                issues_found += 1
                continue
                
            actual_tp_pct = (tp - entry) / entry if tp > entry else 0
            actual_sl_pct = (entry - sl) / entry if sl < entry else 0
            
            # Check if TP matches expected
            tp_diff = abs(actual_tp_pct - expected_tp)
            sl_diff = abs(actual_sl_pct - expected_sl)
            
            if tp_diff > 0.001:  # 0.1% tolerance
                self.log_warning(
                    f"{symbol}: TP mismatch! Expected {expected_tp*100:.1f}%, "
                    f"actual {actual_tp_pct*100:.1f}% (diff: {tp_diff*100:.1f}%)"
                )
                issues_found += 1
            else:
                self.log_info(f"{symbol}: TP correct at {actual_tp_pct*100:.1f}%")
                
            if sl_diff > 0.001:
                self.log_warning(
                    f"{symbol}: SL mismatch! Expected {expected_sl*100:.1f}%, "
                    f"actual {actual_sl_pct*100:.1f}% (diff: {sl_diff*100:.1f}%)"
                )
                issues_found += 1
            else:
                self.log_info(f"{symbol}: SL correct at {actual_sl_pct*100:.1f}%")
                
        if issues_found == 0:
            self.log_info(f"All {len(positions)} positions validated successfully")
            
        return issues_found == 0
        
    def check_capital(self) -> bool:
        """Validate capital allocation"""
        print("\n💰 CAPITAL CHECK")
        print("=" * 50)
        
        state_file = Path("data/ibis_true_state.json")
        if not state_file.exists():
            return False
            
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except:
            return False
            
        capital = state.get('capital_awareness', {})
        
        total = capital.get('total_assets', 0)
        available = capital.get('usdt_available', 0)
        locked = capital.get('usdt_locked_buy', 0)
        positions_value = capital.get('holdings_value', 0)
        
        if total <= 0:
            self.log_error("No capital detected!")
            return False
            
        self.log_info(f"Total Assets: ${total:.2f}")
        self.log_info(f"Available: ${available:.2f} ({available/total*100:.1f}%)")
        self.log_info(f"In Positions: ${positions_value:.2f} ({positions_value/total*100:.1f}%)")
        self.log_info(f"Locked in Orders: ${locked:.2f} ({locked/total*100:.1f}%)")
        
        # Check allocation
        allocation_pct = (positions_value + locked) / total * 100
        if allocation_pct > 90:
            self.log_warning(f"High allocation: {allocation_pct:.1f}% (limited flexibility)")
        elif allocation_pct < 10:
            self.log_warning(f"Low allocation: {allocation_pct:.1f}% (may be missing opportunities)")
        else:
            self.log_info(f"Allocation: {allocation_pct:.1f}% (healthy)")
            
        return True
        
    def run_all_checks(self) -> Tuple[bool, List[str]]:
        """Run all health checks and return results"""
        print("\n" + "=" * 60)
        print("🦅 IBIS SYSTEM HEALTH CHECK")
        print("=" * 60)
        
        config_ok = self.check_configuration()
        positions_ok = self.check_positions()
        capital_ok = self.check_capital()
        
        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        
        for info in self.info:
            print(info)
            
        for warning in self.warnings:
            print(warning)
            
        for error in self.errors:
            print(error)
            
        all_ok = config_ok and positions_ok and capital_ok and len(self.errors) == 0
        
        print("\n" + "=" * 60)
        if all_ok and len(self.warnings) == 0:
            print("🎉 SYSTEM HEALTH: EXCELLENT")
        elif all_ok:
            print("⚠️  SYSTEM HEALTH: GOOD (with warnings)")
        else:
            print("❌ SYSTEM HEALTH: ISSUES DETECTED")
        print("=" * 60)
        
        return all_ok, self.errors + self.warnings


def main():
    """Run health check from command line"""
    checker = SystemHealthCheck()
    healthy, issues = checker.run_all_checks()
    
    if not healthy:
        print("\n🔧 RECOMMENDED ACTIONS:")
        for issue in issues:
            print(f"   {issue}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
