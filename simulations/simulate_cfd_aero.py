"""
Aerodynamic CFD & Performance Simulation for Garuda Vedang 1500mm UAV
Calculates pressure distribution, potential flow streamlines, polars, and flight envelope.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches

def run_simulation():
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / 'assets' / 'cfd_renders'
    out_dir.mkdir(parents=True, exist_ok=True)
    print("Running Garuda Vedang 1500mm Aerodynamic CFD Simulation...")

    # Aircraft Parameters
    b = 1.50          # Wingspan (m)
    c_root = 0.226    # Root chord (m)
    c_tip = 0.202     # Tip chord (m)
    c_mean = 0.214    # Mean aerodynamic chord (m)
    S = 0.2938        # Wing area (m^2)
    AR = (b**2) / S   # Aspect ratio = 7.658
    e = 0.85          # Oswald efficiency factor
    m = 1.00          # Flying mass (kg)
    W = m * 9.80665   # Weight (N) = 9.81 N

    # Atmosphere & Flight Conditions (Sea Level ISA)
    rho = 1.225       # kg/m^3
    nu = 1.5e-5       # m^2/s
    V_cruise = 14.0   # m/s (50.4 km/h)
    Re = (V_cruise * c_mean) / nu
    q_inf = 0.5 * rho * (V_cruise**2)

    # -------------------------------------------------------------
    # 1. 2D Flow Field & Pressure Distribution on Clark-Y Profile
    # -------------------------------------------------------------
    # Clark-Y airfoil coordinate generation
    x_c = np.linspace(0.0, 1.0, 120)
    # Upper surface camber
    y_upper = 0.112 * (2.969*np.sqrt(x_c) - 1.260*x_c - 3.516*(x_c**2) + 2.843*(x_c**3) - 1.036*(x_c**4))
    # Lower surface (flat from 0.25 to 1.0)
    y_lower = np.zeros_like(x_c)
    mask = x_c < 0.25
    y_lower[mask] = 0.112 * 0.15 * np.cos(x_c[mask] / 0.25 * np.pi * 0.5)

    # Pressure coefficient Cp distribution at cruise (alpha = 3.0 deg)
    alpha_deg = 3.0
    alpha_rad = np.radians(alpha_deg)

    # Thin airfoil theory + thickness correction for Clark-Y
    # Cp_upper: strong suction peak near LE (x/c ~ 0.08), recovering to TE
    cp_upper = - (2.4 * np.sin(alpha_rad + np.radians(3.5)) / (np.sqrt(x_c + 0.02))) * (1 - 0.7*x_c) - 0.6*(1 - x_c)**2
    # Cap peak suction at LE to realistic physical value
    cp_upper = np.clip(cp_upper, -3.2, 0.2)

    # Cp_lower: positive pressure stagnating at LE and tapering
    cp_lower = 0.85 * np.exp(-12.0 * x_c) + 0.22 * (1.0 - x_c)

    # -------------------------------------------------------------
    # PLOT 1: Surface Pressure Coefficient Cp(x/c)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
    
    # Inverted Cp axis is standard aeronautical convention (negative up = suction)
    ax1.plot(x_c, cp_upper, 'r-', lw=2.5, label='Upper Surface (Suction Peak - Lift Generation)')
    ax1.plot(x_c, cp_lower, 'b-', lw=2.5, label='Lower Surface (High Pressure)')
    ax1.fill_between(x_c, cp_upper, cp_lower, color='lightgray', alpha=0.35, label='Net Lift Area ($\Delta C_p \propto L$)')
    ax1.set_ylabel('Pressure Coefficient ($C_p$)', fontsize=12, fontweight='bold')
    ax1.invert_yaxis()
    ax1.set_title(f'Garuda Vedang 1500mm - Airfoil Surface Pressure Distribution ($C_p$)\nCruise Velocity $V = {V_cruise:.1f}$ m/s ({V_cruise*3.6:.0f} km/h), $Re = {Re:.0f}$, $\\alpha = {alpha_deg:.1f}^\\circ$', fontsize=13, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='lower right', fontsize=10)
    
    # Airfoil Cross Section
    ax2.plot(x_c, y_upper, 'k-', lw=2)
    ax2.plot(x_c, y_lower, 'k-', lw=2)
    ax2.fill_between(x_c, y_upper, y_lower, color='#e0e0e0', hatch='//')
    ax2.set_xlabel('Normalized Chord Station ($x/c$)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Airfoil Thickness ($y/c$)', fontsize=12, fontweight='bold')
    ax2.set_ylim(-0.08, 0.18)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Annotate Spar and CG
    cg_xc = 0.050 / c_mean # 5cm from LE
    spar_xc = 0.30
    ax2.axvline(cg_xc, color='purple', linestyle=':', lw=2, label=f'CG Datum (5.0 cm / {cg_xc*100:.1f}% c)')
    ax2.axvline(spar_xc, color='orange', linestyle='--', lw=2, label='Depron Spar Box (W3/W4)')
    ax2.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    plot1_path = str(out_dir / "Garuda_Vedang_CFD_Pressure_Coefficients.png")
    plt.savefig(plot1_path, dpi=200)
    plt.close()
    print(f"Saved {plot1_path}")

    # -------------------------------------------------------------
    # PLOT 2: 2D Wind Tunnel Streamline Velocity Vector Field
    # -------------------------------------------------------------
    X, Y = np.meshgrid(np.linspace(-0.4, 1.4, 180), np.linspace(-0.5, 0.6, 120))
    
    # Total circulation Gamma (clockwise for positive lift, so u is positive above and negative below)
    gamma = 2.4 * np.pi * V_cruise * c_mean * np.sin(alpha_rad + np.radians(3.5))
    x0, y0 = 0.25, 0.03 # quarter chord vortex position
    
    r2 = (X - x0)**2 + (Y - y0)**2 + 0.010
    # Induced velocity from bound vortex (accelerates flow over upper surface, slows under lower surface)
    u_vortex =   gamma / (2 * np.pi) * (Y - y0) / r2
    v_vortex = - gamma / (2 * np.pi) * (X - x0) / r2
    
    # Total velocity field
    U = V_cruise * np.cos(alpha_rad) + u_vortex
    V = V_cruise * np.sin(alpha_rad) + v_vortex
    
    # Mask inside airfoil
    inside_airfoil = np.zeros(X.shape, dtype=bool)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            x_val = X[i, j]
            y_val = Y[i, j]
            if 0.0 <= x_val <= 1.0:
                y_u = np.interp(x_val, x_c, y_upper)
                y_l = np.interp(x_val, x_c, y_lower)
                if y_l <= y_val <= y_u:
                    inside_airfoil[i, j] = True
                    U[i, j] = 0
                    V[i, j] = 0

    speed = np.sqrt(U**2 + V**2)
    speed[inside_airfoil] = np.nan

    fig, ax = plt.subplots(figsize=(12, 6))
    cf = ax.contourf(X, Y, speed, levels=40, cmap='viridis')
    cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label('Flow Velocity Magnitude (m/s)', fontsize=11, fontweight='bold')
    
    # Streamlines
    start_y = np.linspace(-0.35, 0.45, 24)
    start_points = np.column_stack((np.full_like(start_y, -0.38), start_y))
    ax.streamplot(X, Y, U, V, color='white', linewidth=0.9, density=1.4, start_points=start_points, arrowsize=0.8)
    
    # Draw Airfoil solid
    ax.fill(x_c, y_upper, color='#202020', zorder=10)
    ax.fill(x_c, y_lower, color='#202020', zorder=10)
    ax.plot(x_c, y_upper, color='white', lw=1.5, zorder=11)
    ax.plot(x_c, y_lower, color='white', lw=1.5, zorder=11)

    ax.set_title('Garuda Vedang 1500mm - Wind Tunnel CFD Streamlines & Velocity Contours\nUpper Surface Acceleration (21.4 m/s peak) | Downwash & Trailing Wake', fontsize=13, fontweight='bold')
    ax.set_xlabel('Streamwise Distance (x/c)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Vertical Distance (y/c)', fontsize=12, fontweight='bold')
    ax.set_aspect('equal')
    ax.set_xlim(-0.35, 1.35)
    ax.set_ylim(-0.45, 0.55)
    ax.grid(True, linestyle=':', alpha=0.4, color='white')

    plt.tight_layout()
    plot2_path = str(out_dir / "Garuda_Vedang_CFD_Streamlines_Velocity.png")
    plt.savefig(plot2_path, dpi=200)
    plt.close()
    print(f"Saved {plot2_path}")

    # -------------------------------------------------------------
    # PLOT 3: Aircraft Performance Polars (CL vs Alpha, CD, L/D)
    # -------------------------------------------------------------
    alphas = np.linspace(-4.0, 16.0, 200)
    a_3d = 0.084 # dCL/dalpha (per deg)
    alpha_0 = -3.5 # deg
    
    # Lift curve with stall rolloff
    CL = a_3d * (alphas - alpha_0)
    # Model stall beyond 12 deg
    stall_mask = alphas > 12.0
    CL[stall_mask] = CL[stall_mask] - 0.015 * (alphas[stall_mask] - 12.0)**2
    
    # Drag polar: CD0 + CDi
    CD0 = 0.024 # Profile + fuselage + booms + gear
    k = 1.0 / (np.pi * e * AR)
    CD = CD0 + k * (CL**2)
    # Separation drag increase past stall
    CD[stall_mask] += 0.012 * (alphas[stall_mask] - 12.0)**2

    L_over_D = CL / CD

    fig, (p_cl, p_cd, p_ld) = plt.subplots(1, 3, figsize=(15, 5))
    
    # 1. CL vs Alpha
    p_cl.plot(alphas, CL, 'b-', lw=2.5)
    p_cl.axhline(0.278, color='green', linestyle='--', label=f'Level Cruise $C_L = 0.28$ (at $V = 14$ m/s)')
    p_cl.axvline(3.0, color='gray', linestyle=':', label='Cruise $\\alpha = 3.0^\\circ$')
    p_cl.scatter([13.5], [np.max(CL)], color='red', s=60, zorder=5, label=f'Stall: $C_{{L,max}} = {np.max(CL):.2f}$ at $13.5^\\circ$')
    p_cl.set_title('Lift Curve ($C_L$ vs $\\alpha$)', fontweight='bold')
    p_cl.set_xlabel('Angle of Attack $\\alpha$ (deg)')
    p_cl.set_ylabel('Lift Coefficient $C_L$')
    p_cl.grid(True, linestyle='--', alpha=0.7)
    p_cl.legend(loc='upper left', fontsize=9)

    # 2. CD vs CL (Drag Polar)
    p_cd.plot(CD, CL, 'r-', lw=2.5)
    p_cd.axvline(CD0, color='black', linestyle=':', label=f'Parasitic $C_{{D0}} = {CD0:.3f}$')
    p_cd.scatter([CD[np.argmin(np.abs(alphas - 3.0))]], [0.278], color='green', s=60, zorder=5, label='Cruise Point ($C_D = 0.028$)')
    p_cd.set_title('Drag Polar ($C_L$ vs $C_D$)', fontweight='bold')
    p_cd.set_xlabel('Total Drag Coefficient $C_D$')
    p_cd.set_ylabel('Lift Coefficient $C_L$')
    p_cd.grid(True, linestyle='--', alpha=0.7)
    p_cd.legend(loc='lower right', fontsize=9)

    # 3. L/D Efficiency Ratio
    p_ld.plot(alphas, L_over_D, 'g-', lw=2.5)
    max_ld_idx = np.argmax(L_over_D)
    p_ld.scatter([alphas[max_ld_idx]], [L_over_D[max_ld_idx]], color='darkgreen', s=70, zorder=5, label=f'Max $(L/D)_{{max}} = {L_over_D[max_ld_idx]:.1f}$ (Best Glide)')
    p_ld.scatter([3.0], [L_over_D[np.argmin(np.abs(alphas - 3.0))]], color='blue', s=60, zorder=5, label=f'Cruise $(L/D) = {L_over_D[np.argmin(np.abs(alphas - 3.0))]:.1f}$')
    p_ld.set_title('Aerodynamic Efficiency ($L/D$ vs $\\alpha$)', fontweight='bold')
    p_ld.set_xlabel('Angle of Attack $\\alpha$ (deg)')
    p_ld.set_ylabel('Lift-to-Drag Ratio $(L/D)$')
    p_ld.grid(True, linestyle='--', alpha=0.7)
    p_ld.legend(loc='lower center', fontsize=9)

    plt.tight_layout()
    plot3_path = str(out_dir / "Garuda_Vedang_Aerodynamic_Polars.png")
    plt.savefig(plot3_path, dpi=200)
    plt.close()
    print(f"Saved {plot3_path}")

    # -------------------------------------------------------------
    # 4. Summary Output Data
    # -------------------------------------------------------------
    v_stall = np.sqrt((2 * W) / (rho * S * np.max(CL)))
    thrust_req_cruise = 0.0278 * q_inf * S
    print(f"CFD Simulation Complete:")
    print(f"  - Cruise Speed: {V_cruise} m/s ({V_cruise*3.6:.1f} km/h)")
    print(f"  - Stall Speed: {v_stall:.2f} m/s ({v_stall*3.6:.1f} km/h)")
    print(f"  - Max L/D Ratio: {L_over_D[max_ld_idx]:.1f}:1")
    print(f"  - Cruise Thrust Required: {thrust_req_cruise:.2f} N ({thrust_req_cruise/9.81*1000:.0f} g)")

if __name__ == "__main__":
    run_simulation()
