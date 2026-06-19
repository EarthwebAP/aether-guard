"""
Integration tests for aether-guard with real-world scenarios
"""
import pytest
import asyncio
from aether_guard import guard, async_guard, GuardRetryException, GuardTimeoutException


class TestLangChainIntegration:
    """Test integration with LangChain-like patterns"""
    
    def test_simulated_chain_execution(self):
        """Test decorator with a simulated LangChain chain"""
        execution_count = {'count': 0}
        
        @guard(timeout=5, retries=2)
        def simulated_chain_run():
            execution_count['count'] += 1
            if execution_count['count'] < 2:
                raise ConnectionError("API temporarily unavailable")
            return {"output": "Generated report"}
        
        result = simulated_chain_run()
        assert result["output"] == "Generated report"
        assert execution_count['count'] == 2
    
    def test_chain_with_timeout_protection(self):
        """Test timeout protection on chain execution"""
        @guard(timeout=1, retries=1)
        def chain_that_might_hang():
            # Simulate work that completes in time
            import time
            time.sleep(0.5)
            return "completed"
        
        result = chain_that_might_hang()
        assert result == "completed"


class TestRecursiveAgentPattern:
    """Test decorator with recursive agent patterns"""
    
    def test_recursive_function_with_guard(self):
        """Test decorated recursive functions"""
        @guard(retries=1)
        def factorial(n, depth=0):
            if depth > 5:  # Safety limit
                raise RecursionError("Too deep")
            if n <= 1:
                return 1
            return n * factorial(n - 1, depth + 1)
        
        # Note: Each recursive call gets its own guard protection
        result = factorial(5)
        assert result == 120


class TestBatchProcessing:
    """Test batch processing scenarios"""
    
    def test_batch_processing_with_retry(self):
        """Test processing multiple items with retry protection"""
        items_processed = []
        retry_count = {'count': 0}
        
        @guard(retries=2)
        def process_batch(items):
            retry_count['count'] += 1
            if retry_count['count'] < 2:
                raise ValueError("Batch processing failed, retrying...")
            for item in items:
                items_processed.append(item)
            return len(items_processed)
        
        batch = [1, 2, 3, 4, 5]
        result = process_batch(batch)
        assert result == 5
        assert items_processed == batch
    
    def test_partial_batch_recovery(self):
        """Test graceful handling of partial batch failures"""
        @guard(retries=1)
        def process_items(items):
            results = []
            for item in items:
                try:
                    results.append(item * 2)
                except Exception:
                    results.append(None)
            return results
        
        result = process_items([1, 2, 3, 4])
        assert result == [2, 4, 6, 8]


class TestErrorRecovery:
    """Test various error recovery scenarios"""
    
    def test_recovery_from_network_error(self):
        """Test recovery from simulated network errors"""
        attempt = {'count': 0}
        
        @guard(retries=3)
        def api_call():
            attempt['count'] += 1
            if attempt['count'] < 2:
                raise ConnectionError("Network timeout")
            return {"status": "success"}
        
        result = api_call()
        assert result["status"] == "success"
    
    def test_recovery_from_rate_limiting(self):
        """Test recovery from rate limit errors"""
        attempt = {'count': 0}
        
        @guard(retries=3, retry_backoff=1.0)
        def rate_limited_call():
            attempt['count'] += 1
            if attempt['count'] < 2:
                raise RuntimeError("Rate limited, retry after 1 second")
            return "data"
        
        result = rate_limited_call()
        assert result == "data"


class TestAsyncIntegration:
    """Test async patterns"""
    
    @pytest.mark.asyncio
    async def test_async_with_retry(self):
        """Test async guard with retry"""
        attempt = {'count': 0}
        
        @async_guard(retries=2)
        async def async_api_call():
            attempt['count'] += 1
            await asyncio.sleep(0.01)
            if attempt['count'] < 2:
                raise ConnectionError("Async connection failed")
            return "async data"
        
        result = await async_api_call()
        assert result == "async data"
        assert attempt['count'] == 2
    
    @pytest.mark.asyncio
    async def test_concurrent_async_calls(self):
        """Test multiple concurrent async operations"""
        @async_guard(retries=1)
        async def fetch_data(id):
            await asyncio.sleep(0.01)
            return f"data_{id}"
        
        # Run multiple tasks concurrently
        tasks = [fetch_data(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert results[0] == "data_0"
        assert results[4] == "data_4"


class TestStressScenarios:
    """Test under stress conditions"""
    
    def test_high_frequency_calls(self):
        """Test handling many rapid calls"""
        @guard(retries=1)
        def fast_operation():
            return "result"
        
        results = [fast_operation() for _ in range(100)]
        assert len(results) == 100
        assert all(r == "result" for r in results)
    
    def test_mixed_success_and_failure(self):
        """Test mixed success/failure patterns"""
        call_count = {'count': 0}
        
        @guard(retries=2)
        def sometimes_fails():
            call_count['count'] += 1
            # Fail on odd calls, succeed on even
            if call_count['count'] % 2 == 1 and call_count['count'] < 10:
                raise ValueError("Odd call failed")
            return call_count['count']
        
        result = sometimes_fails()
        assert result > 0


class TestComplexScenarios:
    """Test complex real-world scenarios"""
    
    def test_chained_guarded_functions(self):
        """Test multiple guarded functions called in sequence"""
        @guard(retries=1)
        def step1():
            return {"data": "processed"}
        
        @guard(retries=1)
        def step2(input_data):
            return {"enriched": input_data["data"]}
        
        @guard(retries=1)
        def step3(input_data):
            return {"final": input_data["enriched"]}
        
        result1 = step1()
        result2 = step2(result1)
        result3 = step3(result2)
        
        assert result3["final"] == "processed"
    
    def test_nested_guarded_functions(self):
        """Test nested decorated functions"""
        @guard(retries=1)
        def outer():
            @guard(retries=1)
            def inner():
                return "inner result"
            return inner()
        
        result = outer()
        assert result == "inner result"
