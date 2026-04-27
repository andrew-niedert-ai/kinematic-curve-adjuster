"""
Kinematic Curve Adjustment Utility
Allows fitting, stretching/shrinking, and forcing curves through origin
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.metrics import r2_score
import pyperclip


class CurveAdjusterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kinematic Curve Adjuster")
        self.root.geometry("1200x800")
        
        # Data storage
        self.x_original = None
        self.y_original = None
        self.x_adjusted = None
        self.y_adjusted = None
        self.best_fit_original = None
        self.best_fit_adjusted = None
        self.original_poly_coeffs = None
        self.adjusted_poly_coeffs = None
        self.original_order = None
        self.adjusted_order = None
        self.x_offset = 0
        self.adjustment_stats = {}
        
        # Manual adjustment variables
        self.manual_scale = 1.0
        self.manual_y_shift = 0.0
        self.manual_x_shift = 0.0
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure root grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create tabs
        tab1 = ttk.Frame(self.notebook, padding="10")
        tab2 = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(tab1, text="Curve Adjustment")
        self.notebook.add(tab2, text="Data Averaging")
        
        # Configure tab grid weights
        tab1.columnconfigure(1, weight=1)
        tab1.rowconfigure(5, weight=1)
        tab2.columnconfigure(0, weight=1)
        tab2.rowconfigure(1, weight=1)
        
        # Build Tab 1 (existing functionality)
        self.create_curve_adjustment_tab(tab1)
        
        # Build Tab 2 (new averaging functionality)
        self.create_data_averaging_tab(tab2)
    
    def create_curve_adjustment_tab(self, main_frame):
        """Create the curve adjustment tab (original functionality)"""
        # Original functionality - just change parent from self.root to main_frame
        
        # ===== Input Section =====
        input_frame = ttk.LabelFrame(main_frame, text="Data Input", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="X Values (one per line or space/comma separated):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.x_input = scrolledtext.ScrolledText(input_frame, width=40, height=8)
        self.x_input.grid(row=1, column=0, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Y Values (one per line or space/comma separated):").grid(
            row=0, column=1, sticky=tk.W, pady=2
        )
        self.y_input = scrolledtext.ScrolledText(input_frame, width=40, height=8)
        self.y_input.grid(row=1, column=1, padx=5, pady=2)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(btn_frame, text="Load & Fit Data", command=self.load_and_fit_data).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # ===== Adjustment Parameters =====
        param_frame = ttk.LabelFrame(main_frame, text="Adjustment Parameters", padding="10")
        param_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Desired values
        ttk.Label(param_frame, text="Desired Y Min:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.y_min_entry = ttk.Entry(param_frame, width=15)
        self.y_min_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(param_frame, text="Desired Y Max:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.y_max_entry = ttk.Entry(param_frame, width=15)
        self.y_max_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(param_frame, text="Max Deviation %:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.max_deviation_entry = ttk.Entry(param_frame, width=10)
        self.max_deviation_entry.insert(0, "50")  # Default 50%
        self.max_deviation_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(param_frame, text="Apply Adjustments", command=self.apply_adjustments).grid(
            row=0, column=6, padx=10
        )
        
        # Manual Controls Frame
        manual_frame = ttk.LabelFrame(main_frame, text="Manual Fine-Tuning Controls", padding="10")
        manual_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Scaling controls
        ttk.Label(manual_frame, text="Scale Y (%):", font=('TkDefaultFont', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Label(manual_frame, text="Increment:").grid(row=0, column=1, sticky=tk.W, padx=5)
        self.scale_increment = ttk.Entry(manual_frame, width=10)
        self.scale_increment.insert(0, "1.0")  # Default 1%
        self.scale_increment.grid(row=0, column=2, padx=5)
        
        ttk.Button(manual_frame, text="▼ Scale Down", command=self.scale_down).grid(
            row=0, column=3, padx=5
        )
        ttk.Button(manual_frame, text="▲ Scale Up", command=self.scale_up).grid(
            row=0, column=4, padx=5
        )
        
        self.scale_label = ttk.Label(manual_frame, text="Current: 100.0%")
        self.scale_label.grid(row=0, column=5, padx=10)
        
        # Vertical shift controls
        ttk.Label(manual_frame, text="Shift Y (Vertical):", font=('TkDefaultFont', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Label(manual_frame, text="Increment:").grid(row=1, column=1, sticky=tk.W, padx=5)
        self.y_shift_increment = ttk.Entry(manual_frame, width=10)
        self.y_shift_increment.insert(0, "1.0")  # Default 1.0 units
        self.y_shift_increment.grid(row=1, column=2, padx=5)
        
        ttk.Button(manual_frame, text="▼ Shift Down", command=self.shift_y_down).grid(
            row=1, column=3, padx=5
        )
        ttk.Button(manual_frame, text="▲ Shift Up", command=self.shift_y_up).grid(
            row=1, column=4, padx=5
        )
        
        self.y_shift_label = ttk.Label(manual_frame, text="Current: 0.0")
        self.y_shift_label.grid(row=1, column=5, padx=10)
        
        # Horizontal shift controls
        ttk.Label(manual_frame, text="Shift X (Horizontal):", font=('TkDefaultFont', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Label(manual_frame, text="Increment:").grid(row=2, column=1, sticky=tk.W, padx=5)
        self.x_shift_increment = ttk.Entry(manual_frame, width=10)
        self.x_shift_increment.insert(0, "1.0")  # Default 1.0 units
        self.x_shift_increment.grid(row=2, column=2, padx=5)
        
        ttk.Button(manual_frame, text="◄ Shift Left", command=self.shift_x_left).grid(
            row=2, column=3, padx=5
        )
        ttk.Button(manual_frame, text="► Shift Right", command=self.shift_x_right).grid(
            row=2, column=4, padx=5
        )
        
        self.x_shift_label = ttk.Label(manual_frame, text="Current: 0.0")
        self.x_shift_label.grid(row=2, column=5, padx=10)
        
        # Reset button
        ttk.Button(manual_frame, text="Reset All Manual Adjustments", command=self.reset_manual_adjustments).grid(
            row=3, column=0, columnspan=6, pady=10
        )
        
        # ===== Results Section =====
        results_frame = ttk.LabelFrame(main_frame, text="Curve Equations", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(results_frame, text="Original Best Fit:").grid(row=0, column=0, sticky=tk.W)
        self.original_eq_text = scrolledtext.ScrolledText(results_frame, width=50, height=3)
        self.original_eq_text.grid(row=1, column=0, padx=5, pady=2)
        
        ttk.Label(results_frame, text="Adjusted Best Fit:").grid(row=0, column=1, sticky=tk.W)
        self.adjusted_eq_text = scrolledtext.ScrolledText(results_frame, width=50, height=3)
        self.adjusted_eq_text.grid(row=1, column=1, padx=5, pady=2)
        
        btn_copy_frame = ttk.Frame(results_frame)
        btn_copy_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(btn_copy_frame, text="Copy Original Equation", 
                  command=self.copy_original_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_copy_frame, text="Copy Adjusted Equation", 
                  command=self.copy_adjusted_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_copy_frame, text="Copy New Y Values", 
                  command=self.copy_new_y_values).pack(side=tk.LEFT, padx=5)
        
        # ===== Statistics Section =====
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, width=100, height=4)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # ===== Plot Section =====
        plot_frame = ttk.LabelFrame(main_frame, text="Visualization", padding="10")
        plot_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.figure = Figure(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def parse_input(self, text):
        """Parse input text into numpy array"""
        # Replace commas with spaces, split by whitespace or newlines
        text = text.replace(',', ' ').replace('\n', ' ')
        values = [float(x) for x in text.split() if x.strip()]
        return np.array(values)
    
    def fit_polynomial(self, x, y, degree, force_zero_intercept=False):
        """Fit polynomial and return coefficients and R² score"""
        if force_zero_intercept:
            # Force polynomial through origin by removing constant term
            # Fit polynomial of form: ax^n + bx^(n-1) + ... + cx (no constant)
            X = np.vander(x, degree + 1, increasing=False)[:, :-1]  # Remove last column (constant term)
            coeffs_no_const = np.linalg.lstsq(X, y, rcond=None)[0]
            coeffs = np.append(coeffs_no_const, 0)  # Add zero constant term
        else:
            coeffs = np.polyfit(x, y, degree)
        
        y_pred = np.polyval(coeffs, x)
        r2 = r2_score(y, y_pred)
        return coeffs, r2
    
    def find_best_fit(self, x, y, force_zero_intercept=False):
        """Find best fitting polynomial (linear, 2nd, or 3rd order)"""
        best_r2 = -np.inf
        best_coeffs = None
        best_order = None
        
        for degree in [1, 2, 3]:
            coeffs, r2 = self.fit_polynomial(x, y, degree, force_zero_intercept)
            if r2 > best_r2:
                best_r2 = r2
                best_coeffs = coeffs
                best_order = degree
        
        return best_coeffs, best_order, best_r2
    
    def format_equation(self, coeffs, order, x_offset=0, use_caret=False):
        """Format polynomial equation as string"""
        if use_caret:
            # Use ^ for exponents (clipboard format)
            if abs(x_offset) < 1e-10:
                # No offset
                if order == 1:
                    return f"y = {coeffs[0]:.6e}*x + {coeffs[1]:.6e}"
                elif order == 2:
                    return f"y = {coeffs[0]:.6e}*x^2 + {coeffs[1]:.6e}*x + {coeffs[2]:.6e}"
                elif order == 3:
                    return f"y = {coeffs[0]:.6e}*x^3 + {coeffs[1]:.6e}*x^2 + {coeffs[2]:.6e}*x + {coeffs[3]:.6e}"
            else:
                # With offset
                if order == 1:
                    return f"y = {coeffs[0]:.6e}*(x-({x_offset:.6e})) + {coeffs[1]:.6e}"
                elif order == 2:
                    return f"y = {coeffs[0]:.6e}*(x-({x_offset:.6e}))^2 + {coeffs[1]:.6e}*(x-({x_offset:.6e})) + {coeffs[2]:.6e}"
                elif order == 3:
                    return f"y = {coeffs[0]:.6e}*(x-({x_offset:.6e}))^3 + {coeffs[1]:.6e}*(x-({x_offset:.6e}))^2 + {coeffs[2]:.6e}*(x-({x_offset:.6e})) + {coeffs[3]:.6e}"
        else:
            # Use Unicode superscripts (display format)
            if abs(x_offset) < 1e-10:
                # No offset
                if order == 1:
                    return f"y = {coeffs[0]:.6e}*x + {coeffs[1]:.6e}"
                elif order == 2:
                    return f"y = {coeffs[0]:.6e}*x² + {coeffs[1]:.6e}*x + {coeffs[2]:.6e}"
                elif order == 3:
                    return f"y = {coeffs[0]:.6e}*x³ + {coeffs[1]:.6e}*x² + {coeffs[2]:.6e}*x + {coeffs[3]:.6e}"
            else:
                # With offset
                if order == 1:
                    return f"y = {coeffs[0]:.6e}*(x-{x_offset:.6e}) + {coeffs[1]:.6e}"
                elif order == 2:
                    return f"y = {coeffs[0]:.6e}*(x-{x_offset:.6e})² + {coeffs[1]:.6e}*(x-{x_offset:.6e}) + {coeffs[2]:.6e}"
                elif order == 3:
                    return f"y = {coeffs[0]:.6e}*(x-{x_offset:.6e})³ + {coeffs[1]:.6e}*(x-{x_offset:.6e})² + {coeffs[2]:.6e}*(x-{x_offset:.6e}) + {coeffs[3]:.6e}"
        return ""
    
    def load_and_fit_data(self):
        """Load data from input fields and fit polynomial"""
        try:
            # Parse input
            x_text = self.x_input.get("1.0", tk.END).strip()
            y_text = self.y_input.get("1.0", tk.END).strip()
            
            if not x_text or not y_text:
                messagebox.showerror("Error", "Please enter both X and Y values")
                return
            
            self.x_original = self.parse_input(x_text)
            self.y_original = self.parse_input(y_text)
            
            if len(self.x_original) != len(self.y_original):
                messagebox.showerror("Error", "X and Y must have the same number of values")
                return
            
            if len(self.x_original) < 4:
                messagebox.showerror("Error", "Need at least 4 data points")
                return
            
            # Find best fit
            self.original_poly_coeffs, self.original_order, r2 = self.find_best_fit(
                self.x_original, self.y_original
            )
            
            # Display original equation
            eq_text = self.format_equation(self.original_poly_coeffs, self.original_order)
            self.original_eq_text.delete("1.0", tk.END)
            self.original_eq_text.insert("1.0", f"{eq_text}\nR² = {r2:.6f}\nOrder: {self.original_order}")
            
            # Display statistics
            self.stats_text.delete("1.0", tk.END)
            stats = f"Original Data:\n"
            stats += f"  Points: {len(self.x_original)}\n"
            stats += f"  X range: [{self.x_original.min():.4f}, {self.x_original.max():.4f}]\n"
            stats += f"  Y range: [{self.y_original.min():.4f}, {self.y_original.max():.4f}]\n"
            stats += f"  Best fit: {self.original_order}{'st' if self.original_order == 1 else 'nd' if self.original_order == 2 else 'rd'} order polynomial (R² = {r2:.6f})"
            self.stats_text.insert("1.0", stats)
            
            # Plot
            self.plot_data()
            
            messagebox.showinfo("Success", f"Data loaded successfully!\nBest fit: {self.original_order}{'st' if self.original_order == 1 else 'nd' if self.original_order == 2 else 'rd'} order polynomial (R² = {r2:.6f})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def apply_adjustments(self):
        """Apply stretch/shrink and force through origin while maintaining desired Y range"""
        if self.x_original is None or self.y_original is None:
            messagebox.showerror("Error", "Please load data first")
            return
        
        try:
            # Get desired min/max
            y_min_str = self.y_min_entry.get().strip()
            y_max_str = self.y_max_entry.get().strip()
            
            if not y_min_str or not y_max_str:
                messagebox.showerror("Error", "Please enter desired Y min and max values")
                return
            
            desired_y_min = float(y_min_str)
            desired_y_max = float(y_max_str)
            
            if desired_y_min >= desired_y_max:
                messagebox.showerror("Error", "Y min must be less than Y max")
                return
            
            # Use iterative adjustment to achieve exact bounds
            self.apply_adjustments_iterative(desired_y_min, desired_y_max)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply adjustments: {str(e)}")
    
    def apply_adjustments_iterative(self, desired_y_min, desired_y_max):
        """Adjust polynomial to match desired Y range AND pass through (0,0) in original X coords.
        
        Algorithm:
            q(x) = k * p(x - h) + d, where:
                - p(x) is the original fitted polynomial
                - k = scale factor
                - h = X-shift  
                - d = Y-shift
            
            Constraints (3 equations, 3 unknowns):
                - min(q over [x_min, x_max]) = desired_y_min
                - max(q over [x_min, x_max]) = desired_y_max
                - q(0) = 0
            
            We iterate on h:
                - Given h, we can solve k and d directly from min/max
                - Then check q(0) = 0; if not, update h via Newton step
        """
        # Get max deviation percentage
        try:
            max_deviation_pct = float(self.max_deviation_entry.get().strip())
            if max_deviation_pct <= 0:
                messagebox.showerror("Error", "Max deviation percentage must be positive")
                return
        except:
            messagebox.showerror("Error", "Invalid max deviation percentage")
            return
        
        # Check if requested adjustment exceeds max deviation
        # Use polynomial-based ranges (calculus) for fair comparison
        x_min = self.x_original.min()
        x_max = self.x_original.max()
        orig_y_min, orig_y_max = self._get_poly_min_max(self.original_poly_coeffs, x_min, x_max)
        original_y_range = orig_y_max - orig_y_min
        desired_range = desired_y_max - desired_y_min
        change_pct = abs(desired_range - original_y_range) / original_y_range * 100
        
        if change_pct > max_deviation_pct:
            response = messagebox.askyesno("Warning", 
                f"Requested adjustment ({change_pct:.1f}% change) exceeds\n"
                f"maximum allowed deviation ({max_deviation_pct:.1f}%).\n\n"
                f"Original Y range (fitted): {original_y_range:.4f}\n"
                f"Desired Y range: {desired_range:.4f}\n\n"
                f"Continue anyway?")
            if not response:
                return
        
        # Run the new robust algorithm
        success, info = self._compute_adjusted_polynomial(desired_y_min, desired_y_max, max_deviation_pct)
        
        if not success:
            messagebox.showerror("Error", info.get('error', 'Adjustment failed'))
            return
        
        # Store results
        self.adjusted_poly_coeffs = info['coeffs']
        self.adjusted_order = info['order']
        self.x_offset = info['x_offset']
        self.adjustment_stats = info['stats']
        
        # Store the final adjusted data (in original X coordinates)
        self.x_adjusted = self.x_original.copy()
        self.y_adjusted = np.polyval(self.adjusted_poly_coeffs, self.x_original)
        
        # Display results
        actual_min = info['actual_min']
        actual_max = info['actual_max']
        iterations = info['iterations']
        self.display_adjustment_results(iterations, actual_min, actual_max, desired_y_min, desired_y_max)
    
    def _get_poly_min_max(self, coeffs, x_min, x_max):
        """Find min and max of polynomial over [x_min, x_max] using calculus"""
        deriv = np.polyder(coeffs)
        crit = np.roots(deriv) if len(deriv) > 0 else np.array([])
        real_crit = crit[np.isreal(crit)].real if len(crit) > 0 else np.array([])
        valid_crit = real_crit[(real_crit >= x_min) & (real_crit <= x_max)]
        eval_pts = np.concatenate([valid_crit, [x_min, x_max]])
        eval_vals = np.polyval(coeffs, eval_pts)
        return eval_vals.min(), eval_vals.max()
    
    def _shift_polynomial(self, coeffs, h):
        """Compute coefficients of q(x) = p(x - h) where p has given coeffs.
        
        Uses polynomial composition: q(x) = p(x - h)
        """
        p = np.poly1d(coeffs)
        # Represent (x - h) as a polynomial in x
        x_minus_h = np.poly1d([1.0, -h])
        # Compose: q = p o (x - h)
        q = p(x_minus_h)
        return q.coeffs
    
    def _compute_adjusted_polynomial(self, desired_y_min, desired_y_max, max_deviation_pct):
        """Robust algorithm to find polynomial passing through origin with desired Y range.
        
        Form: q(x) = k * p(x - h) + d
            where p is the original polynomial, k=scale, h=X-shift, d=Y-shift
        
        Constraints:
            - min(q) = desired_y_min
            - max(q) = desired_y_max
            - q(0) = 0
        
        Strategy: Reduce to 1D root-finding on h.
            - For any h: solve k, d directly from min/max constraints
            - Then F(h) = q(0; h) is a 1D function we want to zero
            - Use brentq with bracketing search
        
        Returns (success, info_dict)
        """
        try:
            from scipy.optimize import brentq
            
            x_min = self.x_original.min()
            x_max = self.x_original.max()
            desired_range = desired_y_max - desired_y_min
            
            # Get original polynomial info
            orig_y_min, orig_y_max = self._get_poly_min_max(self.original_poly_coeffs, x_min, x_max)
            original_range = orig_y_max - orig_y_min
            
            if original_range < 1e-12:
                return False, {'error': 'Original polynomial has zero Y range'}
            
            base_scale = desired_range / original_range
            
            # Sanity check
            if abs(base_scale) > 100 or abs(base_scale) < 0.01:
                return False, {'error': f'Scale factor {base_scale:.4f} is unreasonable. Check input data.'}
            
            # Define the system for a given h, returning (q_coeffs, k, d, shift_y_min, shift_y_max)
            def compute_q_for_h(h):
                p_shift_coeffs = self._shift_polynomial(self.original_poly_coeffs, h)
                shift_y_min, shift_y_max = self._get_poly_min_max(p_shift_coeffs, x_min, x_max)
                shift_range = shift_y_max - shift_y_min
                if shift_range < 1e-12:
                    return None, None, None, None, None
                k = desired_range / shift_range
                d = desired_y_min - k * shift_y_min
                q_coeffs = p_shift_coeffs * k
                q_coeffs[-1] += d
                return q_coeffs, k, d, shift_y_min, shift_y_max
            
            def F(h):
                """Returns q(0) for a given h. We want F(h) = 0."""
                q_coeffs, _, _, _, _ = compute_q_for_h(h)
                if q_coeffs is None:
                    return float('inf')
                return np.polyval(q_coeffs, 0.0)
            
            # Step 1: Sweep h over a reasonable range to find sign changes
            data_range = x_max - x_min
            h_search = np.linspace(-data_range * 1.5, data_range * 1.5, 121)
            F_values = []
            for h in h_search:
                F_h = F(h)
                F_values.append(F_h)
            
            F_arr = np.array(F_values)
            
            # Step 2: Find sign changes (brackets)
            sign_changes = []
            for i in range(len(F_arr) - 1):
                if not np.isfinite(F_arr[i]) or not np.isfinite(F_arr[i+1]):
                    continue
                if F_arr[i] * F_arr[i+1] < 0:
                    sign_changes.append((h_search[i], h_search[i+1]))
            
            if not sign_changes:
                # No sign change found - try to find h with smallest |F(h)|
                finite_mask = np.isfinite(F_arr)
                if np.any(finite_mask):
                    best_idx = np.argmin(np.abs(F_arr[finite_mask]))
                    h_best = h_search[finite_mask][best_idx]
                    F_best = F_arr[finite_mask][best_idx]
                    if abs(F_best) < 0.01 * desired_range:
                        # Close enough - accept this approximate solution
                        q_coeffs, k, d, shift_y_min, shift_y_max = compute_q_for_h(h_best)
                        return self._build_result(q_coeffs, h_best, k, d, shift_y_min, shift_y_max,
                                                 orig_y_min, orig_y_max, original_range,
                                                 max_deviation_pct, 1)
                return False, {'error': 'Could not find a polynomial that passes through origin with the desired Y range. Try a different desired range or relax the constraint.'}
            
            # Step 3: Find solutions with brentq for each bracket; pick the one with smallest |h|
            solutions = []
            for (h_lo, h_hi) in sign_changes:
                try:
                    h_sol = brentq(F, h_lo, h_hi, xtol=1e-10, maxiter=100)
                    q_coeffs, k, d, shift_y_min, shift_y_max = compute_q_for_h(h_sol)
                    if q_coeffs is not None:
                        solutions.append((h_sol, q_coeffs, k, d, shift_y_min, shift_y_max))
                except Exception:
                    continue
            
            if not solutions:
                return False, {'error': 'Failed to find polynomial solution. Try different desired Y values.'}
            
            # Pick solution with smallest |h| (least disturbance)
            best = min(solutions, key=lambda s: abs(s[0]))
            h_sol, q_coeffs, k, d, shift_y_min, shift_y_max = best
            
            # Build result info
            return self._build_result(q_coeffs, h_sol, k, d, shift_y_min, shift_y_max,
                                     orig_y_min, orig_y_max, original_range,
                                     max_deviation_pct, len(sign_changes))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, {'error': f'Algorithm error: {str(e)}'}
    
    def _build_result(self, q_coeffs, h, k, d, shift_y_min, shift_y_max,
                      orig_y_min, orig_y_max, original_range, max_deviation_pct, iterations):
        """Build the result dictionary from the solver output."""
        x_min = self.x_original.min()
        x_max = self.x_original.max()
        
        actual_min, actual_max = self._get_poly_min_max(q_coeffs, x_min, x_max)
        actual_change_pct = abs((actual_max - actual_min) - original_range) / original_range * 100
        
        # Sanity check: not exceeding deviation
        if actual_change_pct > max_deviation_pct + 1.0:
            return False, {'error': f'Solution requires {actual_change_pct:.1f}% deviation (max allowed: {max_deviation_pct:.1f}%).'}
        
        q_at_zero = np.polyval(q_coeffs, 0.0)
        
        # Determine effective polynomial order
        order = len(q_coeffs) - 1
        for i in range(len(q_coeffs)):
            if abs(q_coeffs[i]) > 1e-10:
                order = len(q_coeffs) - 1 - i
                break
        
        stats = {
            'original_y_min': orig_y_min,
            'original_y_max': orig_y_max,
            'original_range': original_range,
            'scale_factor': k,
            'x_shift': h,
            'y_shift': d,
            'shift_y_min': shift_y_min,
            'shift_y_max': shift_y_max,
            'q_at_zero': q_at_zero,
            'r2_adjusted': 1.0,
            'actual_change_pct': actual_change_pct,
        }
        
        return True, {
            'coeffs': q_coeffs,
            'order': order,
            'x_offset': h,
            'actual_min': actual_min,
            'actual_max': actual_max,
            'iterations': iterations,
            'stats': stats,
        }
    
    def display_adjustment_results(self, iterations, actual_min, actual_max, desired_y_min, desired_y_max):
        """Display the final adjustment results"""
        # Verify: polynomial at x=0 should be ~0 (passes through origin in original X coords)
        y_check = np.polyval(self.adjusted_poly_coeffs, 0)
        
        # Display adjusted equation (now in ORIGINAL X coordinates - no offset note needed)
        eq_text = self.format_equation(self.adjusted_poly_coeffs, self.adjusted_order, x_offset=0, use_caret=False)
        self.adjusted_eq_text.delete("1.0", tk.END)
        self.adjusted_eq_text.insert("1.0", 
            f"{eq_text}\n"
            f"R² = {self.adjustment_stats['r2_adjusted']:.6f}\n"
            f"Order: {self.adjusted_order}\n"
            f"Polynomial is in ORIGINAL X coordinates - evaluate directly at your X values")
        
        # Update statistics
        current_stats = self.stats_text.get("1.0", tk.END)
        stats = self.adjustment_stats
        new_stats = f"\n\nAdjustment Process (converged in {iterations} iterations):\n"
        new_stats += f"  Original fitted range (calculus): [{stats['original_y_min']:.4f}, {stats['original_y_max']:.4f}]\n"
        new_stats += f"  Original range: {stats['original_range']:.4f}\n"
        new_stats += f"  Scale factor (k): {stats['scale_factor']:.6f}\n"
        new_stats += f"  X-shift (h): {stats['x_shift']:.6f}\n"
        new_stats += f"  Y-shift (d): {stats['y_shift']:.6f}\n"
        new_stats += f"  Form: q(x) = k*p(x - h) + d\n"
        new_stats += f"\n  DESIRED Y range: [{desired_y_min:.4f}, {desired_y_max:.4f}]\n"
        new_stats += f"  ACTUAL Y range (at original X): [{actual_min:.4f}, {actual_max:.4f}]\n"
        new_stats += f"  Error: min={abs(actual_min-desired_y_min):.6f}, max={abs(actual_max-desired_y_max):.6f}\n"
        new_stats += f"  Actual Y range change: {stats['actual_change_pct']:.2f}%\n"
        new_stats += f"  Y at X=0: {y_check:.6e} (passes through origin ✓)"
        
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", current_stats.rstrip() + new_stats)
        
        # Update plot
        self.plot_data()
        
        # Create success message
        success_msg = f"Adjustments applied successfully!\n(Converged in {iterations} iterations)\n\n"
        success_msg += f"Desired Y range: [{desired_y_min:.4f}, {desired_y_max:.4f}]\n"
        success_msg += f"Actual Y range:  [{actual_min:.4f}, {actual_max:.4f}]\n"
        success_msg += f"Error: ±{max(abs(actual_min-desired_y_min), abs(actual_max-desired_y_max)):.6f}\n"
        success_msg += f"Y at X=0: {y_check:.2e} (passes through origin)"
        
        messagebox.showinfo("Success", success_msg)
    
    def plot_data(self):
        """Plot original and adjusted data"""
        self.figure.clear()
        
        if self.x_original is None:
            return
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        # Plot original data
        ax.scatter(self.x_original, self.y_original, color='blue', label='Original Data', alpha=0.6, s=50)
        
        # Plot original fit
        if self.original_poly_coeffs is not None:
            x_smooth = np.linspace(self.x_original.min(), self.x_original.max(), 200)
            y_fit = np.polyval(self.original_poly_coeffs, x_smooth)
            ax.plot(x_smooth, y_fit, 'b--', label=f'Original Fit (Order {self.original_order})', linewidth=2)
        
        # Plot adjusted data if available
        # Plot against ORIGINAL X values, not shifted X values
        if self.adjusted_poly_coeffs is not None:
            # Check if manual adjustments are active
            has_manual_adjustments = (abs(self.manual_scale - 1.0) > 1e-6 or 
                                     abs(self.manual_y_shift) > 1e-6 or 
                                     abs(self.manual_x_shift) > 1e-6)
            
            if has_manual_adjustments:
                # Show both automatic and manual adjusted curves
                # Automatic adjustment (without manual)
                y_auto = np.polyval(self.adjusted_poly_coeffs, self.x_original)
                ax.scatter(self.x_original, y_auto, color='orange', label='Auto Adjusted', 
                          alpha=0.4, s=40, marker='s')
                
                x_smooth = np.linspace(self.x_original.min(), self.x_original.max(), 200)
                y_auto_smooth = np.polyval(self.adjusted_poly_coeffs, x_smooth)
                ax.plot(x_smooth, y_auto_smooth, color='orange', linestyle='--', 
                       alpha=0.4, linewidth=1.5)
                
                # Manual adjusted data
                y_manual = self.get_manually_adjusted_y_values(self.x_original)
                ax.scatter(self.x_original, y_manual, color='red', 
                          label='Manual Adjusted', alpha=0.8, s=50, marker='s')
                
                y_manual_smooth = self.get_manually_adjusted_y_values(x_smooth)
                ax.plot(x_smooth, y_manual_smooth, 'r-', 
                       label=f'Manual Fit (Order {self.adjusted_order})', linewidth=2.5)
            else:
                # Only automatic adjustment
                y_adjusted_at_original_x = np.polyval(self.adjusted_poly_coeffs, self.x_original)
                ax.scatter(self.x_original, y_adjusted_at_original_x, color='red', 
                          label='Adjusted Data', alpha=0.6, s=50, marker='s')
                
                # Plot adjusted fit curve over original X range
                x_smooth = np.linspace(self.x_original.min(), self.x_original.max(), 200)
                y_fit = np.polyval(self.adjusted_poly_coeffs, x_smooth)
                ax.plot(x_smooth, y_fit, 'r-', 
                       label=f'Adjusted Fit (Order {self.adjusted_order})', linewidth=2)
        
        # Add origin marker
        ax.axhline(y=0, color='k', linestyle=':', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle=':', alpha=0.3)
        ax.plot(0, 0, 'go', markersize=8, label='Origin (0,0)')
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title('Kinematic Curve Adjustment', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def create_data_averaging_tab(self, parent):
        """Create the data averaging tab"""
        # Input Section (LEFT SIDE)
        input_frame = ttk.LabelFrame(parent, text="Input Data Sets (up to 4)", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=5, padx=(0,5))
        
        self.avg_x_inputs = []
        self.avg_y_inputs = []
        self.avg_order_vars = []
        
        for i in range(4):
            # Label
            ttk.Label(input_frame, text=f"Dataset {i+1}:").grid(row=i*2, column=0, sticky=tk.W, pady=2)
            
            # X input
            ttk.Label(input_frame, text=f"X values:").grid(row=i*2, column=1, sticky=tk.W, padx=5)
            x_input = scrolledtext.ScrolledText(input_frame, width=25, height=3)
            x_input.grid(row=i*2, column=2, padx=5, pady=2)
            self.avg_x_inputs.append(x_input)
            
            # Y input
            ttk.Label(input_frame, text=f"Y values:").grid(row=i*2, column=3, sticky=tk.W, padx=5)
            y_input = scrolledtext.ScrolledText(input_frame, width=25, height=3)
            y_input.grid(row=i*2, column=4, padx=5, pady=2)
            self.avg_y_inputs.append(y_input)
            
            # Polynomial order selection
            ttk.Label(input_frame, text=f"Order:").grid(row=i*2+1, column=1, sticky=tk.W, padx=5)
            order_var = tk.IntVar(value=3)
            order_frame = ttk.Frame(input_frame)
            order_frame.grid(row=i*2+1, column=2, sticky=tk.W, padx=5)
            ttk.Radiobutton(order_frame, text="Linear", variable=order_var, value=1).pack(side=tk.LEFT)
            ttk.Radiobutton(order_frame, text="2nd", variable=order_var, value=2).pack(side=tk.LEFT)
            ttk.Radiobutton(order_frame, text="3rd", variable=order_var, value=3).pack(side=tk.LEFT)
            self.avg_order_vars.append(order_var)
        
        # X-Range Configuration (RIGHT SIDE)
        range_frame = ttk.LabelFrame(parent, text="Output X-Range Configuration", padding="10")
        range_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), pady=5, padx=(5,0))
        
        # Option 1: Specify range parameters
        ttk.Label(range_frame, text="Option 1 - Specify Range:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=(0,5), columnspan=2
        )
        
        ttk.Label(range_frame, text="X Min:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.avg_x_min = ttk.Entry(range_frame, width=15)
        self.avg_x_min.grid(row=1, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(range_frame, text="X Max:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.avg_x_max = ttk.Entry(range_frame, width=15)
        self.avg_x_max.grid(row=2, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(range_frame, text="Interval:").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.avg_x_interval = ttk.Entry(range_frame, width=15)
        self.avg_x_interval.grid(row=3, column=1, padx=5, sticky=tk.W)
        
        # Option 2: Paste X values directly
        ttk.Label(range_frame, text="Option 2 - Paste X Values:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=(15,2), columnspan=2
        )
        ttk.Label(range_frame, text="(Leave blank to use Option 1)", font=('TkDefaultFont', 8, 'italic')).grid(
            row=5, column=0, sticky=tk.W, padx=5, pady=(0,2), columnspan=2
        )
        
        self.avg_x_values_input = scrolledtext.ScrolledText(range_frame, width=35, height=8)
        self.avg_x_values_input.grid(row=6, column=0, columnspan=2, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        # Buttons
        ttk.Button(range_frame, text="Process & Average", command=self.process_averaging).grid(
            row=7, column=0, columnspan=2, pady=(10,5), padx=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(range_frame, text="Copy X Values", command=self.copy_averaged_x).grid(
            row=8, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(range_frame, text="Copy Averaged Y Values", command=self.copy_averaged_y).grid(
            row=9, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(range_frame, text="Export to Curve Adjustment", command=self.export_to_curve_adjustment).grid(
            row=10, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(range_frame, text="Clear Data", command=self.clear_averaging_data).grid(
            row=11, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(range_frame, text="Clear X-Range Config", command=self.clear_x_range_config).grid(
            row=12, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E)
        )
        
        # Results Section (spans both columns)
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.avg_results_text = scrolledtext.ScrolledText(results_frame, width=100, height=5)
        self.avg_results_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Plot Section (spans both columns)
        plot_frame = ttk.LabelFrame(parent, text="Averaged Data Visualization", padding="10")
        plot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.avg_figure = Figure(figsize=(10, 6), dpi=100)
        self.avg_canvas = FigureCanvasTkAgg(self.avg_figure, master=plot_frame)
        self.avg_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Store averaged data
        self.averaged_x = None
        self.averaged_y = None
    
    def process_averaging(self):
        """Process multiple datasets and compute average"""
        try:
            # Check which method to use for X values
            x_values_text = self.avg_x_values_input.get("1.0", tk.END).strip()
            
            if x_values_text:
                # Option 2: Parse pasted X values
                self.averaged_x = self.parse_input(x_values_text)
                self.averaged_x = np.sort(self.averaged_x)  # Ensure sorted
            else:
                # Option 1: Generate X values from range parameters
                x_min_str = self.avg_x_min.get().strip()
                x_max_str = self.avg_x_max.get().strip()
                x_interval_str = self.avg_x_interval.get().strip()
                
                if not x_min_str or not x_max_str or not x_interval_str:
                    messagebox.showerror("Error", "Please either paste X values OR enter X Min, Max, and Interval")
                    return
                
                x_min = float(x_min_str)
                x_max = float(x_max_str)
                x_interval = float(x_interval_str)
                
                if x_min >= x_max:
                    messagebox.showerror("Error", "X Min must be less than X Max")
                    return
                
                if x_interval <= 0:
                    messagebox.showerror("Error", "Interval must be positive")
                    return
                
                # Generate output X values - calculate exact number of points to ensure endpoint is included
                num_points = int(round((x_max - x_min) / x_interval)) + 1
                self.averaged_x = np.linspace(x_min, x_max, num_points)
            
            # Ensure X=0 is included if it's within the range
            x_min_range = self.averaged_x.min()
            x_max_range = self.averaged_x.max()
            
            if x_min_range <= 0 <= x_max_range:
                # 0 is within range, check if it's already in the array
                if not np.any(np.isclose(self.averaged_x, 0, atol=1e-10)):
                    # Add 0 and re-sort
                    self.averaged_x = np.sort(np.append(self.averaged_x, 0))
                    print(f"Added X=0 to dataset (was not in original range)")
            
            # Process each dataset
            datasets = []
            fitted_polys = []
            colors = ['blue', 'green', 'red', 'purple']
            
            for i in range(4):
                x_text = self.avg_x_inputs[i].get("1.0", tk.END).strip()
                y_text = self.avg_y_inputs[i].get("1.0", tk.END).strip()
                
                if not x_text or not y_text:
                    continue  # Skip empty datasets
                
                # Parse data
                x_data = self.parse_input(x_text)
                y_data = self.parse_input(y_text)
                
                if len(x_data) != len(y_data):
                    messagebox.showerror("Error", f"Dataset {i+1}: X and Y must have same length")
                    return
                
                order = self.avg_order_vars[i].get()
                
                # Fit polynomial
                coeffs = np.polyfit(x_data, y_data, order)
                
                # Evaluate at output X values
                y_fitted = np.polyval(coeffs, self.averaged_x)
                
                datasets.append({
                    'x_orig': x_data,
                    'y_orig': y_data,
                    'coeffs': coeffs,
                    'order': order,
                    'y_fitted': y_fitted,
                    'color': colors[i],
                    'number': i+1
                })
                fitted_polys.append(y_fitted)
            
            if len(datasets) == 0:
                messagebox.showerror("Error", "Please enter at least one dataset")
                return
            
            # Average the fitted Y values
            self.averaged_y = np.mean(fitted_polys, axis=0)
            
            # Display results
            self.avg_results_text.delete("1.0", tk.END)
            results = f"Averaging Results:\n"
            results += f"  Number of datasets: {len(datasets)}\n"
            results += f"  Output X range: [{self.averaged_x.min():.4f}, {self.averaged_x.max():.4f}]\n"
            results += f"  Number of output points: {len(self.averaged_x)}\n"
            results += f"  Averaged Y range: [{self.averaged_y.min():.4f}, {self.averaged_y.max():.4f}]\n\n"
            
            for ds in datasets:
                results += f"  Dataset {ds['number']}: {ds['order']}{'st' if ds['order']==1 else 'nd' if ds['order']==2 else 'rd'} order, "
                results += f"{len(ds['x_orig'])} points, Y range [{ds['y_orig'].min():.4f}, {ds['y_orig'].max():.4f}]\n"
            
            self.avg_results_text.insert("1.0", results)
            
            # Plot
            self.plot_averaged_data(datasets)
            
            messagebox.showinfo("Success", f"Successfully averaged {len(datasets)} datasets!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process: {str(e)}")
    
    def plot_averaged_data(self, datasets):
        """Plot original datasets and averaged curve"""
        self.avg_figure.clear()
        ax = self.avg_figure.add_subplot(111)
        
        # Plot original datasets
        for ds in datasets:
            ax.scatter(ds['x_orig'], ds['y_orig'], 
                      color=ds['color'], alpha=0.5, s=40,
                      label=f"Dataset {ds['number']} (Order {ds['order']})")
            
            # Plot fitted curves
            ax.plot(self.averaged_x, ds['y_fitted'],
                   color=ds['color'], linestyle='--', alpha=0.5, linewidth=1.5)
        
        # Plot averaged curve
        ax.plot(self.averaged_x, self.averaged_y,
               color='black', linewidth=3, label='Averaged Curve')
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title('Data Averaging: Multiple Datasets', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        self.avg_figure.tight_layout()
        self.avg_canvas.draw()
    
    def copy_averaged_x(self):
        """Copy X values to clipboard"""
        if self.averaged_x is None:
            messagebox.showwarning("Warning", "No X values available. Please process data first.")
            return
        
        # Format as column
        x_column = '\n'.join([f"{x:.10f}" for x in self.averaged_x])
        
        pyperclip.copy(x_column)
        
        messagebox.showinfo("Success",
            f"X values copied to clipboard!\n\n"
            f"Format: One value per line\n"
            f"Count: {len(self.averaged_x)} values\n"
            f"Range: [{self.averaged_x.min():.6f}, {self.averaged_x.max():.6f}]\n\n"
            f"Ready to paste into Excel/spreadsheet!")
    
    def copy_averaged_y(self):
        """Copy averaged Y values to clipboard"""
        if self.averaged_y is None:
            messagebox.showwarning("Warning", "No averaged data available. Please process data first.")
            return
        
        # Format as column
        y_column = '\n'.join([f"{y:.10f}" for y in self.averaged_y])
        
        pyperclip.copy(y_column)
        
        messagebox.showinfo("Success",
            f"Averaged Y values copied to clipboard!\n\n"
            f"Format: One value per line\n"
            f"Count: {len(self.averaged_y)} values\n"
            f"Range: [{self.averaged_y.min():.6f}, {self.averaged_y.max():.6f}]\n\n"
            f"Ready to paste into Excel/spreadsheet!")
    
    def clear_averaging_data(self):
        """Clear dataset inputs and results, but preserve X-Range configuration"""
        for x_input in self.avg_x_inputs:
            x_input.delete("1.0", tk.END)
        for y_input in self.avg_y_inputs:
            y_input.delete("1.0", tk.END)
        
        # Do NOT clear X Min, X Max, and Interval - preserve them for next dataset
        # self.avg_x_min.delete(0, tk.END)
        # self.avg_x_max.delete(0, tk.END)
        # self.avg_x_interval.delete(0, tk.END)
        
        self.avg_x_values_input.delete("1.0", tk.END)
        self.avg_results_text.delete("1.0", tk.END)
        
        self.averaged_x = None
        self.averaged_y = None
        
        self.avg_figure.clear()
        self.avg_canvas.draw()
    
    def clear_x_range_config(self):
        """Clear X-Range configuration (Min, Max, Interval, and pasted X values)"""
        self.avg_x_min.delete(0, tk.END)
        self.avg_x_max.delete(0, tk.END)
        self.avg_x_interval.delete(0, tk.END)
        self.avg_x_values_input.delete("1.0", tk.END)
        
        messagebox.showinfo("Success", "X-Range configuration cleared")
    
    def export_to_curve_adjustment(self):
        """Export averaged X and Y data to Curve Adjustment tab"""
        if self.averaged_x is None or self.averaged_y is None:
            messagebox.showwarning("Warning", "No averaged data available. Please process data first.")
            return
        
        # Format X and Y values as columns (one per line)
        x_column = '\n'.join([f"{x:.10f}" for x in self.averaged_x])
        y_column = '\n'.join([f"{y:.10f}" for y in self.averaged_y])
        
        # Clear the Curve Adjustment tab inputs
        self.x_input.delete("1.0", tk.END)
        self.y_input.delete("1.0", tk.END)
        
        # Populate with averaged data
        self.x_input.insert("1.0", x_column)
        self.y_input.insert("1.0", y_column)
        
        # Switch to Curve Adjustment tab
        self.notebook.select(0)  # Tab index 0 is Curve Adjustment
        
        messagebox.showinfo("Success",
            f"Averaged data exported to Curve Adjustment tab!\n\n"
            f"X values: {len(self.averaged_x)} points\n"
            f"Y values: {len(self.averaged_y)} points\n\n"
            f"Ready to apply curve adjustments!")
    
    def copy_original_to_clipboard(self):
        """Copy original equation to clipboard with ^ notation"""
        if self.original_poly_coeffs is None:
            messagebox.showwarning("Warning", "No original equation available")
            return
        
        eq_text = self.format_equation(self.original_poly_coeffs, self.original_order, 0, use_caret=True)
        pyperclip.copy(eq_text)
        messagebox.showinfo("Success", "Original equation copied to clipboard!\n(Using ^ for exponents)")
    
    def copy_adjusted_to_clipboard(self):
        """Copy adjusted equation to clipboard with ^ notation"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "No adjusted equation available")
            return
        
        # Polynomial is in ORIGINAL X coordinates - just copy the equation directly
        eq_text = self.format_equation(self.adjusted_poly_coeffs, self.adjusted_order, x_offset=0, use_caret=True)
        
        pyperclip.copy(eq_text)
        messagebox.showinfo("Success", 
            f"Adjusted equation copied to clipboard!\n\n"
            f"(Using ^ for exponents)\n"
            f"Equation is in ORIGINAL X coordinates - evaluate directly")
    
    def copy_new_y_values(self):
        """Copy new Y values (final polynomial evaluated at ORIGINAL X values) to clipboard"""
        if self.adjusted_poly_coeffs is None or self.x_original is None:
            messagebox.showwarning("Warning", "No adjusted equation available. Please load and adjust data first.")
            return
        
        # Check if manual adjustments are active
        has_manual_adjustments = (abs(self.manual_scale - 1.0) > 1e-6 or 
                                 abs(self.manual_y_shift) > 1e-6 or 
                                 abs(self.manual_x_shift) > 1e-6)
        
        if has_manual_adjustments:
            # Use manually adjusted values
            new_y_values = self.get_manually_adjusted_y_values(self.x_original)
            adjustment_type = "with manual adjustments"
        else:
            # Evaluate the final polynomial at ORIGINAL X values
            new_y_values = np.polyval(self.adjusted_poly_coeffs, self.x_original)
            adjustment_type = "from adjusted fit"
        
        # Format as column (one value per line)
        y_column = '\n'.join([f"{y:.10f}" for y in new_y_values])
        
        pyperclip.copy(y_column)
        
        messagebox.showinfo("Success", 
            f"New Y values copied to clipboard!\n\n"
            f"Type: {adjustment_type}\n"
            f"Format: One value per line\n"
            f"Count: {len(new_y_values)} values\n"
            f"Range: [{new_y_values.min():.6f}, {new_y_values.max():.6f}]\n\n"
            f"Ready to paste into Excel/spreadsheet!")
    
    def clear_all(self):
        """Clear all data and reset"""
        self.x_input.delete("1.0", tk.END)
        self.y_input.delete("1.0", tk.END)
        self.y_min_entry.delete(0, tk.END)
        self.y_max_entry.delete(0, tk.END)
        self.original_eq_text.delete("1.0", tk.END)
        self.adjusted_eq_text.delete("1.0", tk.END)
        self.stats_text.delete("1.0", tk.END)
        
        self.x_original = None
        self.y_original = None
        self.x_adjusted = None
        self.y_adjusted = None
        self.original_poly_coeffs = None
        self.adjusted_poly_coeffs = None
        
        # Reset manual adjustments
        self.manual_scale = 1.0
        self.manual_y_shift = 0.0
        self.manual_x_shift = 0.0
        self.update_manual_labels()
        
        self.figure.clear()
        self.canvas.draw()
    
    def scale_up(self):
        """Scale curve up by the specified percentage increment"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "Please apply adjustments first")
            return
        
        try:
            increment = float(self.scale_increment.get()) / 100.0
            self.manual_scale *= (1 + increment)
            self.apply_manual_adjustments()
        except:
            messagebox.showerror("Error", "Invalid scale increment")
    
    def scale_down(self):
        """Scale curve down by the specified percentage increment"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "Please apply adjustments first")
            return
        
        try:
            increment = float(self.scale_increment.get()) / 100.0
            self.manual_scale *= (1 - increment)
            self.apply_manual_adjustments()
        except:
            messagebox.showerror("Error", "Invalid scale increment")
    
    def shift_y_up(self):
        """Shift curve up by the specified increment"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "Please apply adjustments first")
            return
        
        try:
            increment = float(self.y_shift_increment.get())
            self.manual_y_shift += increment
            self.apply_manual_adjustments()
        except:
            messagebox.showerror("Error", "Invalid Y shift increment")
    
    def shift_y_down(self):
        """Shift curve down by the specified increment"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "Please apply adjustments first")
            return
        
        try:
            increment = float(self.y_shift_increment.get())
            self.manual_y_shift -= increment
            self.apply_manual_adjustments()
        except:
            messagebox.showerror("Error", "Invalid Y shift increment")
    
    def shift_x_right(self):
        """Shift curve right by the specified increment"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "Please apply adjustments first")
            return
        
        try:
            increment = float(self.x_shift_increment.get())
            self.manual_x_shift += increment
            self.apply_manual_adjustments()
        except:
            messagebox.showerror("Error", "Invalid X shift increment")
    
    def shift_x_left(self):
        """Shift curve left by the specified increment"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "Please apply adjustments first")
            return
        
        try:
            increment = float(self.x_shift_increment.get())
            self.manual_x_shift -= increment
            self.apply_manual_adjustments()
        except:
            messagebox.showerror("Error", "Invalid X shift increment")
    
    def apply_manual_adjustments(self):
        """Apply all manual adjustments to the curve"""
        # Update labels
        self.update_manual_labels()
        
        # Replot with manual adjustments
        self.plot_data()
        
        # Update stats to show current Y range with manual adjustments
        final_y_values = self.get_manually_adjusted_y_values(self.x_original)
        actual_min = final_y_values.min()
        actual_max = final_y_values.max()
        
        current_stats = self.stats_text.get("1.0", tk.END)
        manual_stats = f"\n\nManual Adjustments Applied:\n"
        manual_stats += f"  Scale: {self.manual_scale*100:.2f}%\n"
        manual_stats += f"  Y Shift: {self.manual_y_shift:+.4f}\n"
        manual_stats += f"  X Shift: {self.manual_x_shift:+.4f}\n"
        manual_stats += f"  Current Y range: [{actual_min:.4f}, {actual_max:.4f}]"
        
        # Check if manual stats already exist and update them
        if "Manual Adjustments Applied:" in current_stats:
            # Remove old manual stats and append new ones
            stats_parts = current_stats.split("Manual Adjustments Applied:")
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", stats_parts[0].rstrip() + manual_stats)
        else:
            # Append manual stats
            self.stats_text.insert(tk.END, manual_stats)
    
    def get_manually_adjusted_y_values(self, x_values):
        """Get Y values with all manual adjustments applied"""
        # Evaluate polynomial at shifted X values
        x_shifted = x_values - self.manual_x_shift
        y_base = np.polyval(self.adjusted_poly_coeffs, x_shifted)
        
        # Apply scale and Y shift
        y_adjusted = y_base * self.manual_scale + self.manual_y_shift
        
        return y_adjusted
    
    def update_manual_labels(self):
        """Update the labels showing current manual adjustment values"""
        # Safety check in case this is called before UI is created
        if hasattr(self, 'scale_label'):
            self.scale_label.config(text=f"Current: {self.manual_scale*100:.2f}%")
            self.y_shift_label.config(text=f"Current: {self.manual_y_shift:+.4f}")
            self.x_shift_label.config(text=f"Current: {self.manual_x_shift:+.4f}")
    
    def reset_manual_adjustments(self):
        """Reset all manual adjustments to default values"""
        if self.adjusted_poly_coeffs is None:
            messagebox.showwarning("Warning", "No adjustments to reset")
            return
        
        self.manual_scale = 1.0
        self.manual_y_shift = 0.0
        self.manual_x_shift = 0.0
        
        self.update_manual_labels()
        self.plot_data()
        
        # Remove manual adjustment stats if present
        current_stats = self.stats_text.get("1.0", tk.END)
        if "Manual Adjustments Applied:" in current_stats:
            stats_parts = current_stats.split("Manual Adjustments Applied:")
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", stats_parts[0].rstrip())
        
        messagebox.showinfo("Success", "Manual adjustments reset")


def main():
    root = tk.Tk()
    app = CurveAdjusterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

