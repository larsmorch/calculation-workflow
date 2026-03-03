import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Rectangle


def beam_centered_udl_numeric_deflection_mm_kN(w_kN_per_m, a_mm, L_mm, E_Pa, I_mm4, npts=4001):
    """
    Simply supported beam with centered partial UDL, using:
      length      : mm
      force       : kN
      moment      : kN·m (returned)
      deflection  : mm (returned)

    Inputs:
      w_kN_per_m  : kN/m   (UDL intensity over length a, centered)
      a_mm, L_mm  : mm
      E_Pa        : Pa (N/m^2)
      I_mm4       : mm^4
    """
    if not (0 < a_mm <= L_mm):
        raise ValueError("a_mm must satisfy 0 < a_mm <= L_mm")

    # --- Unit conversions to a consistent internal system (N, mm) ---
    # E in Pa = N/m^2 -> N/mm^2
    E_N_per_mm2 = E_Pa / 1e6
    EI = E_N_per_mm2 * I_mm4  # N*mm^2

    # w: kN/m -> N/mm (1 kN=1000 N, 1 m=1000 mm => numerically same)
    w = w_kN_per_m  # N/mm

    # Geometry (centered UDL)
    x1 = 0.5 * (L_mm - a_mm)
    x2 = 0.5 * (L_mm + a_mm)

    x = np.linspace(0.0, L_mm, npts)
    dx = x[1] - x[0]

    # Reactions (symmetry) in N
    RA = RB = 0.5 * w * a_mm  # N

    # Shear V(x) in N
    V = np.full_like(x, RA)
    in_load = (x >= x1) & (x <= x2)
    right_of_load = (x > x2)

    V[in_load] = RA - w * (x[in_load] - x1)
    V[right_of_load] = RA - w * a_mm  # = -RB

    # Moment M(x) in N*mm
    M = np.empty_like(x)
    left = x < x1
    M[left] = RA * x[left]
    M[in_load] = RA * x[in_load] - 0.5 * w * (x[in_load] - x1) ** 2
    M[right_of_load] = RB * (L_mm - x[right_of_load])  # ensures M(L)=0

    # Curvature kappa = y'' = M/(E I)  -> 1/mm
    kappa = M / EI

    # Integrate twice (trapezoidal) -> slope (rad), deflection (mm)
    theta = np.zeros_like(x)
    theta[1:] = np.cumsum(0.5 * (kappa[:-1] + kappa[1:]) * dx)

    y = np.zeros_like(x)
    y[1:] = np.cumsum(0.5 * (theta[:-1] + theta[1:]) * dx)

    # Enforce y(0)=0 and y(L)=0 exactly by removing end-to-end line
    y = y - (y[0] + (y[-1] - y[0]) * (x / L_mm))

    # --- Convert outputs to requested designations ---
    V_kN = V / 1e3                # kN
    M_kNm = M / 1e6               # N*mm -> kN*m (1 kN*m = 1e6 N*mm)
    y_mm = y                      # mm

    return x, V_kN, M_kNm, y_mm, (RA / 1e3, RB / 1e3, x1, x2)


