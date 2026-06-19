#!/usr/bin/env python
"""
Test runner script for aether-guard
Runs the test suite and reports results
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ {description} FAILED")
        return False
    print(f"✅ {description} PASSED")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 aether-guard Test Suite Runner")
    print("="*60)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("\n⚠️  pytest not found. Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pytest", "pytest-asyncio"])
    
    all_passed = True
    
    # Run unit tests
    all_passed &= run_command(
        f"{sys.executable} -m pytest tests/test_basic_guard.py -v --tb=short",
        "Unit Tests (Basic Guard Functionality)"
    )
    
    # Run integration tests
    all_passed &= run_command(
        f"{sys.executable} -m pytest tests/test_integration.py -v --tb=short",
        "Integration Tests (Real-World Scenarios)"
    )
    
    # Run stress tests
    all_passed &= run_command(
        f"{sys.executable} -m pytest tests/test_stress.py -v --tb=short",
        "Stress Tests (Load & Reliability)"
    )
    
    # Final report
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
