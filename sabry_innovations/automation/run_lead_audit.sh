#!/bin/bash
############################################################
# CRM Lead Audit Automation - Linux Shell Script
############################################################
#
# This script runs the CRM Lead Audit automation on Linux
#
# Usage: ./run_lead_audit.sh
############################################################

echo "============================================================"
echo "CRM Lead Audit Automation"
echo "Starting: $(date)"
echo "============================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
else
    echo "WARNING: .env file not found, using system environment variables"
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found"
    echo "Please run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Run the automation script
echo "Running lead audit automation..."
python lead_audit_automation.py

EXIT_CODE=$?

# Deactivate virtual environment
deactivate

echo ""
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "Automation completed successfully"
else
    echo "ERROR: Automation failed with exit code $EXIT_CODE"
    echo "Check logs in: logs/lead_audit_$(date +%Y%m%d).log"
fi
echo "Finished: $(date)"
echo "============================================================"

exit $EXIT_CODE
