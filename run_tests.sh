#!/bin/bash
# Quick test runner for aether-guard

echo "=========================================="
echo "🧪 aether-guard Test Suite"
echo "=========================================="

# Install dependencies if needed
python -m pip install -q pytest pytest-asyncio 2>/dev/null

# Run the tests
python run_tests.py
