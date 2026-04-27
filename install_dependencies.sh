#!/bin/bash

echo "========================================"
echo "Installing Required Python Libraries"
echo "========================================"
echo ""
echo "This will install the following packages:"
echo "- numpy (numerical computing)"
echo "- matplotlib (plotting and visualization)"
echo "- scikit-learn (machine learning utilities)"
echo "- pyperclip (clipboard operations)"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3 first."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python found. Installing dependencies..."
echo ""

# Upgrade pip first
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

echo ""
echo "Installing required packages..."
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "SUCCESS! All dependencies installed."
    echo "========================================"
    echo ""
    echo "You can now run the application using:"
    echo "  python3 curve_adjuster.py"
    echo ""
    echo "Or simply run: ./run_curve_adjuster.sh"
    echo ""
else
    echo ""
    echo "========================================"
    echo "ERROR: Installation failed!"
    echo "========================================"
    echo ""
    echo "Please try running this command manually:"
    echo "  pip3 install numpy matplotlib scikit-learn pyperclip"
    echo ""
fi

read -p "Press Enter to continue..."

