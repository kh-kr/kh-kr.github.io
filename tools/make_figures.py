"""Generate the schematic research figures used on the website.

Each figure is written twice, once per colour scheme, so the page can swap them
with <picture media="(prefers-color-scheme: dark)">. Every figure reseeds its
own generator, so the two colour schemes plot identical points. The plots are
schematics of the methods, not reproductions of published data.

    python3 tools/make_figures.py
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "images", "figures")

THEMES = {
    "light": dict(
        surface="#ffffff", ink="#232a3b", secondary="#5a6478", muted="#79839a",
        grid="#e4e8f0", axis="#ccd3e0",
        blue="#2a78d6", orange="#eb6834", yellow="#eda100", aqua="#1baf7a",
        neutral="#b4bccc",
    ),
    "dark": dict(
        surface="#162031", ink="#e6ebf5", secondary="#9aa7bd", muted="#8291a8",
        grid="#243149", axis="#35435f",
        blue="#3987e5", orange="#d95926", yellow="#c98500", aqua="#199e70",
        neutral="#55637d",
    ),
}

rng = np.random.default_rng(0)


def reseed(seed):
    """Both colour schemes of a figure must plot the same points."""
    global rng
    rng = np.random.default_rng(seed)


def new_fig(t, figsize=(6.4, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    ax.grid(True, color=t["grid"], linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(t["axis"])
        ax.spines[side].set_linewidth(1.0)
    ax.tick_params(colors=t["muted"], labelsize=9, length=3, width=0.9)
    return fig, ax


def finish(fig, ax, t, name, title, xlabel, ylabel,
           legend_loc="best", legend_frame=False):
    ax.set_xlabel(xlabel, color=t["secondary"], fontsize=10, labelpad=7)
    ax.set_ylabel(ylabel, color=t["secondary"], fontsize=10, labelpad=7)
    ax.set_title(title, color=t["ink"], fontsize=11.5, fontweight="600",
                 loc="left", pad=12)
    leg = ax.legend(loc=legend_loc, fontsize=9, labelspacing=0.5,
                    handletextpad=0.6, borderpad=0.5,
                    frameon=legend_frame,
                    facecolor=t["surface"] if legend_frame else "none",
                    edgecolor="none", framealpha=0.92 if legend_frame else 0)
    for txt in leg.get_texts():
        txt.set_color(t["secondary"])
    leg.set_zorder(8)
    fig.tight_layout(pad=0.9)
    path = os.path.join(OUT_DIR, f"{name}.svg")
    fig.savefig(path, format="svg", facecolor=t["surface"])
    plt.close(fig)
    return path


def note(ax, t, text, xy, xytext, color=None, ha="left"):
    """A short label tied to a point, kept legible over dense scatter."""
    ax.annotate(
        text, xy=xy, xytext=xytext, fontsize=9.5, color=color or t["ink"],
        ha=ha, va="center", fontweight="600", zorder=7,
        bbox=dict(boxstyle="round,pad=0.32", facecolor=t["surface"],
                  edgecolor="none", alpha=0.9),
        arrowprops=dict(arrowstyle="-", color=color or t["muted"],
                        linewidth=1.0, shrinkA=4, shrinkB=4),
    )


def caption(ax, t, text, xy, ha="left", va="bottom", size=9):
    ax.text(*xy, text, fontsize=size, color=t["secondary"], ha=ha, va=va,
            zorder=7, transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=t["surface"],
                      edgecolor="none", alpha=0.9))


# --------------------------------------------------------------------------
# 1. Colour-magnitude diagram: where the stragglers live
# --------------------------------------------------------------------------
def ms_ridge(u):
    """Main-sequence ridge line, parametrised from faint/red (0) to the turnoff (1)."""
    return 1.75 - 1.18 * u, 15.9 - 3.75 * u - 0.55 * u ** 3


def fig_cmd(theme):
    reseed(101)
    t = THEMES[theme]
    fig, ax = new_fig(t)

    u = rng.random(430) ** 0.75
    ms_col, ms_mag = ms_ridge(u)
    ms_col = ms_col + rng.normal(0, 0.035, u.size)
    ms_mag = ms_mag + rng.normal(0, 0.10, u.size)

    v = rng.random(70)
    sgb_col, sgb_mag = 0.72 + 0.42 * v, 12.05 - 0.42 * v + rng.normal(0, 0.07, v.size)
    w = rng.random(70) ** 0.8
    rgb_col, rgb_mag = 1.10 + 0.52 * w, 11.60 - 2.75 * w + rng.normal(0, 0.10, w.size)
    clump_col, clump_mag = rng.normal(1.19, 0.045, 22), rng.normal(10.62, 0.09, 22)

    ax.scatter(np.concatenate([ms_col, sgb_col, rgb_col, clump_col]),
               np.concatenate([ms_mag, sgb_mag, rgb_mag, clump_mag]),
               s=11, c=t["neutral"], linewidths=0, zorder=2, label="Cluster members")

    # Blue stragglers: bluer and brighter than the turnoff.
    bss_col = rng.uniform(0.10, 0.50, 17)
    bss_mag = 11.95 - (0.50 - bss_col) * 2.9 + rng.normal(0, 0.28, 17)
    ax.scatter(bss_col, bss_mag, s=54, c=t["blue"], marker="o",
               edgecolors=t["surface"], linewidths=1.1, zorder=5,
               label="Blue stragglers")

    # Yellow stragglers: between the blue stragglers and the giant branch.
    ax.scatter(rng.uniform(0.66, 0.98, 5), rng.uniform(10.45, 11.35, 5),
               s=54, c=t["yellow"], marker="s", edgecolors=t["surface"],
               linewidths=1.1, zorder=5, label="Yellow stragglers")

    # Blue lurkers: photometrically ordinary, sitting on the main sequence.
    bl_u = rng.uniform(0.72, 0.87, 7)
    bl_col, bl_mag = ms_ridge(bl_u)
    ax.scatter(bl_col + rng.normal(0, 0.02, 7), bl_mag + rng.normal(0, 0.05, 7),
               s=54, c=t["aqua"], marker="D", edgecolors=t["surface"],
               linewidths=1.1, zorder=5, label="Blue lurkers")

    ax.axhline(12.15, color=t["axis"], linestyle=(0, (5, 4)), linewidth=1.1, zorder=1)
    ax.text(1.76, 12.08, "main-sequence turnoff", fontsize=9, color=t["muted"],
            ha="right", va="bottom", zorder=6)

    note(ax, t, "brighter and bluer\nthan the turnoff", (0.30, 11.3), (0.62, 9.7),
         color=t["blue"])
    note(ax, t, "ordinary in colour —\nfound by their fast spin", (0.83, 13.05),
         (0.64, 15.15), color=t["aqua"])

    ax.set_xlim(-0.05, 1.80)
    ax.set_ylim(16.3, 9.0)  # magnitudes: brighter is up
    return finish(fig, ax, t, f"cmd-{theme}",
                  "Stragglers in a cluster colour–magnitude diagram",
                  "Colour  (BP – RP)", "Magnitude  (G)",
                  legend_loc="lower left", legend_frame=True)


# --------------------------------------------------------------------------
# 2. The A+ parameter: blue stragglers as a dynamical clock
# --------------------------------------------------------------------------
def fig_aplus(theme):
    reseed(202)
    t = THEMES[theme]
    fig, ax = new_fig(t)

    r = np.linspace(0, 1, 300)
    bss, ref = r ** 0.62, r ** 1.32

    ax.fill_between(r, ref, bss, color=t["blue"], alpha=0.16, linewidth=0, zorder=2)
    ax.plot(r, bss, color=t["blue"], linewidth=2.0, zorder=4, label="Blue stragglers")
    ax.plot(r, ref, color=t["orange"], linewidth=2.0, zorder=4,
            label="Reference population (giants)")
    ax.plot([0, 1], [0, 1], color=t["axis"], linewidth=1.1,
            linestyle=(0, (5, 4)), zorder=1)

    ax.text(0.47, 0.60, r"$A^{+}$", fontsize=18, color=t["blue"], fontweight="700",
            ha="center", va="center", zorder=6)
    ax.text(0.50, 0.51, "area between the curves\ngrows as the cluster ages",
            fontsize=9.5, color=t["secondary"], ha="center", va="top", zorder=6)

    note(ax, t, "stragglers have already\nsunk toward the centre", (0.17, 0.325),
         (0.30, 0.88), color=t["blue"])

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    return finish(fig, ax, t, f"aplus-{theme}",
                  "The A⁺ parameter: mass segregation as a clock",
                  "Normalised distance from cluster centre",
                  "Cumulative fraction of stars", legend_loc="lower right")


# --------------------------------------------------------------------------
# 3. Extended main-sequence turnoff driven by rotation
# --------------------------------------------------------------------------
def turnoff_ridge(s):
    """Upper main sequence (s=0) through the turnoff and into the hook (s=1)."""
    s = np.asarray(s, dtype=float)
    on_ms = s <= 0.82
    a, b = s / 0.82, (s - 0.82) / 0.18
    col = np.where(on_ms, 0.62 - 0.44 * a, 0.18 + 0.27 * b)
    mag = np.where(on_ms, 13.85 - 1.50 * a, 12.35 - 0.30 * b)
    return col, mag


def fig_emsto(theme):
    reseed(303)
    t = THEMES[theme]
    fig, ax = new_fig(t)

    s_line = np.linspace(0, 1, 400)
    c_line, m_line = turnoff_ridge(s_line)
    ax.plot(c_line, m_line, color=t["axis"], linewidth=1.7, linestyle=(0, (5, 4)),
            zorder=3, label="Non-rotating isochrone")

    def population(n, dcol, dmag, spread):
        s = rng.random(n) ** 0.72
        col, mag = turnoff_ridge(s)
        # Rotation barely matters low on the main sequence, most at the turnoff.
        weight = np.clip((s - 0.30) / 0.70, 0, 1)
        col = col + weight * dcol + rng.normal(0, spread, n)
        mag = mag + weight * dmag + rng.normal(0, 0.045, n)
        return col, mag

    slow_c, slow_m = population(130, -0.030, -0.05, 0.018)
    fast_c, fast_m = population(130, 0.115, 0.17, 0.022)

    ax.scatter(slow_c, slow_m, s=24, c=t["blue"], linewidths=0, alpha=0.95,
               zorder=4, label="Slow rotators")
    ax.scatter(fast_c, fast_m, s=24, c=t["orange"], marker="^", linewidths=0,
               alpha=0.95, zorder=4, label="Fast rotators")

    ax.annotate("", xy=(0.175, 12.19), xytext=(0.395, 12.19),
                arrowprops=dict(arrowstyle="<->", color=t["ink"], linewidth=1.5),
                zorder=7)
    ax.text(0.285, 12.10, "extended turnoff", fontsize=9.5, color=t["ink"],
            ha="center", va="bottom", fontweight="600", zorder=7,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=t["surface"],
                      edgecolor="none", alpha=0.9))
    caption(ax, t, "one age — two spin rates", (0.97, 0.06), ha="right")

    ax.set_xlim(-0.02, 0.80)
    ax.set_ylim(14.15, 11.85)
    return finish(fig, ax, t, f"emsto-{theme}",
                  "Rotation broadens the main-sequence turnoff",
                  "Colour  (BP – RP)", "Magnitude  (G)",
                  legend_loc="lower left", legend_frame=True)


# --------------------------------------------------------------------------
# 4. Eclipsing blue straggler: a phase-folded light curve
# --------------------------------------------------------------------------
def fig_eclipse(theme):
    reseed(404)
    t = THEMES[theme]
    fig, ax = new_fig(t)

    def model(phase):
        """Trapezoidal eclipses plus a small ellipsoidal modulation."""
        f = np.ones_like(phase) - 0.012 * np.cos(4 * np.pi * phase)
        for centre, depth, half, edge in ((0.0, 0.235, 0.030, 0.020),
                                          (0.5, 0.088, 0.028, 0.019),
                                          (1.0, 0.235, 0.030, 0.020)):
            d = np.abs(phase - centre)
            f[d <= half - edge] -= depth
            ing = (d > half - edge) & (d < half)
            f[ing] -= depth * (half - d[ing]) / edge
        return f

    grid = np.linspace(0, 1, 1200)
    obs = np.sort(rng.random(320))
    ax.scatter(obs, model(obs) + rng.normal(0, 0.0055, obs.size), s=13,
               c=t["blue"], linewidths=0, alpha=0.85, zorder=3,
               label="Time-series photometry")
    ax.plot(grid, model(grid), color=t["orange"], linewidth=2.0, zorder=4,
            label="Light-curve model")

    note(ax, t, "primary eclipse", (0.030, 0.775), (0.155, 0.815))
    note(ax, t, "secondary eclipse", (0.500, 0.905), (0.645, 0.858))

    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(0.72, 1.05)
    return finish(fig, ax, t, f"eclipse-{theme}",
                  "Eclipsing systems weigh the stragglers directly",
                  "Orbital phase", "Normalised flux",
                  legend_loc="center left", legend_frame=True)


# --------------------------------------------------------------------------
# 5. Machine-learning membership in the proper-motion plane
# --------------------------------------------------------------------------
def fig_membership(theme):
    reseed(505)
    t = THEMES[theme]
    fig, ax = new_fig(t)

    fx, fy = rng.normal(-1.2, 3.3, 900), rng.normal(-0.6, 3.1, 900)
    keep = (fx + 3.05) ** 2 / 0.85 ** 2 + (fy - 2.35) ** 2 / 0.85 ** 2 > 1
    ax.scatter(fx[keep], fy[keep], s=7, c=t["neutral"], linewidths=0, alpha=0.75,
               zorder=2, label="Field stars")
    ax.scatter(rng.normal(-3.05, 0.26, 170), rng.normal(2.35, 0.24, 170),
               s=17, c=t["blue"], linewidths=0, zorder=4,
               label="Members found by ML-MOC")
    ax.add_patch(Ellipse((-3.05, 2.35), 2.5, 2.35, fill=False, edgecolor=t["blue"],
                         linewidth=1.5, linestyle=(0, (4, 3)), zorder=5))

    note(ax, t, "the cluster moves as one", (-2.0, 3.0), (1.6, 5.9), color=t["blue"])
    caption(ax, t, "kNN + Gaussian mixture,\nno hand-tuned cuts", (0.97, 0.04),
            ha="right")

    ax.set_xlim(-10.5, 8)
    ax.set_ylim(-9.5, 8.5)
    return finish(fig, ax, t, f"membership-{theme}",
                  "Separating members from the Milky Way field",
                  "Proper motion in RA  (mas yr⁻¹)",
                  "Proper motion in Dec  (mas yr⁻¹)",
                  legend_loc="upper left", legend_frame=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Liberation Sans"],
        "svg.fonttype": "path",
        "figure.dpi": 100,
    })
    for build in (fig_cmd, fig_aplus, fig_emsto, fig_eclipse, fig_membership):
        for theme in THEMES:
            print("wrote", build(theme))


if __name__ == "__main__":
    main()
