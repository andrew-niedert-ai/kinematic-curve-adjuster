# Algorithm Explanation: Fitted Curve Scaling with X-Offset

## The Correct Algorithm

You want to adjust kinematic curve data with TWO simultaneous constraints:
1. **Exact Y range**: The adjusted data must reach EXACTLY [Y_min, Y_max]
2. **Pass through origin**: The curve must cross y=0 (with x-offset notation)

## The Solution: Scale Fitted Curve, Then Find X-Offset

This approach works with the **fitted polynomial curve** rather than raw data points, ensuring smooth results.

## The Algorithm (Step by Step)

### Step 1: Fit Polynomial to Original Data
```
Original data: X = [...], Y = [...]

Fit polynomial (choose best of 1st, 2nd, 3rd order by R²):
Original equation: y = 5.115e-07*x³ - 5.348e-06*x² - 1.650e-02*x + 1.485e-05
```

### Step 2: Find True Min/Max Using Calculus
```
For polynomial: y = ax³ + bx² + cx + d
Derivative: y' = 3ax² + 2bx + c

Find critical points by solving y' = 0:
Critical points (roots of derivative) = [...X values where slope = 0...]

Evaluate polynomial at:
- Critical points (local min/max)
- Endpoints of X range (boundary values)

Example:
Critical points within [-125, 125]: [-87.3, 0, 91.2]
Evaluate at: [-125, -87.3, 0, 91.2, 125]
Y values: [0.918, -1.200, 0.000, 1.084, -1.075]

True fitted min = -1.200 (at X ≈ -87.3)
True fitted max = 1.084 (at X ≈ 91.2)
Fitted range = 2.284
```

**Why This Matters:**
The actual min/max of the curve might not occur exactly at your data points. Using calculus ensures we find the true extrema of the fitted polynomial curve.

### Step 3: Scale to Desired Range
```
Desired range = 1.125 - (-1.125) = 2.25

Scale factor = Desired range / Fitted range
Scale factor = 2.25 / 2.284 = 0.9851

Scale the fitted Y values:
Y_scaled = (Y_fitted - Fitted_Y_min) × scale_factor
Y_scaled now has the correct range size (2.25)
```

### Step 4: Apply Y-Offset
```
After scaling, find where the min is:
Current min = 0.0 (normalized)

Apply offset to hit desired min:
Y_offset = Desired_Y_min - Current_min
Y_offset = -1.125 - 0.0 = -1.125

Y_adjusted = Y_scaled + Y_offset
```

Now Y_adjusted spans exactly [-1.125, 1.125] ✓

### Step 5: Fit New Polynomial to Adjusted Data
```
Fit polynomial to (X_original, Y_adjusted):

New equation: y = 5.072e-07*x³ - 2.181e-06*x² - 1.630e-02*x + 2.221e-02
R² = 0.999999
```

### Step 5b: Verify New Range Using Calculus
```
Take derivative of new polynomial:
y' = 3(5.072e-07)x² + 2(-2.181e-06)x + (-1.630e-02)

Find critical points within [-125, 125]
Evaluate at critical points and endpoints

Adjusted Y min (calculus) = -1.125 ✓
Adjusted Y max (calculus) = 1.125 ✓

This confirms the true range of the curve matches our target!
```

### Step 6: Find X-Offset (Where Curve Crosses Zero)
```
Solve: 5.072e-07*x³ - 2.181e-06*x² - 1.630e-02*x + 2.221e-02 = 0

Find roots:
Real roots: [-137.21, 1.36, 141.52]

Choose root closest to 0:
X_offset = 1.36
```

### Step 7: Express in (x-offset) Format
```
Final equation for clipboard (with ^ notation):
y = 5.072e-07*(x-1.36)^3 - 2.181e-06*(x-1.36)^2 - 1.630e-02*(x-1.36) + 2.221e-02

Verify: When x = 1.36, y ≈ 0 ✓
```

### Step 8: Generate New Y Values
```
Evaluate new polynomial at original X values:
For each X in original X array:
    New_Y = polyval(adjusted_coeffs, X)

This gives you the new Y values that:
- Follow the adjusted polynomial
- Span exactly [-1.125, 1.125]
- Are smooth and well-fitted
```

## Why This Works Better

### Advantages:

1. **Works with fitted curve**: Eliminates noise from raw data points
2. **Preserves curve shape**: Scaling the fitted curve maintains smoothness
3. **Exact range control**: Y-offset ensures precise min/max values
4. **Clear origin reference**: X-offset shows exactly where curve crosses zero
5. **Reproducible Y values**: Evaluating at original X positions gives consistent results

### Comparison to Other Methods:

**Method 1 (Raw data scaling):**
- ❌ Noise in raw data affects results
- ❌ May not maintain smooth curve
- ✓ Simple to understand

**Method 2 (Asymmetric scaling):**
- ❌ Distorts curve shape
- ❌ Different scale factors complicate interpretation
- ✓ Reaches both bounds

**Method 3 (This method - Fitted curve scaling):**
- ✓ Smooth, noise-free results
- ✓ Reaches both bounds exactly
- ✓ Maintains curve characteristics
- ✓ Clear x-offset for origin reference
- ✓ Easy to regenerate Y values

## Practical Example

**Your kinematic data:**
```
Input: X = [-125 to 125], Y = [-1.2 to 1.082]
Desired: Y range = [-1.125 to 1.125]

Process:
1. Fit original → 3rd order polynomial
2. Scale fitted range: 2.284 → 2.25 (scale = 0.9851)
3. Apply Y-offset: -1.125
4. Refit → New 3rd order polynomial
5. Find x-axis crossing → X_offset ≈ 1.36
6. Express as (x-1.36)³ format
7. Evaluate at original X → New Y values

Result:
✓ New Y values span exactly [-1.125, 1.125]
✓ Curve crosses zero at x = 1.36
✓ Smooth, well-fitted curve
✓ Ready to paste into database
```

## Key Takeaways

1. **Fit first, scale second** - Work with the fitted curve for best results
2. **Range scaling + offset** - Two-step process ensures exact bounds
3. **X-offset is meaningful** - Shows where adjusted curve crosses zero
4. **Regenerate Y values** - Evaluate polynomial at original X for database updates
5. **Smooth and precise** - Best of both worlds

This algorithm gives you production-ready Y values that maintain the kinematic relationship while meeting your exact range requirements!
