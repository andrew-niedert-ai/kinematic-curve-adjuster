# Curve Adjuster Improvements

## Overview
Enhanced the Kinematic Curve Adjuster utility to better handle 3rd order polynomial curves and provide manual fine-tuning controls for precise curve adjustments.

## 1. Improved Algorithm for 3rd Order Curves

### Enhanced Iterative Convergence
- **Increased iterations**: From 20 to 50 iterations for better convergence
- **Adaptive correction factor**: Dynamically adjusts based on error magnitude to prevent oscillation
  - Large errors (>10): Uses 0.5 correction factor
  - Medium errors (5-10): Uses 0.6 correction factor
  - Small errors (1-5): Uses 0.7 correction factor
  - Very small errors (<1): Uses 0.85 correction factor
- **Better handling of complex curves**: The adaptive approach prevents overshooting and helps achieve more accurate min/max values

## 2. Safety Safeguards

### Maximum Deviation Percentage
- **New field**: "Max Deviation %" in Adjustment Parameters (default: 50%)
- **Pre-flight check**: Warns user if requested adjustment exceeds the maximum allowed percentage
- **User confirmation**: Option to proceed anyway if desired
- **Calculation**: Compares the change in Y range (desired vs original) as a percentage

Example warning message:
```
Requested adjustment (75.2% change) exceeds
maximum allowed deviation (50.0%).

Original Y range: 400.0
Desired Y range: 700.8

Continue anyway?
```

## 3. Manual Fine-Tuning Controls

### New Control Panel: "Manual Fine-Tuning Controls"
A comprehensive set of controls for manual curve adjustment after automatic fitting.

#### A. Scale Y (Vertical Scaling)
- **Controls**: ▼ Scale Down | ▲ Scale Up
- **Increment field**: Adjustable percentage increment (default: 1.0%)
- **Current display**: Shows current scale as percentage (e.g., "Current: 102.5%")
- **Function**: Scales the Y values of the curve up or down by the specified percentage

#### B. Shift Y (Vertical Translation)
- **Controls**: ▼ Shift Down | ▲ Shift Up
- **Increment field**: Adjustable shift amount (default: 1.0 units)
- **Current display**: Shows current Y shift (e.g., "Current: +3.5")
- **Function**: Shifts the entire curve vertically by the specified amount

#### C. Shift X (Horizontal Translation)
- **Controls**: ◄ Shift Left | ► Shift Right
- **Increment field**: Adjustable shift amount (default: 1.0 units)
- **Current display**: Shows current X shift (e.g., "Current: -2.0")
- **Function**: Shifts the entire curve horizontally by the specified amount

#### D. Reset Button
- **"Reset All Manual Adjustments"**: Returns all manual adjustments to default values (scale=100%, shifts=0)

## 4. Enhanced Visualization

### Multi-Layer Plotting
When manual adjustments are active, the plot now shows three layers:
1. **Original Data** (Blue dots & dashed line): Your original input data and its fitted curve
2. **Auto Adjusted** (Orange, semi-transparent): The automatically adjusted curve before manual tuning
3. **Manual Adjusted** (Red, prominent): The final curve with all manual adjustments applied

This allows you to see:
- Where you started (original)
- What the algorithm produced (auto adjusted)
- What your final result is (manual adjusted)

## 5. Updated Statistics Display

### Manual Adjustments Section
When manual adjustments are applied, a new section appears in the Statistics panel:

```
Manual Adjustments Applied:
  Scale: 102.50%
  Y Shift: +3.5000
  X Shift: -2.0000
  Current Y range: [-2.1500, 2.3200]
```

This shows:
- Current scale percentage
- Current Y shift value
- Current X shift value
- The actual Y range of the manually adjusted curve

## 6. Enhanced Copy Function

### Copy New Y Values
The "Copy New Y Values" button now intelligently handles manual adjustments:
- **With manual adjustments**: Copies the manually adjusted Y values and notes this in the success message
- **Without manual adjustments**: Copies the automatically adjusted Y values as before
- **Message includes**: Type of adjustment applied (manual vs automatic)

## Usage Workflow

### Typical Usage Pattern
1. **Load your data** in the Curve Adjustment tab
2. **Click "Load & Fit Data"** to see the original polynomial fit
3. **Enter desired Y Min/Max values**
4. **Set Max Deviation %** (safety limit)
5. **Click "Apply Adjustments"** for automatic adjustment
6. **Review the result** in the plot
7. **Fine-tune manually** if needed:
   - Use Scale Y to adjust amplitude
   - Use Shift Y to move curve up/down
   - Use Shift X to move curve left/right
8. **Copy the final Y values** when satisfied

### Tips for Manual Adjustments
- **Start with small increments** (1% for scaling, 0.5 for shifts)
- **Watch the "Current Y range"** in statistics to see if you're hitting your targets
- **Reset if you overshoot** and try again with smaller increments
- **Visual feedback**: The plot updates immediately after each adjustment

## Technical Details

### Manual Adjustment Implementation
The manual adjustments are applied in this order:
1. X-shift is applied to the X values: `x_adjusted = x - x_shift`
2. Polynomial is evaluated at adjusted X values: `y = poly(x_adjusted)`
3. Scale is applied to Y values: `y_scaled = y * scale`
4. Y-shift is applied: `y_final = y_scaled + y_shift`

This order allows independent control of each transformation.

### Adaptive Convergence Algorithm
The improved algorithm adjusts its convergence strategy based on how far off it is from the target:
- **Large errors**: Be cautious, take smaller steps (50% correction)
- **Small errors**: Be aggressive, converge faster (85% correction)

This prevents oscillation that can occur with 3rd order polynomials where overshooting leads to large swings in min/max values.

## Benefits

1. **Better accuracy**: Improved convergence for difficult 3rd order curves
2. **Safety**: Protection against excessive modifications
3. **Flexibility**: Manual controls for cases where automatic adjustment isn't perfect
4. **Transparency**: Clear visualization of all adjustment layers
5. **Control**: Precise fine-tuning with adjustable increments

## Future Enhancements (Potential)

- Undo/Redo functionality for manual adjustments
- Preset manual adjustment patterns (e.g., "shift to align peaks")
- Keyboard shortcuts for manual adjustments
- Animation showing convergence process
- Export adjustment history/parameters

---

**Version**: Updated April 27, 2026  
**Repository**: https://github.com/andrew-niedert-ai/kinematic-curve-adjuster