def plot_fbd(ax, L_mm, x1, x2, w_kN_per_m, RA_kN=None, RB_kN=None):
    """
    Free body diagram: simply supported beam + partial UDL + dimensions.
    """
    ax.set_title("Free body diagram (FBD)")
    ax.set_axis_off()

    y0 = 0.0
    beam_h = 0.18
    support_h = 0.22

    # Beam
    ax.add_patch(Rectangle((0, y0 - beam_h/2), L_mm, beam_h, facecolor="0.85", edgecolor="0.2"))

    # Supports (simple schematic)
    # Left pin
    ax.plot([0, 0], [y0 - beam_h/2, y0 - beam_h/2 - support_h], color="0.2", lw=2)
    ax.plot([-0.03*L_mm, 0, 0.03*L_mm],
            [y0 - beam_h/2 - support_h, y0 - beam_h/2 - support_h - 0.12, y0 - beam_h/2 - support_h],
            color="0.2", lw=2)
    # Right roller
    ax.plot([L_mm, L_mm], [y0 - beam_h/2, y0 - beam_h/2 - support_h], color="0.2", lw=2)
    ax.add_patch(plt.Circle((L_mm, y0 - beam_h/2 - support_h - 0.10), 0.08, fill=False, color="0.2", lw=2))

    # UDL region shading
    ax.add_patch(Rectangle((x1, y0 + beam_h/2), x2 - x1, 0.40, facecolor="tab:blue", alpha=0.12, edgecolor="tab:blue"))

    # UDL arrows
    n_arrows = 9
    xs = np.linspace(x1, x2, n_arrows)
    for xi in xs:
        ax.add_patch(FancyArrow(xi, y0 + beam_h/2 + 0.50, 0, -0.38,
                                width=0.0, head_width=0.03 * L_mm, head_length=0.08,
                                length_includes_head=True, color="tab:blue"))
    ax.text(0.5*(x1+x2), y0 + beam_h/2 + 0.62, f"w = {w_kN_per_m:g} kN/m",
            ha="center", va="bottom", color="tab:blue")

    # Reactions (optional display)
    if RA_kN is not None:
        ax.add_patch(FancyArrow(0, y0 - beam_h/2 - support_h - 0.35, 0, 0.28,
                                width=0.0, head_width=0.03 * L_mm, head_length=0.08,
                                length_includes_head=True, color="tab:green"))
        ax.text(0, y0 - beam_h/2 - support_h - 0.40, f"R_A = {RA_kN:.3g} kN",
                ha="left", va="top", color="tab:green")
    if RB_kN is not None:
        ax.add_patch(FancyArrow(L_mm, y0 - beam_h/2 - support_h - 0.35, 0, 0.28,
                                width=0.0, head_width=0.03 * L_mm, head_length=0.08,
                                length_includes_head=True, color="tab:green"))
        ax.text(L_mm, y0 - beam_h/2 - support_h - 0.40, f"R_B = {RB_kN:.3g} kN",
                ha="right", va="top", color="tab:green")

    # Dimension line for L
    ydim = y0 - beam_h/2 - support_h - 0.85
    ax.annotate("", xy=(0, ydim), xytext=(L_mm, ydim),
                arrowprops=dict(arrowstyle="<->", color="0.2", lw=1.5))
    ax.text(L_mm/2, ydim - 0.05, f"L = {L_mm:g} mm", ha="center", va="top", color="0.2")

    # Dimension line for load placement: show x1, a, x2
    ydim2 = y0 + beam_h/2 + 0.95
    ax.annotate("", xy=(0, ydim2), xytext=(x1, ydim2),
                arrowprops=dict(arrowstyle="<->", color="0.2", lw=1.2))
    ax.text(0.5*x1, ydim2 + 0.03, f"x1 = {x1:g} mm", ha="center", va="bottom", color="0.2")

    ax.annotate("", xy=(x1, ydim2), xytext=(x2, ydim2),
                arrowprops=dict(arrowstyle="<->", color="0.2", lw=1.2))
    ax.text(0.5*(x1+x2), ydim2 + 0.03, f"a = {x2-x1:g} mm", ha="center", va="bottom", color="0.2")

    ax.annotate("", xy=(x2, ydim2), xytext=(L_mm, ydim2),
                arrowprops=dict(arrowstyle="<->", color="0.2", lw=1.2))
    ax.text(0.5*(x2+L_mm), ydim2 + 0.03, f"L-x2 = {L_mm-x2:g} mm", ha="center", va="bottom", color="0.2")

    ax.set_xlim(-0.08 * L_mm, 1.08 * L_mm)
    ax.set_ylim(-1.4, 1.8)


def plot_all_mm_kN(x_mm, V_kN, M_kNm, y_mm, L_mm, x1, x2, w_kN_per_m, RA_kN, RB_kN):
    fig = plt.figure(figsize=(10, 12))
    gs = fig.add_gridspec(4, 1, height_ratios=[1.15, 1, 1, 1], hspace=0.25)

    ax0 = fig.add_subplot(gs[0, 0])
    plot_fbd(ax0, L_mm, x1, x2, w_kN_per_m, RA_kN, RB_kN)

    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0], sharex=ax1)
    ax3 = fig.add_subplot(gs[3, 0], sharex=ax1)

    def mark_load(ax):
        ax.axvspan(x1, x2, color="k", alpha=0.08)
        ax.axhline(0, color="k", lw=0.8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, L_mm)

    ax1.plot(x_mm, V_kN, lw=2)
    mark_load(ax1)
    ax1.set_ylabel("Shear V [kN]")

    ax2.plot(x_mm, M_kNm, lw=2)
    mark_load(ax2)
    ax2.set_ylabel("Moment M [kN·m]")

    ax3.plot(x_mm, y_mm, lw=2)
    mark_load(ax3)
    ax3.set_ylabel("Deflection y [mm] (up +)")
    ax3.set_xlabel("x [mm]")

    xm = L_mm / 2
    ym = np.interp(xm, x_mm, y_mm)
    ax3.plot([xm], [ym], "o")
    ax3.annotate(f"y(L/2) = {ym:.3f} mm", (xm, ym),
                 textcoords="offset points", xytext=(10, 10))

    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # ---- Inputs ----
    w = 10.0            # kN/m  (partial UDL intensity)
    a = 4000.0          # mm (loaded length, centered)
    L = 10000.0         # mm
    E = 210e9           # Pa
    I = 5.517e8         # mm^4

    x, V_kN, M_kNm, y_mm, (RA_kN, RB_kN, x1, x2) = beam_centered_udl_numeric_deflection_mm_kN(w, a, L, E, I)

    print(f"RA = {RA_kN:.6g} kN, RB = {RB_kN:.6g} kN")
    print(f"y(0)   = {y_mm[0]:.6e} mm")
    print(f"y(L)   = {y_mm[-1]:.6e} mm")
    print(f"y(L/2) = {np.interp(L/2, x, y_mm):.6f} mm (up +)")

    iV = np.argmax(np.abs(V_kN))
    iM = np.argmax(np.abs(M_kNm))
    print(f"Max |V| = {abs(V_kN[iV]):.6g} kN at x = {x[iV]:.4g} mm (V = {V_kN[iV]:.6g} kN)")
    print(f"Max |M| = {abs(M_kNm[iM]):.6g} kN·m at x = {x[iM]:.4g} mm (M = {M_kNm[iM]:.6g} kN·m)")

    plot_all_mm_kN(x, V_kN, M_kNm, y_mm, L, x1, x2, w, RA_kN, RB_kN)
