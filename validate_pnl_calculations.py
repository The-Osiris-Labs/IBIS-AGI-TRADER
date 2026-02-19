#!/usr/bin/env python3
"""
P&L Validation and Documentation System
========================================
Comprehensive validation, debugging, and documentation for P&L calculations.

This script provides a complete system for validating P&L calculations, identifying
errors, and ensuring consistency across all calculation methods.

Key Features:
- Validate trade history and trade data
- Verify P&L calculation consistency across methods
- Check fee calculation and tracking
- Debug and diagnose P&L calculation issues
- Generate comprehensive validation reports
"""

import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ibis.pnl_tracker import PnLTracker, ValidationError, CalculationError
from ibis.database.db import IbisDB
from ibis.core.risk_manager import risk_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("pnl_validation.log")],
)

logger = logging.getLogger(__name__)


class PnLValidationSystem:
    """Comprehensive P&L validation and documentation system"""

    def __init__(self, verbose: bool = False):
        """Initialize the validation system

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        self.tracker = PnLTracker()
        self.db = IbisDB()
        self.risk_manager = risk_manager
        self.risk_manager.set_database(self.db)

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "errors": [],
            "warnings": [],
            "validations": {},
            "summary": {},
        }

    def validate_trade_history(self) -> bool:
        """Validate trade history

        Returns:
            True if valid, False if errors
        """
        logger.info("Validating trade history...")

        try:
            validation_report = self.tracker.validate_trade_history()
            self.results["validations"]["trade_history"] = validation_report

            if validation_report["invalid_trades"] > 0:
                self.results["success"] = False
                self.results["errors"].extend(
                    [
                        f"Invalid trade {e['order_id']}: {', '.join(e['errors'])}"
                        for e in validation_report["errors"]
                    ]
                )

            if validation_report["duplicate_order_ids"]:
                for order_id in validation_report["duplicate_order_ids"]:
                    self.results["warnings"].append(f"Duplicate order ID: {order_id}")

            logger.info(
                f"Trade history validation: {validation_report['valid_trades']}/{validation_report['total_trades']} valid trades"
            )

            return validation_report["invalid_trades"] == 0

        except Exception as e:
            logger.error(f"Trade history validation failed: {e}")
            self.results["success"] = False
            self.results["errors"].append(f"Trade history validation: {str(e)}")
            return False

    def validate_matched_trades(self) -> bool:
        """Validate matched trades

        Returns:
            True if valid, False if errors
        """
        logger.info("Validating matched trades...")

        try:
            # Match trades with validation
            matched_trades = self.tracker.match_trades_fifo(validate=True)
            valid_count = 0

            for i, trade in enumerate(matched_trades):
                try:
                    errors = trade.validate()
                    if errors:
                        self.results["success"] = False
                        self.results["errors"].extend(
                            [
                                f"Matched trade {i}: buy={trade.buy_trade.order_id}, "
                                f"sell={trade.sell_trade.order_id} - {e}"
                                for e in errors
                            ]
                        )
                    else:
                        valid_count += 1

                except Exception as e:
                    self.results["success"] = False
                    self.results["errors"].append(f"Matched trade {i}: {str(e)}")

            self.results["validations"]["matched_trades"] = {
                "total": len(matched_trades),
                "valid": valid_count,
                "invalid": len(matched_trades) - valid_count,
            }

            logger.info(
                f"Matched trades validation: {valid_count}/{len(matched_trades)} valid matches"
            )

            return len(matched_trades) - valid_count == 0

        except ValidationError as e:
            logger.error(f"Trade matching failed: {e}")
            self.results["success"] = False
            self.results["errors"].extend([str(e)] + e.errors)
            return False
        except Exception as e:
            logger.error(f"Trade matching failed: {e}")
            self.results["success"] = False
            self.results["errors"].append(f"Trade matching: {str(e)}")
            return False

    def validate_fee_calculations(self) -> bool:
        """Validate fee calculations

        Returns:
            True if valid, False if errors
        """
        logger.info("Validating fee calculations...")

        try:
            # Test fee rate retrieval
            db_fees = self.db.get_average_fees_per_symbol(days=7)

            if db_fees:
                logger.info(f"Fee history available for {len(db_fees)} symbols")

                # Validate fee rates
                for symbol, fees in db_fees.items():
                    if fees["maker"] < 0 or fees["taker"] < 0:
                        self.results["success"] = False
                        self.results["errors"].append(
                            f"Negative fee rates for {symbol}: maker={fees['maker']:.4f}, taker={fees['taker']:.4f}"
                        )
                    if fees["maker"] > 0.05 or fees["taker"] > 0.05:
                        self.results["success"] = False
                        self.results["errors"].append(
                            f"Excessive fee rates for {symbol}: maker={fees['maker']:.4f}, taker={fees['taker']:.4f}"
                        )

                self.results["validations"]["fee_rates"] = db_fees

            # Test fee calculation from risk manager
            risk_fees = self.risk_manager._get_fee_rates("BTC")
            logger.debug(f"Risk manager fee rates: {risk_fees}")

            return True

        except Exception as e:
            logger.error(f"Fee calculation validation failed: {e}")
            self.results["success"] = False
            self.results["errors"].append(f"Fee calculation: {str(e)}")
            return False

    def validate_pnl_calculations(self) -> bool:
        """Validate P&L calculations

        Returns:
            True if valid, False if errors
        """
        logger.info("Validating P&L calculations...")

        try:
            # Calculate different time periods
            weekly = self.tracker.get_weekly_pnl()
            monthly = self.tracker.get_monthly_pnl()
            all_time = self.tracker.get_all_time_pnl()

            self.results["validations"]["pnl_calculations"] = {
                "weekly": weekly,
                "monthly": monthly,
                "all_time": all_time,
            }

            # Validate calculation consistency
            if weekly["trades"] > 0:
                weekly_total = weekly["pnl"]
                trades_total = sum(t["net_pnl"] for t in weekly["trades_detail"])
                if abs(weekly_total - trades_total) > 0.0001:
                    self.results["success"] = False
                    self.results["errors"].append(
                        f"Weekly P&L mismatch: calculated={weekly_total:.4f}, sum of trades={trades_total:.4f}"
                    )

            if monthly["trades"] > 0:
                monthly_total = monthly["pnl"]
                trades_total = sum(t["net_pnl"] for t in monthly["trades_detail"])
                if abs(monthly_total - trades_total) > 0.0001:
                    self.results["success"] = False
                    self.results["errors"].append(
                        f"Monthly P&L mismatch: calculated={monthly_total:.4f}, sum of trades={trades_total:.4f}"
                    )

            if all_time["trades"] > 0:
                all_time_total = all_time["pnl"]
                trades_total = sum(t["net_pnl"] for t in all_time["trades_detail"])
                if abs(all_time_total - trades_total) > 0.0001:
                    self.results["success"] = False
                    self.results["errors"].append(
                        f"All-time P&L mismatch: calculated={all_time_total:.4f}, sum of trades={trades_total:.4f}"
                    )

            logger.info("P&L calculations validated successfully")
            return True

        except Exception as e:
            logger.error(f"P&L calculation validation failed: {e}")
            self.results["success"] = False
            self.results["errors"].append(f"P&L calculation: {str(e)}")
            return False

    def generate_summary(self):
        """Generate validation summary"""
        summary = {
            "total_errors": len(self.results["errors"]),
            "total_warnings": len(self.results["warnings"]),
            "validations": len(self.results["validations"]),
        }

        # Add trade statistics
        if "trade_history" in self.results["validations"]:
            th = self.results["validations"]["trade_history"]
            summary["trade_history"] = {
                "total": th["total_trades"],
                "valid": th["valid_trades"],
                "invalid": th["invalid_trades"],
                "duplicates": len(th.get("duplicate_order_ids", [])),
            }

        if "matched_trades" in self.results["validations"]:
            mt = self.results["validations"]["matched_trades"]
            summary["matched_trades"] = {
                "total": mt["total"],
                "valid": mt["valid"],
                "invalid": mt["invalid"],
            }

        if "pnl_calculations" in self.results["validations"]:
            pnl = self.results["validations"]["pnl_calculations"]
            summary["pnl"] = {
                "weekly": {"pnl": pnl["weekly"]["pnl"], "trades": pnl["weekly"]["trades"]},
                "monthly": {"pnl": pnl["monthly"]["pnl"], "trades": pnl["monthly"]["trades"]},
                "all_time": {"pnl": pnl["all_time"]["pnl"], "trades": pnl["all_time"]["trades"]},
            }

        self.results["summary"] = summary

    def run_validation(self) -> dict:
        """Run complete validation

        Returns:
            Validation results dictionary
        """
        logger.info("Starting P&L validation...")

        # Run all validations
        self.validate_trade_history()
        self.validate_matched_trades()
        self.validate_fee_calculations()
        self.validate_pnl_calculations()

        # Generate summary
        self.generate_summary()

        # Log final result
        if self.results["success"]:
            logger.info("P&L validation completed successfully!")
        else:
            logger.error("P&L validation failed!")

        return self.results

    def print_report(self):
        """Print validation report"""
        print("=" * 80)
        print("P&L VALIDATION REPORT")
        print("=" * 80)
        print()

        print(f"Generated: {self.results['timestamp']}")
        print()

        # Summary
        print("SUMMARY:")
        print("-" * 40)
        print(f"Status: {'SUCCESS' if self.results['success'] else 'FAILED'}")
        print(f"Errors: {len(self.results['errors'])}")
        print(f"Warnings: {len(self.results['warnings'])}")
        print()

        # Trade history
        if "trade_history" in self.results["validations"]:
            th = self.results["validations"]["trade_history"]
            print("TRADE HISTORY:")
            print("-" * 40)
            print(f"Total trades: {th['total_trades']}")
            print(f"Valid trades: {th['valid_trades']}")
            print(f"Invalid trades: {th['invalid_trades']}")
            if th.get("duplicate_order_ids"):
                print(f"Duplicate order IDs: {len(th['duplicate_order_ids'])}")
            print()

        # Matched trades
        if "matched_trades" in self.results["validations"]:
            mt = self.results["validations"]["matched_trades"]
            print("MATCHED TRADES:")
            print("-" * 40)
            print(f"Total matches: {mt['total']}")
            print(f"Valid matches: {mt['valid']}")
            print(f"Invalid matches: {mt['invalid']}")
            print()

        # Errors
        if self.results["errors"]:
            print("ERRORS:")
            print("-" * 40)
            for error in self.results["errors"]:
                print(f"✗ {error}")
            print()

        # Warnings
        if self.results["warnings"]:
            print("WARNINGS:")
            print("-" * 40)
            for warning in self.results["warnings"]:
                print(f"⚠ {warning}")
            print()

        # P&L Summary
        if "pnl" in self.results["summary"]:
            pnl = self.results["summary"]["pnl"]
            print("P&L SUMMARY:")
            print("-" * 40)
            print(f"Weekly: ${pnl['weekly']['pnl']:.2f} ({pnl['weekly']['trades']} trades)")
            print(f"Monthly: ${pnl['monthly']['pnl']:.2f} ({pnl['monthly']['trades']} trades)")
            print(f"All Time: ${pnl['all_time']['pnl']:.2f} ({pnl['all_time']['trades']} trades)")

    def save_report(self, filename: str = "pnl_validation_report.json"):
        """Save validation report to file

        Args:
            filename: Output filename
        """
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"Report saved to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="P&L Validation and Documentation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script provides comprehensive validation of P&L calculations for the AGI Trader system.
It checks trade history validity, P&L calculation consistency, fee calculations, and
generates detailed validation reports.
        """,
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="pnl_validation_report.json",
        help="Output report filename (default: pnl_validation_report.json)",
    )

    parser.add_argument("-d", "--debug", type=str, help="Debug P&L calculation for specific symbol")

    args = parser.parse_args()

    logger.info("Initializing P&L Validation System...")

    # Initialize validation system
    validator = PnLValidationSystem(verbose=args.verbose)

    if args.debug:
        logger.info(f"Debugging P&L calculation for symbol: {args.debug}")
        debug_info = validator.tracker.debug_calculation(symbol=args.debug, detailed=True)

        print(json.dumps(debug_info, indent=2, default=str))

        # Check open positions
        open_positions = validator.tracker.get_open_positions()
        if open_positions:
            print("\nOPEN POSITIONS:")
            for pos in open_positions:
                if pos["symbol"] == args.debug:
                    print(json.dumps(pos, indent=2))

    else:
        # Run complete validation
        results = validator.run_validation()

        # Print report
        validator.print_report()

        # Save report
        validator.save_report(args.output)

        # Exit with appropriate code
        sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
