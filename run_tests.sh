#!/bin/bash

# Ensure PYTHONPATH is set to the current directory
export PYTHONPATH=.

# Run all tests with coverage report
echo "--- Running Story Generator Robust Test Suite ---"
./.venv/bin/pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "Test run complete. Coverage report generated in htmlcov/index.html"
