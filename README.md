# Kinematic Curve Adjustment Utility

A Python GUI application for manipulating kinematic curves with polynomial fitting, scaling, and origin constraint features.

## Features

1. **Data Input**: Paste X and Y values directly into the GUI (supports multiple formats: comma-separated, space-separated, or one value per line)

2. **Automatic Best Fit**: Automatically fits linear, 2nd order, and 3rd order polynomials and selects the one with the best R² value

3. **Stretch/Shrink**: Adjust Y values to desired relative maximum and minimum within the provided X-value range

4. **Force Through Origin**: Automatically adjusts the curve to pass through point (0, 0) after stretch/shrink operations

5. **Copy to Clipboard**: Copy equations (with ^ exponents) or recalculated Y values as a column for easy use in spreadsheets

6. **Visualization**: Side-by-side comparison of original and adjusted data with fitted curves on an interactive graph

## Installation

### Prerequisites
- Python 3.7 or higher

### Quick Setup (Recommended)

**Windows:**
1. Double-click `install_dependencies.bat`
2. Wait for installation to complete
3. Done! You can now run the application.

**Linux/Mac:**
1. Open terminal in this directory
2. Run: `chmod +x install_dependencies.sh`
3. Run: `./install_dependencies.sh`
4. Done! You can now run the application.

### Manual Setup

If the quick setup doesn't work, install packages manually:

```bash
pip install numpy matplotlib scikit-learn pyperclip
```

Or using the requirements file:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python curve_adjuster.py
```

### Step-by-Step Guide

1. **Enter Data**:
   - Paste your X values in the left text box
   - Paste your Y values in the right text box
   - Values can be:
     - One per line
     - Comma-separated: `1, 2, 3, 4, 5`
     - Space-separated: `1 2 3 4 5`
     - Any combination of the above

2. **Load and Fit**:
   - Click "Load & Fit Data" button
   - The application will automatically:
     - Parse your data
     - Fit linear, 2nd order, and 3rd order polynomials
     - Select the best fit based on R² value
     - Display the equation and statistics
     - Show the original data on the graph

3. **Apply Adjustments**:
   - Enter your desired Y minimum value
   - Enter your desired Y maximum value
   - Click "Apply Adjustments"
   - The application will:
     - Scale Y values to the specified range
     - Adjust the curve to pass through (0, 0)
     - Refit the polynomial
     - Display adjusted equation and updated graph

4. **Copy Results**:
   - **Copy Original Equation**: Copies the original fitted equation (with ^ notation)
   - **Copy Adjusted Equation**: Copies the adjusted equation in (x-offset) format (with ^ notation)
   - **Copy New Y Values**: Copies the recalculated Y values (evaluated at original X positions) as a column
   - Paste directly into Excel, databases, or text files

### Example

**Input Data:**
```
X: 0, 1, 2, 3, 4, 5
Y: 0.5, 2.1, 4.3, 6.8, 9.5, 12.3
```

**Adjustments:**
- Desired Y Min: -10
- Desired Y Max: 10

**Result:** 
1. Data is scaled to fit exactly within [-10, 10]
2. Best-fit polynomial is calculated
3. X-offset is found where the curve equals zero
4. Equation is expressed as f(x-offset) format
5. The equation in (x-offset) form will pass through (0,0)

**Understanding the Constraints:**
When both "pass through origin" and "Y range" constraints are applied, the algorithm:
- Scales Y values to reach EXACTLY both Y min AND Y max ✓
- Finds X-offset where the scaled curve crosses zero ✓
- Expresses equation as polynomial of (x-offset) form ✓
- When you substitute x=offset into the equation, y=0 (passes through origin)
- Uses single scale factor (maintains data proportions)

## Features in Detail

### Polynomial Fitting
The application tests three types of curves:
- **Linear**: y = ax + b
- **2nd Order**: y = ax² + bx + c
- **3rd Order**: y = ax³ + bx² + cx + d

It automatically selects the curve with the highest R² (coefficient of determination) value, indicating the best fit.

### Scaling Algorithm

The application uses an iterative algorithm with calculus-based verification:

### Single Iteration Steps:
1. **Fit Original Polynomial**: Fits best polynomial (1st, 2nd, or 3rd order) to original data
2. **Find True Min/Max (Calculus)**: Uses derivative (f'(x) = 0) to find critical points of fitted curve
3. **Calculate Range**: Determines the original fitted curve's range
4. **Scale Original Data**: Applies scale factor to original Y data based on target range
5. **Fit & Verify Scaled**: Fits polynomial to scaled data, confirms range using derivative
6. **Apply Y-Offset**: Calculates and applies Y-offset to align with target min/max
7. **Fit & Verify Offset**: Fits polynomial to offset data, confirms target range using derivative
8. **Calculate X-Offset**: Finds where the offset polynomial crosses y=0
9. **Apply X-Offset to Data**: Shifts X data by x-offset amount
10. **Fit Final Polynomial**: Fits final polynomial to x-shifted, y-offset data

### Iterative Convergence:
11. **Evaluate at Original X**: Evaluates final polynomial at original X positions
12. **Check Convergence**: Compares actual min/max to desired values
13. **Adjust Targets**: If not converged, adjusts target min/max and repeats (80% correction factor)
14. **Repeat Until Converged**: Iterates until error < 0.001 or max 20 iterations reached

**Important Notes:**
- Applies transformations to **original data**, not fitted curves ✓
- **Uses calculus (derivatives)** to verify ranges at each step ✓
- **Iterative convergence** - automatically adjusts targets to achieve exact bounds ✓
- The Y range will EXACTLY match [Y min, Y max] when evaluated at original X values ✓
- Handles 2nd order and linear fits where extrema occur at endpoints ✓
- Typically converges in 1-5 iterations (max 20) ✓
- X-offset is applied to the data itself (shifts coordinate system) ✓
- Final polynomial evaluated at original X positions (accounting for offset) ✓
- Statistics display shows convergence iterations and final error ✓
- Clipboard output uses ^ (caret) for exponents for compatibility

### Statistics Display
The application shows:
- Number of data points
- X and Y ranges
- Best fit polynomial order
- R² values for both original and adjusted fits
- Y value at x = 0 (should be ~0 after adjustment)

## Dependencies

- **numpy**: Numerical computations and polynomial fitting
- **matplotlib**: Data visualization
- **scikit-learn**: R² score calculation
- **pyperclip**: Clipboard operations
- **tkinter**: GUI framework (included with Python)

## Troubleshooting

**Issue**: "Please enter both X and Y values"
- **Solution**: Make sure you've entered data in both text boxes

**Issue**: "X and Y must have the same number of values"
- **Solution**: Count your X and Y values - they must match

**Issue**: "Need at least 4 data points"
- **Solution**: You need at least 4 X-Y pairs to fit a 3rd order polynomial

**Issue**: Application doesn't start
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

## License

This utility is provided as-is for kinematic curve analysis and adjustment tasks.

## Author

Created for kinematic curve adjustments in database refresh operations.

