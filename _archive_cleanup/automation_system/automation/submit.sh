#!/bin/bash

# Simple wrapper for the python update script
# Usage: ./automation/submit.sh my_data.yaml

if [ -z "$1" ]; then
    echo "Usage: ./automation/submit.sh <path_to_yaml>"
    exit 1
fi

python3 automation/submit_update.py --yaml "$1"
