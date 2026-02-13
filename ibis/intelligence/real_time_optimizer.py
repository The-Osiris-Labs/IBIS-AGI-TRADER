"""
IBIS Real-Time Intelligence Processing Optimization
===================================================
High-performance real-time processing architecture for market intelligence
"""

import asyncio
import concurrent.futures
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json
from collections import defaultdict, deque

import numpy as np

logger = logging.getLogger("IBIS")


class RealTimeProcessor:
    """
    High-performance real-time intelligence processor
    Optimized for low latency and high throughput
    """

    def __init__(self):
        self.processing_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.processing_tasks = []
        self._running = False
        self._processor_pool = None
        self._task_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        # Performance monitoring
        self.performance_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "avg_processing_time": 0.0,
            "max_processing_time": 0.0,
            "min_processing_time": float("inf"),
            "queue_length_history": deque(maxlen=100),
            "processing_time_history": deque(maxlen=100),
        }

        # Source-specific statistics
        self.source_stats = defaultdict(
            lambda: {
                "processed": 0,
                "errors": 0,
                "avg_time": 0.0,
                "last_processed": None,
            }
        )

        # Caching for frequently accessed data
        self.cache = {
            "source_metadata": {},
            "pattern_templates": {},
            "correlation_models": {},
        }

        # Pre-warm cache
        self._prewarm_cache()

    def _prewarm_cache(self):
        """Pre-warm cache with commonly used data"""
        # Pre-load source metadata
        self.cache["source_metadata"] = {
            "coingecko": {"priority": 0.8, "reliability": 0.9},
            "glassnode": {"priority": 0.9, "reliability": 0.95},
            "messari": {"priority": 0.85, "reliability": 0.88},
            "nansen": {"priority": 0.9, "reliability": 0.92},
            "twitter": {"priority": 0.6, "reliability": 0.75},
            "reddit": {"priority": 0.55, "reliability": 0.7},
        }

    async def start(self, num_processors: int = 2):
        """Start processing system"""
        if self._running:
            return

        self._running = True
        self._processor_pool = []

        for i in range(num_processors):
            task = asyncio.create_task(self._processor_worker(i))
            self._processor_pool.append(task)

        logger.info(f"Real-time processor started with {num_processors} workers")

    async def stop(self):
        """Stop processing system"""
        self._running = False

        for task in self._processor_pool:
            task.cancel()

        try:
            await asyncio.gather(*self._processor_pool, return_exceptions=True)
        except asyncio.CancelledError:
            pass

        self._processor_pool = []
        logger.info("Real-time processor stopped")

    async def add_task(self, task: Dict):
        """Add processing task to queue"""
        if not self._running:
            raise RuntimeError("Processor not running")

        await self.processing_queue.put(task)
        self.performance_stats["queue_length_history"].append(self.processing_queue.qsize())

    async def get_result(self, timeout: float = 30.0) -> Optional[Dict]:
        """Get processed result from queue"""
        try:
            result = await asyncio.wait_for(self.result_queue.get(), timeout=timeout)
            self.result_queue.task_done()
            return result
        except asyncio.TimeoutError:
            logger.warning("Result timeout")
            return None

    async def _processor_worker(self, worker_id: int):
        """Processor worker task"""
        logger.debug(f"Worker {worker_id} started")

        while self._running:
            try:
                task = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            start_time = time.time()

            try:
                # Process task
                result = await self._process_task(task)

                # Add to result queue
                await self.result_queue.put(result)

                # Update performance stats
                processing_time = time.time() - start_time
                await self._update_performance_stats(task, processing_time, success=True)

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await self._update_performance_stats(task, time.time() - start_time, success=False)

                # Add error result
                await self.result_queue.put(
                    {
                        "task_id": task.get("task_id"),
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            finally:
                self.processing_queue.task_done()

    async def _process_task(self, task: Dict) -> Dict:
        """Process a single task with type-specific handlers"""
        task_type = task.get("type", "UNKNOWN")
        task_id = task.get("task_id", f"task_{time.time()}")

        # Route to appropriate handler
        handler = await self._get_handler(task_type)
        if not handler:
            raise ValueError(f"Unknown task type: {task_type}")

        result = await handler(task)

        return {
            "task_id": task_id,
            "task_type": task_type,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

    async def _get_handler(self, task_type: str):
        """Get task handler based on type"""
        handlers = {
            "signal_quality": self._handle_signal_quality,
            "signal_fusion": self._handle_signal_fusion,
            "pattern_recognition": self._handle_pattern_recognition,
            "correlation_analysis": self._handle_correlation_analysis,
        }

        return handlers.get(task_type.lower())

    async def _handle_signal_quality(self, task: Dict) -> Dict:
        """Handle signal quality assessment"""
        from ibis.intelligence.quality_assurance import intelligence_qa

        source_signals = task.get("source_signals", {})
        symbol = task.get("symbol", "UNKNOWN")

        # Validate and score signals
        validated_signals = {}
        validation_reports = {}

        for source_name, signal in source_signals.items():
            is_valid, report = await intelligence_qa.validate_source(
                f"{source_name}_signal", signal
            )
            validation_reports[source_name] = report

            if is_valid:
                validated_signals[source_name] = intelligence_qa.cleanse_data(signal)

        return {
            "validated_signals": validated_signals,
            "validation_reports": validation_reports,
        }

    async def _handle_signal_fusion(self, task: Dict) -> Dict:
        """Handle signal fusion"""
        from ibis.intelligence.multi_source_correlator import signal_fusion_engine

        validated_signals = task.get("validated_signals", {})
        symbol = task.get("symbol", "UNKNOWN")
        correlation_matrix = task.get("correlation_matrix", {})
        consensus_report = task.get("consensus_report", {})

        fused_signal = await signal_fusion_engine.fuse_signals(
            symbol, validated_signals, correlation_matrix, consensus_report
        )

        return {"fused_signal": fused_signal}

    async def _handle_pattern_recognition(self, task: Dict) -> Dict:
        """Handle pattern recognition"""
        from ibis.intelligence.advanced_signal_processor import PatternRecognizer

        symbol = task.get("symbol", "UNKNOWN")
        signal = task.get("signal", {})
        historical_data = task.get("historical_data", {})

        pattern_recognizer = PatternRecognizer()
        patterns = await pattern_recognizer.recognize_patterns(symbol, signal, historical_data)

        return {"patterns": patterns}

    async def _handle_correlation_analysis(self, task: Dict) -> Dict:
        """Handle correlation analysis"""
        from ibis.intelligence.multi_source_correlator import MultiSourceCorrelationSystem

        symbol = task.get("symbol", "UNKNOWN")
        source_signals = task.get("source_signals", {})
        historical_data = task.get("historical_data", {})

        correlator = MultiSourceCorrelationSystem()
        correlation_report = await correlator.analyze_correlations(
            symbol, source_signals, historical_data
        )

        return {"correlation_report": correlation_report}

    async def _update_performance_stats(self, task: Dict, processing_time: float, success: bool):
        """Update performance statistics"""
        self.performance_stats["total_processed"] += 1
        if not success:
            self.performance_stats["total_errors"] += 1

        # Update processing time stats
        self.performance_stats["processing_time_history"].append(processing_time)
        self.performance_stats["avg_processing_time"] = np.mean(
            list(self.performance_stats["processing_time_history"])
        )
        self.performance_stats["max_processing_time"] = max(
            self.performance_stats["max_processing_time"], processing_time
        )
        self.performance_stats["min_processing_time"] = min(
            self.performance_stats["min_processing_time"], processing_time
        )

        # Update source-specific stats
        source = task.get("source", "unknown")
        source_stats = self.source_stats[source]
        source_stats["processed"] += 1
        if not success:
            source_stats["errors"] += 1
        source_stats["last_processed"] = datetime.now()

        # Update average processing time for source
        if source_stats["processed"] > 0:
            source_stats["avg_time"] = (
                source_stats["avg_time"] * (source_stats["processed"] - 1) + processing_time
            ) / source_stats["processed"]

    def get_performance_report(self) -> Dict:
        """Get performance report"""
        return {
            "total_processed": self.performance_stats["total_processed"],
            "total_errors": self.performance_stats["total_errors"],
            "error_rate": (
                self.performance_stats["total_errors"] / self.performance_stats["total_processed"]
                if self.performance_stats["total_processed"] > 0
                else 0
            ),
            "avg_processing_time": self.performance_stats["avg_processing_time"],
            "max_processing_time": self.performance_stats["max_processing_time"],
            "min_processing_time": self.performance_stats["min_processing_time"],
            "queue_length": self.processing_queue.qsize(),
            "avg_queue_length": (
                np.mean(list(self.performance_stats["queue_length_history"]))
                if self.performance_stats["queue_length_history"]
                else 0
            ),
            "source_stats": dict(self.source_stats),
        }

    def get_performance_summary(self) -> str:
        """Get human-readable performance summary"""
        report = self.get_performance_report()
        return (
            f"Processed: {report['total_processed']} tasks ({report['total_errors']} errors, "
            f"{report['error_rate']:.1%} error rate)\n"
            f"Avg: {report['avg_processing_time']:.2f}ms | "
            f"Min: {report['min_processing_time']:.2f}ms | "
            f"Max: {report['max_processing_time']:.2f}ms\n"
            f"Queue: {report['queue_length']} tasks ({report['avg_queue_length']:.1f} avg)\n"
            f"Source Stats:\n"
            + "\n".join(
                f"  {source}: {stats['processed']} tasks, {stats['avg_time']:.2f}ms avg"
                for source, stats in report["source_stats"].items()
            )
        )


class TaskPriorityQueue:
    """
    Priority-based task queue for intelligent scheduling
    """

    def __init__(self):
        self._priority_queues = defaultdict(asyncio.Queue)
        self._priority_levels = ["HIGH", "MEDIUM", "LOW"]
        self._task_counter = 0

    async def put(self, task: Dict, priority: str = "MEDIUM") -> int:
        """Put task into queue with priority"""
        task["task_id"] = task.get("task_id", f"task_{self._task_counter}")
        task["priority"] = priority.upper()
        task["created_time"] = time.time()

        self._task_counter += 1

        await self._priority_queues[task["priority"]].put(task)
        return task["task_id"]

    async def get(self) -> Dict:
        """Get highest priority task"""
        while True:
            # Check high priority first
            for priority in self._priority_levels:
                if not self._priority_queues[priority].empty():
                    task = await self._priority_queues[priority].get()
                    return task

            # All queues empty, wait
            await asyncio.sleep(0.1)

    def qsize(self) -> int:
        """Get total queue size"""
        return sum(queue.qsize() for queue in self._priority_queues.values())

    def empty(self) -> bool:
        """Check if all queues are empty"""
        return all(queue.empty() for queue in self._priority_queues.values())

    def get_priority_sizes(self) -> Dict:
        """Get queue sizes per priority"""
        return {p: self._priority_queues[p].qsize() for p in self._priority_levels}

    def get_statistics(self) -> Dict:
        """Get queue statistics"""
        total = self.qsize()
        return {
            "total_tasks": total,
            "priority_sizes": self.get_priority_sizes(),
            "created_tasks": self._task_counter,
        }


class AsyncDataFetcher:
    """
    Asynchronous data fetcher with request optimization
    """

    def __init__(self):
        self._pending_requests = set()
        self._cache = {}
        self._request_locks = defaultdict(asyncio.Lock)
        self._request_timeout = 10.0
        self._concurrent_limit = 5

        # Request optimization settings
        self._batching = True
        self._batch_timeout = 0.2
        self._batch_cache = defaultdict(list)

    async def fetch_with_cache(
        self, url: str, params: Dict = None, cache_ttl: float = 30.0, priority: str = "MEDIUM"
    ) -> Dict:
        """Fetch with cache and request optimization"""
        # Generate cache key
        cache_key = self._generate_cache_key(url, params)

        # Check cache first
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry["timestamp"] < cache_ttl:
                return cache_entry["data"]

        # Check if request already pending
        if cache_key in self._pending_requests:
            # Wait for existing request
            async with self._request_locks[cache_key]:
                if cache_key in self._cache:
                    return self._cache[cache_key]["data"]

        # Mark request as pending
        self._pending_requests.add(cache_key)

        try:
            async with self._request_locks[cache_key]:
                data = await self._execute_request(url, params, priority)

                # Cache the result
                self._cache[cache_key] = {
                    "data": data,
                    "timestamp": time.time(),
                    "url": url,
                    "params": params,
                }

                return data

        finally:
            self._pending_requests.remove(cache_key)

    async def _execute_request(self, url: str, params: Dict, priority: str) -> Dict:
        """Execute actual HTTP request"""
        # Simple request implementation - would use aiohttp in production
        await asyncio.sleep(0.1)  # Simulated latency

        return {
            "url": url,
            "params": params,
            "timestamp": datetime.now().isoformat(),
            "data": {},  # Simulated response
        }

    def _generate_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key from URL and parameters"""
        param_str = json.dumps(params, sort_keys=True) if params else ""
        return f"{url}:{param_str}"

    async def fetch_batch(self, requests: List[Dict], batch_key: str) -> List[Dict]:
        """Fetch multiple similar requests in a batch"""
        if not self._batching:
            return await asyncio.gather(
                *[self.fetch_with_cache(r["url"], r.get("params")) for r in requests]
            )

        # Check if batch already pending
        batch_lock = self._request_locks[batch_key]

        async with batch_lock:
            # Check for existing batch
            if batch_key in self._batch_cache:
                existing_batch = self._batch_cache[batch_key]
                existing_batch.extend(requests)
                return await self._wait_for_batch(batch_key)

            # Create new batch
            self._batch_cache[batch_key] = requests

            # Schedule batch processing
            asyncio.create_task(self._process_batch(batch_key))

            # Wait for batch completion
            return await self._wait_for_batch(batch_key)

    async def _wait_for_batch(self, batch_key: str) -> List[Dict]:
        """Wait for batch to complete"""
        start_time = time.time()

        while True:
            await asyncio.sleep(0.05)

            if batch_key not in self._batch_cache:
                return []

            # Check timeout
            if time.time() - start_time > self._batch_timeout:
                break

        return await self._process_batch(batch_key)

    async def _process_batch(self, batch_key: str) -> List[Dict]:
        """Process batch request"""
        if batch_key not in self._batch_cache:
            return []

        requests = self._batch_cache[batch_key]

        # Execute requests
        results = await asyncio.gather(
            *[self.fetch_with_cache(r["url"], r.get("params")) for r in requests]
        )

        del self._batch_cache[batch_key]

        return results

    def get_cache_statistics(self) -> Dict:
        """Get cache statistics"""
        hits = 0
        misses = 0
        current_entries = 0

        # Calculate statistics (would track hits/misses in production)
        return {
            "entries": current_entries,
            "hits": hits,
            "misses": misses,
            "hit_rate": hits / (hits + misses) if hits + misses > 0 else 0,
        }

    def get_pending_statistics(self) -> Dict:
        """Get pending request statistics"""
        return {
            "pending": len(self._pending_requests),
            "locks_held": len([k for k, v in self._request_locks.items() if v.locked()]),
        }


class StreamingBuffer:
    """
    High-performance streaming buffer for real-time data
    """

    def __init__(self, buffer_size: int = 1000, flush_interval: float = 0.1):
        self._buffer = []
        self._buffer_size = buffer_size
        self._flush_interval = flush_interval
        self._last_flush = time.time()
        self._buffer_lock = asyncio.Lock()
        self._data_processors = []

    def add_data_processor(self, processor: callable):
        """Add data processor for buffer flushing"""
        self._data_processors.append(processor)

    async def add_data(self, data: Dict):
        """Add data to buffer"""
        async with self._buffer_lock:
            self._buffer.append(data)

            # Check if flush needed
            if (
                len(self._buffer) >= self._buffer_size
                or time.time() - self._last_flush >= self._flush_interval
            ):
                await self._flush()

    async def _flush(self):
        """Flush buffer to processors"""
        if not self._buffer:
            return

        # Copy and clear buffer
        async with self._buffer_lock:
            data_to_process = self._buffer.copy()
            self._buffer = []
            self._last_flush = time.time()

        # Process data in parallel
        tasks = []
        for processor in self._data_processors:
            task = asyncio.create_task(processor(data_to_process))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def get_buffer_statistics(self) -> Dict:
        """Get buffer statistics"""
        async with self._buffer_lock:
            return {
                "current_size": len(self._buffer),
                "max_size": self._buffer_size,
                "flush_interval": self._flush_interval,
                "time_since_flush": time.time() - self._last_flush,
                "processors_count": len(self._data_processors),
            }


class PerformanceOptimizer:
    """
    Performance optimization controller
    """

    def __init__(self, processor: RealTimeProcessor):
        self._processor = processor
        self._optimization_tasks = []
        self._running = False
        self._optimization_interval = 30.0  # Check every 30 seconds

        # Performance thresholds
        self._thresholds = {
            "avg_latency": 1.0,  # seconds
            "max_latency": 5.0,  # seconds
            "queue_length": 100,
            "error_rate": 0.1,  # 10%
        }

    async def start_optimization(self):
        """Start performance optimization loop"""
        if self._running:
            return

        self._running = True
        logger.info("Performance optimizer started")

        while self._running:
            try:
                await self._optimization_loop()
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")

            await asyncio.sleep(self._optimization_interval)

    async def _optimization_loop(self):
        """Run optimization loop"""
        performance_report = self._processor.get_performance_report()

        # Check performance metrics against thresholds
        issues = await self._check_performance_issues(performance_report)

        if issues:
            await self._apply_optimizations(issues)

    async def _check_performance_issues(self, report: Dict) -> List[Dict]:
        """Check performance issues"""
        issues = []

        # Check latency
        if report["avg_processing_time"] > self._thresholds["avg_latency"]:
            issues.append(
                {
                    "type": "high_latency",
                    "metric": "avg_processing_time",
                    "value": report["avg_processing_time"],
                    "threshold": self._thresholds["avg_latency"],
                    "severity": "warning"
                    if report["avg_processing_time"] < self._thresholds["avg_latency"] * 2
                    else "critical",
                }
            )

        if report["max_processing_time"] > self._thresholds["max_latency"]:
            issues.append(
                {
                    "type": "maximum_latency",
                    "metric": "max_processing_time",
                    "value": report["max_processing_time"],
                    "threshold": self._thresholds["max_latency"],
                    "severity": "critical",
                }
            )

        # Check queue length
        if report["queue_length"] > self._thresholds["queue_length"]:
            issues.append(
                {
                    "type": "queue_overflow",
                    "metric": "queue_length",
                    "value": report["queue_length"],
                    "threshold": self._thresholds["queue_length"],
                    "severity": "critical"
                    if report["queue_length"] > self._thresholds["queue_length"] * 2
                    else "warning",
                }
            )

        # Check error rate
        if report["error_rate"] > self._thresholds["error_rate"]:
            issues.append(
                {
                    "type": "high_error_rate",
                    "metric": "error_rate",
                    "value": report["error_rate"],
                    "threshold": self._thresholds["error_rate"],
                    "severity": "warning"
                    if report["error_rate"] < self._thresholds["error_rate"] * 2
                    else "critical",
                }
            )

        return issues

    async def _apply_optimizations(self, issues: List[Dict]):
        """Apply performance optimizations"""
        for issue in issues:
            logger.warning(
                f"Performance issue: {issue['type']} - {issue['value']:.2f} (threshold: {issue['threshold']})"
            )

            if issue["type"] == "high_latency":
                await self._optimize_latency(issue)
            elif issue["type"] == "queue_overflow":
                await self._optimize_queue(issue)
            elif issue["type"] == "high_error_rate":
                await self._optimize_error_rate(issue)

    async def _optimize_latency(self, issue: Dict):
        """Optimize latency"""
        logger.info("Optimizing for high latency")
        # Could implement dynamic worker scaling, cache warming, etc.

    async def _optimize_queue(self, issue: Dict):
        """Optimize queue overflow"""
        logger.info("Optimizing queue overflow")
        # Could implement task prioritization, selective dropping, etc.

    async def _optimize_error_rate(self, issue: Dict):
        """Optimize error rate"""
        logger.info("Optimizing high error rate")
        # Could implement error monitoring, source health checks, etc.

    async def get_optimization_report(self) -> Dict:
        """Get optimization report"""
        return {
            "running": self._running,
            "optimization_interval": self._optimization_interval,
            "thresholds": self._thresholds,
            "performance_report": self._processor.get_performance_report(),
        }


# Global instances
real_time_processor = RealTimeProcessor()
async_data_fetcher = AsyncDataFetcher()
performance_optimizer = PerformanceOptimizer(real_time_processor)
