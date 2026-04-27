#!/bin/bash
echo "Starting Kinematic Curve Adjuster..."
echo ""
python3 curve_adjuster.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to run the application."
    echo "Please make sure Python is installed and dependencies are installed."
    echo "Run: pip3 install -r requirements.txt"
    read -p "Press Enter to continue..."
fi

