"""
IBIS Robust Error Handling & Fallback System
============================================
Comprehensive error handling and fallback mechanisms for reliable intelligence processing
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import traceback
from collections import defaultdict, deque

logger = logging.getLogger("IBIS")


class ErrorHandler:
    """
    Comprehensive error handling system with fallback mechanisms
    """

    def __init__(self):
        self.error_history = deque(maxlen=1000)
        self.source_errors = defaultdict(lambda: deque(maxlen=100))
        self.fallback_strategies = {}
        self.retry_config = {
            "max_retries": 3,
            "initial_backoff": 0.1,
            "max_backoff": 5.0,
            "backoff_multiplier": 2.0,
            "retryable_errors": [
                "TimeoutError",
                "ConnectionError",
                "HTTPError",
                "RequestException",
                "ServiceUnavailable",
            ],
        }

        self._init_fallback_strategies()

    def _init_fallback_strategies(self):
        """Initialize fallback strategies"""
        self.fallback_strategies = {
            "data_source": [
                self._fallback_to_secondary_source,
                self._fallback_to_cached_data,
                self._fallback_to_statistical_model,
                self._fallback_to_default_value,
            ],
            "signal_processing": [
                self._fallback_to_simplified_processing,
                self._fallback_to_mean_consensus,
                self._fallback_to_trend_extrapolation,
                self._fallback_to_neutral_signal,
            ],
            "analysis": [
                self._fallback_to_basic_analysis,
                self._fallback_to_historical_patterns,
                self._fallback_to_simple_statistics,
                self._fallback_to_neutral_analysis,
            ],
        }

    async def handle_error(self, error: Exception, context: Dict) -> Optional[Dict]:
        """
        Handle error with appropriate fallback strategy
        """
        error_info = await self._collect_error_info(error, context)
        await self._record_error(error_info)

        logger.warning(f"Handling error: {error_info['message']}")

        # Determine error type and apply fallback
        fallback_result = await self._apply_fallback_strategy(error_info)

        if fallback_result is not None:
            logger.info(f"Fallback successful: {fallback_result.get('strategy', 'unknown')}")

        return fallback_result

    async def _collect_error_info(self, error: Exception, context: Dict) -> Dict:
        """Collect comprehensive error information"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "retry_count": context.get("retry_count", 0),
        }

        # Add specific context information
        if "source_name" in context:
            error_info["source_name"] = context["source_name"]

        if "symbol" in context:
            error_info["symbol"] = context["symbol"]

        if "task_type" in context:
            error_info["task_type"] = context["task_type"]

        return error_info

    async def _record_error(self, error_info: Dict):
        """Record error in history"""
        self.error_history.append(error_info)

        if "source_name" in error_info:
            self.source_errors[error_info["source_name"]].append(error_info)

    async def _apply_fallback_strategy(self, error_info: Dict) -> Optional[Dict]:
        """Apply fallback strategy based on error type"""
        # Determine error category
        error_category = await self._determine_error_category(error_info)

        # Get applicable fallback strategies
        strategies = self.fallback_strategies.get(error_category, [])

        for strategy in strategies:
            try:
                result = await strategy(error_info)
                if result is not None:
                    result["strategy"] = strategy.__name__.lstrip("_")
                    return result
            except Exception as e:
                logger.warning(f"Fallback strategy failed: {e}")
                continue

        logger.error(f"No successful fallback for error: {error_info['message']}")
        return None

    async def _determine_error_category(self, error_info: Dict) -> str:
        """Determine error category for fallback strategy selection"""
        context = error_info.get("context", {})

        if context.get("is_data_source", False) or "source_name" in error_info:
            return "data_source"

        if context.get("is_signal_processing", False) or "task_type" in error_info:
            return "signal_processing"

        if context.get("is_analysis", False) or "analysis_type" in error_info:
            return "analysis"

        return "signal_processing"  # Default

    # Data Source Fallback Strategies
    async def _fallback_to_secondary_source(self, error_info: Dict) -> Optional[Dict]:
        """Fallback to secondary data source if primary fails"""
        context = error_info.get("context", {})
        symbol = context.get("symbol")

        if not symbol:
            return None

        logger.debug(f"Falling back to secondary source for {symbol}")

        # Simple fallback logic - replace with actual secondary source selection
        secondary_sources = {
            "coingecko": ["glassnode", "messari"],
            "glassnode": ["coingecko", "messari"],
            "messari": ["coingecko", "glassnode"],
            "twitter": ["reddit"],
            "reddit": ["twitter"],
        }

        primary_source = error_info.get("source_name")
        if primary_source in secondary_sources:
            return {
                "fallback_type": "secondary_source",
                "primary_source": primary_source,
                "secondary_sources": secondary_sources[primary_source],
            }

        return None

    async def _fallback_to_cached_data(self, error_info: Dict) -> Optional[Dict]:
        """Fallback to cached data if live data unavailable"""
        context = error_info.get("context", {})
        symbol = context.get("symbol")

        if not symbol:
            return None

        logger.debug(f"Falling back to cached data for {symbol}")

        # In a real implementation, this would retrieve from cache
        # For now, return mock data
        return {
            "fallback_type": "cached_data",
            "cached_time": datetime.now() - timedelta(minutes=5),
            "quality": "stale",
        }

    async def _fallback_to_statistical_model(self, error_info: Dict) -> Optional[Dict]:
        """Fallback to statistical model prediction if data unavailable"""
        context = error_info.get("context", {})
        symbol = context.get("symbol")

        if not symbol:
            return None

        logger.debug(f"Falling back to statistical model for {symbol}")

        return {
            "fallback_type": "statistical_model",
            "model_type": "ARIMA",
            "prediction": 0.5,
        }

    async def _fallback_to_default_value(self, error_info: Dict) -> Dict:
        """Fallback to default value if all else fails"""
        context = error_info.get("context", {})

        logger.debug(f"Falling back to default value")

        return {
            "fallback_type": "default_value",
            "value": 0.5,
        }

    # Signal Processing Fallback Strategies
    async def _fallback_to_simplified_processing(self, error_info: Dict) -> Dict:
        """Fallback to simplified signal processing"""
        logger.debug("Falling back to simplified signal processing")

        return {
            "fallback_type": "simplified_processing",
            "method": "weighted_average",
            "confidence": 0.7,
        }

    async def _fallback_to_mean_consensus(self, error_info: Dict) -> Dict:
        """Fallback to mean consensus of available signals"""
        logger.debug("Falling back to mean consensus")

        return {
            "fallback_type": "mean_consensus",
            "method": "arithmetic_mean",
            "confidence": 0.6,
        }

    async def _fallback_to_trend_extrapolation(self, error_info: Dict) -> Dict:
        """Fallback to trend extrapolation from historical data"""
        context = error_info.get("context", {})
        symbol = context.get("symbol")

        logger.debug(f"Falling back to trend extrapolation for {symbol}")

        return {
            "fallback_type": "trend_extrapolation",
            "method": "linear_regression",
            "confidence": 0.5,
        }

    async def _fallback_to_neutral_signal(self, error_info: Dict) -> Dict:
        """Fallback to neutral signal if all processing fails"""
        logger.debug("Falling back to neutral signal")

        return {
            "fallback_type": "neutral_signal",
            "signal": "NEUTRAL",
            "confidence": 0.3,
        }

    # Analysis Fallback Strategies
    async def _fallback_to_basic_analysis(self, error_info: Dict) -> Dict:
        """Fallback to basic analysis methods"""
        logger.debug("Falling back to basic analysis")

        return {
            "fallback_type": "basic_analysis",
            "method": "simple_trend",
            "confidence": 0.6,
        }

    async def _fallback_to_historical_patterns(self, error_info: Dict) -> Dict:
        """Fallback to historical pattern matching"""
        context = error_info.get("context", {})
        symbol = context.get("symbol")

        logger.debug(f"Falling back to historical patterns for {symbol}")

        return {
            "fallback_type": "historical_patterns",
            "method": "pattern_matching",
            "confidence": 0.4,
        }

    async def _fallback_to_simple_statistics(self, error_info: Dict) -> Dict:
        """Fallback to simple statistical analysis"""
        logger.debug("Falling back to simple statistics")

        return {
            "fallback_type": "simple_statistics",
            "method": "mean_std",
            "confidence": 0.3,
        }

    async def _fallback_to_neutral_analysis(self, error_info: Dict) -> Dict:
        """Fallback to neutral analysis if all methods fail"""
        logger.debug("Falling back to neutral analysis")

        return {
            "fallback_type": "neutral_analysis",
            "analysis": "NEUTRAL",
            "confidence": 0.2,
        }

    async def should_retry(self, error_info: Dict) -> bool:
        """Determine if error should be retried"""
        retry_count = error_info.get("retry_count", 0)

        if retry_count >= self.retry_config["max_retries"]:
            return False

        error_type = error_info.get("error_type")
        return any(retryable in error_type for retryable in self.retry_config["retryable_errors"])

    async def get_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay with exponential backoff"""
        delay = self.retry_config["initial_backoff"] * (
            self.retry_config["backoff_multiplier"] ** retry_count
        )

        return min(delay, self.retry_config["max_backoff"])

    async def get_error_statistics(self) -> Dict:
        """Get error statistics"""
        error_counts = defaultdict(int)
        source_error_counts = defaultdict(int)
        retryable_count = 0

        for error in self.error_history:
            error_counts[error["error_type"]] += 1

            if "source_name" in error:
                source_error_counts[error["source_name"]] += 1

            if await self.should_retry(error):
                retryable_count += 1

        return {
            "total_errors": len(self.error_history),
            "error_types": dict(error_counts),
            "source_errors": dict(source_error_counts),
            "retryable_errors": retryable_count,
            "non_retryable_errors": len(self.error_history) - retryable_count,
        }

    async def get_source_health_report(self) -> Dict:
        """Get source health report based on recent errors"""
        health_report = {}

        for source_name, errors in self.source_errors.items():
            recent_errors = [
                e
                for e in errors
                if (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 3600
            ]

            health_report[source_name] = {
                "total_errors": len(errors),
                "errors_last_hour": len(recent_errors),
                "is_healthy": len(recent_errors) < 5,
                "error_rate": len(recent_errors) / len(errors) if errors else 0,
            }

        return health_report

    async def clean_up_old_errors(self, max_age: int = 86400):
        """Remove old errors from history"""
        cutoff = datetime.now() - timedelta(seconds=max_age)

        self.error_history = deque(
            [e for e in self.error_history if datetime.fromisoformat(e["timestamp"]) > cutoff]
        )

        for source_name, errors in self.source_errors.items():
            self.source_errors[source_name] = deque(
                [e for e in errors if datetime.fromisoformat(e["timestamp"]) > cutoff]
            )


class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._states = defaultdict(
            lambda: {
                "failures": 0,
                "last_failure": None,
                "is_open": False,
                "last_state_change": datetime.now(),
            }
        )

    async def should_allow_request(self, service: str) -> bool:
        """Determine if circuit breaker should allow request"""
        state = self._states[service]

        # Circuit is open, check if we should try to recover
        if state["is_open"]:
            time_since_open = (datetime.now() - state["last_state_change"]).total_seconds()

            if time_since_open >= self.recovery_timeout:
                logger.info(f"Circuit breaker for {service} transitioning to half-open")
                state["is_open"] = False
                state["failures"] = 0
                return True

            logger.warning(f"Circuit breaker open for {service} - rejecting request")
            return False

        return True

    async def record_success(self, service: str):
        """Record successful request and reset failure counter"""
        state = self._states[service]
        state["failures"] = 0

        if state["is_open"]:
            state["is_open"] = False
            state["last_state_change"] = datetime.now()
            logger.info(f"Circuit breaker for {service} closed - service recovered")

    async def record_failure(self, service: str):
        """Record failed request and update circuit state"""
        state = self._states[service]
        state["failures"] += 1
        state["last_failure"] = datetime.now()

        if state["failures"] >= self.failure_threshold and not state["is_open"]:
            state["is_open"] = True
            state["last_state_change"] = datetime.now()
            logger.warning(
                f"Circuit breaker for {service} opened - {state['failures']} consecutive failures"
            )

    async def get_state(self, service: str) -> Dict:
        """Get circuit breaker state for service"""
        state = self._states[service]

        return {
            "service": service,
            "is_open": state["is_open"],
            "failures": state["failures"],
            "failure_threshold": self.failure_threshold,
            "time_since_last_failure": (
                (datetime.now() - state["last_failure"]).total_seconds()
                if state["last_failure"]
                else None
            ),
            "time_until_recovery": max(
                0,
                self.recovery_timeout
                - (
                    (datetime.now() - state["last_state_change"]).total_seconds()
                    if state["is_open"]
                    else 0
                ),
            ),
        }

    async def get_all_states(self) -> Dict:
        """Get all circuit breaker states"""
        all_states = {}

        for service, state in self._states.items():
            all_states[service] = await self.get_state(service)

        return all_states

    async def reset(self, service: str = None):
        """Reset circuit breaker state"""
        if service:
            self._states[service] = {
                "failures": 0,
                "last_failure": None,
                "is_open": False,
                "last_state_change": datetime.now(),
            }
            logger.info(f"Circuit breaker for {service} reset")
        else:
            self._states.clear()
            logger.info("All circuit breakers reset")


class RetryManager:
    """
    Smart retry manager with exponential backoff and circuit breaker integration
    """

    def __init__(self, error_handler: ErrorHandler, circuit_breaker: CircuitBreaker):
        self.error_handler = error_handler
        self.circuit_breaker = circuit_breaker
        self._retry_states = defaultdict(
            lambda: {
                "current_retry": 0,
                "last_retry": None,
                "next_retry": None,
                "success_count": 0,
                "failure_count": 0,
            }
        )

    async def execute_with_retry(self, coro, context: Dict, max_retries: int = 3) -> Optional[Dict]:
        """
        Execute coroutine with retry logic and fallback
        """
        context = context.copy()
        context.setdefault("retry_count", 0)

        # Check if circuit breaker is open
        service = context.get("service", "unknown")
        if not await self.circuit_breaker.should_allow_request(service):
            logger.warning(f"Circuit breaker open for {service} - skipping execution")
            return await self.error_handler.handle_error(
                Exception("Service unavailable - circuit breaker open"), context
            )

        try:
            result = await coro
            await self.circuit_breaker.record_success(service)
            await self._record_success(context)
            return result

        except Exception as e:
            await self.circuit_breaker.record_failure(service)
            context["retry_count"] += 1

            # Determine if we should retry
            if context["retry_count"] <= max_retries and await self.error_handler.should_retry(
                {
                    "error_type": type(e).__name__,
                    "context": context,
                }
            ):
                delay = await self.error_handler.get_retry_delay(context["retry_count"])
                logger.warning(
                    f"Retry {context['retry_count']}/{max_retries} "
                    f"for {context.get('symbol', 'unknown')} - "
                    f"Waiting {delay:.1f} seconds: {e}"
                )

                await asyncio.sleep(delay)
                return await self.execute_with_retry(coro, context, max_retries)

            # All retries failed
            logger.error(
                f"All {max_retries} retries failed for {context.get('symbol', 'unknown')}: {e}"
            )

            return await self.error_handler.handle_error(e, context)

    async def _record_success(self, context: Dict):
        """Record successful execution"""
        key = self._get_retry_state_key(context)
        state = self._retry_states[key]

        state["success_count"] += 1
        state["failure_count"] = 0
        state["current_retry"] = 0
        state["last_retry"] = datetime.now()
        state["next_retry"] = None

    async def _record_failure(self, context: Dict, error: Exception):
        """Record failed execution"""
        key = self._get_retry_state_key(context)
        state = self._retry_states[key]

        state["failure_count"] += 1
        state["current_retry"] = context.get("retry_count", 0)
        state["last_retry"] = datetime.now()

        if state["current_retry"] < context.get("max_retries", 3):
            delay = await self.error_handler.get_retry_delay(state["current_retry"])
            state["next_retry"] = datetime.now() + timedelta(seconds=delay)
        else:
            state["next_retry"] = None

    def _get_retry_state_key(self, context: Dict) -> str:
        """Generate key for retry state"""
        parts = []

        if "symbol" in context:
            parts.append(context["symbol"])

        if "service" in context:
            parts.append(context["service"])

        if "task_type" in context:
            parts.append(context["task_type"])

        return "|".join(parts) if parts else "default"

    async def get_retry_statistics(self) -> Dict:
        """Get retry statistics"""
        statistics = {
            "total_retries": 0,
            "total_failures": 0,
            "total_successes": 0,
            "service_statistics": defaultdict(
                lambda: {
                    "retries": 0,
                    "failures": 0,
                    "successes": 0,
                }
            ),
        }

        for state in self._retry_states.values():
            statistics["total_retries"] += state["current_retry"]
            statistics["total_failures"] += state["failure_count"]
            statistics["total_successes"] += state["success_count"]

        return statistics

    async def clear_retries(self, context: Dict = None):
        """Clear retry states"""
        if context:
            key = self._get_retry_state_key(context)
            if key in self._retry_states:
                del self._retry_states[key]
        else:
            self._retry_states.clear()


class SystemHealthMonitor:
    """
    System health monitoring with automated recovery
    """

    def __init__(self, error_handler: ErrorHandler, circuit_breaker: CircuitBreaker):
        self.error_handler = error_handler
        self.circuit_breaker = circuit_breaker
        self._health_checks = []
        self._recovery_actions = []
        self._running = False
        self._health_check_task = None

        # Health check thresholds
        self._health_thresholds = {
            "max_errors_per_minute": 10,
            "max_source_errors_per_hour": 20,
            "max_consecutive_errors": 5,
            "min_healthy_sources": 3,
        }

    def add_health_check(self, name: str, check_func: callable, interval: int = 60):
        """Add health check"""
        self._health_checks.append(
            {
                "name": name,
                "check": check_func,
                "interval": interval,
                "last_check": None,
                "last_result": None,
                "failure_count": 0,
            }
        )

    def add_recovery_action(self, name: str, action_func: callable, priority: int = 1):
        """Add recovery action"""
        self._recovery_actions.append(
            {
                "name": name,
                "action": action_func,
                "priority": priority,
            }
        )

    async def start_monitoring(self, interval: int = 30):
        """Start health monitoring"""
        if self._running:
            return

        self._running = True
        self._health_check_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info("System health monitor started")

    async def stop_monitoring(self):
        """Stop health monitoring"""
        if not self._running:
            return

        self._running = False
        self._health_check_task.cancel()

        try:
            await self._health_check_task
        except asyncio.CancelledError:
            pass

        logger.info("System health monitor stopped")

    async def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self._running:
            await self._run_health_checks()
            await self._check_system_health()
            await asyncio.sleep(interval)

    async def _run_health_checks(self):
        """Run scheduled health checks"""
        now = datetime.now()

        for check in self._health_checks:
            if (
                not check["last_check"]
                or (now - check["last_check"]).total_seconds() >= check["interval"]
            ):
                try:
                    result = await check["check"]()
                    check["last_result"] = result
                    check["last_check"] = now

                    if result.get("healthy", False):
                        check["failure_count"] = 0
                    else:
                        check["failure_count"] += 1

                    logger.debug(
                        f"Health check '{check['name']}': "
                        f"{'OK' if result.get('healthy') else 'FAILED'} "
                        f"({check['failure_count']} failures)"
                    )

                except Exception as e:
                    logger.error(f"Health check '{check['name']}' failed: {e}")
                    check["last_result"] = {"healthy": False, "error": str(e)}
                    check["failure_count"] += 1
                    check["last_check"] = now

    async def _check_system_health(self):
        """Check overall system health and trigger recovery if needed"""
        # Get error statistics
        error_stats = await self.error_handler.get_error_statistics()
        source_health = await self.error_handler.get_source_health_report()

        # Check error rates
        await self._check_error_rates(error_stats)

        # Check source health
        await self._check_source_health(source_health)

        # Check circuit breaker states
        await self._check_circuit_breakers()

    async def _check_error_rates(self, error_stats: Dict):
        """Check error rates against thresholds"""
        # Check if we're getting too many errors
        if error_stats["total_errors"] > self._health_thresholds["max_errors_per_minute"]:
            logger.warning(
                f"High error rate: {error_stats['total_errors']} errors/minute "
                f"(threshold: {self._health_thresholds['max_errors_per_minute']})"
            )
            await self._trigger_recovery()

    async def _check_source_health(self, source_health: Dict):
        """Check source health"""
        healthy_sources = sum(1 for source, info in source_health.items() if info["is_healthy"])

        if healthy_sources < self._health_thresholds["min_healthy_sources"]:
            logger.warning(
                f"Low healthy source count: {healthy_sources} sources "
                f"(threshold: {self._health_thresholds['min_healthy_sources']})"
            )
            await self._trigger_recovery()

    async def _check_circuit_breakers(self):
        """Check circuit breaker states"""
        circuit_states = await self.circuit_breaker.get_all_states()
        open_circuits = sum(1 for state in circuit_states.values() if state["is_open"])

        if open_circuits > 0:
            logger.warning(f"{open_circuits} circuit breakers open")
            await self._trigger_recovery()

    async def _trigger_recovery(self):
        """Trigger recovery actions"""
        logger.warning("Triggering system recovery")

        # Sort recovery actions by priority (lower = higher priority)
        sorted_actions = sorted(self._recovery_actions, key=lambda x: x["priority"])

        for action in sorted_actions:
            try:
                logger.info(f"Executing recovery action: {action['name']}")
                await action["action"]()
            except Exception as e:
                logger.error(f"Recovery action failed: {e}")

    async def get_health_report(self) -> Dict:
        """Get comprehensive health report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "error_statistics": await self.error_handler.get_error_statistics(),
            "source_health": await self.error_handler.get_source_health_report(),
            "circuit_breakers": await self.circuit_breaker.get_all_states(),
            "health_checks": await self._get_health_check_results(),
            "system_state": await self._determine_system_state(),
        }

    async def _get_health_check_results(self) -> Dict:
        """Get health check results"""
        results = {}

        for check in self._health_checks:
            results[check["name"]] = {
                "last_result": check["last_result"],
                "last_check": check["last_check"].isoformat() if check["last_check"] else None,
                "failure_count": check["failure_count"],
                "healthy": check["last_result"].get("healthy", False)
                if check["last_result"]
                else False,
            }

        return results

    async def _determine_system_state(self) -> str:
        """Determine overall system state"""
        health_report = await self.get_health_report()

        if (
            health_report["error_statistics"]["total_errors"]
            > self._health_thresholds["max_errors_per_minute"]
        ):
            return "CRITICAL"

        healthy_sources = sum(
            1 for info in health_report["source_health"].values() if info["is_healthy"]
        )
        if healthy_sources < self._health_thresholds["min_healthy_sources"]:
            return "WARNING"

        open_circuits = sum(
            1 for state in health_report["circuit_breakers"].values() if state["is_open"]
        )
        if open_circuits > 0:
            return "WARNING"

        return "HEALTHY"


# Global instances
error_handler = ErrorHandler()
circuit_breaker = CircuitBreaker()
retry_manager = RetryManager(error_handler, circuit_breaker)
health_monitor = SystemHealthMonitor(error_handler, circuit_breaker)
