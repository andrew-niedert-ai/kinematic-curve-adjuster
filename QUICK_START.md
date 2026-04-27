# Quick Start Guide

## Installation (One-Time Setup)

**Windows:**
- Double-click `install_dependencies.bat` and wait for it to complete

**Linux/Mac:**
- Run in terminal: `chmod +x install_dependencies.sh && ./install_dependencies.sh`

**Manual Installation:**
- Run in terminal: `pip install numpy matplotlib scikit-learn pyperclip`

## Running the Application

```bash
python curve_adjuster.py
```

## Quick Test with Sample Data

1. Open `sample_data.txt` in a text editor
2. Copy the X values from Example 1
3. Paste into the X Values field in the application
4. Copy the Y values from Example 1
5. Paste into the Y Values field in the application
6. Click "Load & Fit Data"
7. Enter -5 for Y Min and 5 for Y Max
8. Click "Apply Adjustments"
9. Click one of:
   - "Copy Adjusted Equation" to get the equation with (x-offset) format
   - "Copy New Y Values" to get Y values as a column for pasting into Excel

## What You'll See

- **Original Data**: Blue circles with blue dashed fit line
- **Adjusted Data**: Red squares with red solid fit line
- **Origin**: Green circle at (0,0) - your adjusted curve should pass through this
- **Equations**: Polynomial equations with coefficients in scientific notation
- **Statistics**: Data point count, ranges, R² values

## Tips

- Use at least 4 data points for best results
- Higher R² values (closer to 1.0) indicate better fits
- The application automatically chooses between linear, 2nd order, or 3rd order polynomials
- The adjusted curve will always pass through (0,0) after adjustments
- Copy equations to clipboard and paste into Excel, MATLAB, or other tools

## Need Help?

See `README.md` for detailed documentation and troubleshooting.

