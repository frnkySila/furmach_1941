
from os import system
from itertools import product
from functools import partial

from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import kstest


def take_unique(it, max_unique, max_total=None):
    if max_total is None:
        max_total = max_unique * 100

    seen = set()

    for i, x in enumerate(it):
        if i >= max_total:
            break

        if x not in seen:
            seen.add(x)

            yield x

            if len(seen) == max_unique:
                return


class SampleAnalysis:
    def _annotate_max_diff(self, ax, xs, fs, gs, g_is_step=True, s_format="$%.4f$"):
        x, f, g = xs[0], fs[0], gs[0]

        for i, (xx, fx, gx) in enumerate(zip(xs, fs, gs)[1:]):
            if abs(fx - gx) > abs(f - g):
                x, f, g = xx, fx, gx

            if g_is_step and abs(fx - gs[i]) > abs(f - g):
                x, f, g = xx, fx, gs[i]

        y_text = (f + g) / 2.0

        if x < 0.5:
            x_text = x + 0.1
            ha_text = 'left'
        else:
            x_text = x - 0.1
            ha_text = 'right'

        def draw_annotation(_y, _alpha):
            ax.annotate(
                s=s_format % abs(f - g),
                xy=(x, _y),
                xytext=(x_text, y_text),
                arrowprops=dict(arrowstyle='->', alpha=0.5, clip_on=False),
                ha=ha_text,
                va='center',
                alpha=_alpha
            )

        draw_annotation(f, 0.75)
        draw_annotation(g, 0.0)

        ax.plot([x, x], [f, g], 'b', alpha=0.25)

        ax.plot([x], [f], 'r.', ms=7.5)
        ax.plot([x], [g], 'b.', ms=7.5)


    def _draw_edf_vs_r01(self, ax):
        xs = sorted(self.xs)

        edf_values = [float(i) / len(xs) for i in xrange(1, len(xs) + 1)]

        cdf_values = [max(0.0, min(1.0, x)) for x in xs]

        if xs[0] > 0.0:
            for a in (xs, edf_values, cdf_values):
                a.insert(0, 0.0)

        if xs[-1] < 1.0:
            for a in (xs, edf_values, cdf_values):
                a.append(1.0)

        ax.set_xlim(
            min(0.0, xs[0]),
            max(1.0, xs[-1])
        )

        ax.set_ylim(-0.01, 1.01)

        ax.plot(xs, cdf_values, 'r', label="$F_{R(0; 1)}$")

        ax.step(xs, edf_values, 'b', where='post', label="EDF")

        self._annotate_max_diff(ax, xs, cdf_values, edf_values, s_format="$D_n = %.4f$")

        ax.legend(loc='best')

    def _draw_r01_kolm_smir(self, ax):
        ks_stat, p_value = kstest(self.xs, lambda x: x)

        reject = p_value < self.alpha

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)



        ax.annotate(
            s="  $D_n = %.4f$, $p = %s$ (%s at $\\alpha=%d\\%%$)" % (
                ks_stat,
                ('{:.2f}' if p_value >= min(self.alpha, 0.1) else '{:.3f}').format(p_value),
                reject and "no fit" or "fits",
                int(self.alpha * 100),
            ),
            xy=(0, 0),
            xytext=(0, 0.5),
            textcoords='axes fraction',
            ha='left',
            va='center')

    def is_positive(self):
        return kstest(self.xs, lambda x: x)[1] < self.alpha

    @staticmethod
    def will_result_positive(xs, alpha=0.05):
        return kstest(xs, lambda x: x)[1] < alpha

    def __init__(self, xs, description="", alpha=0.05):
        self.xs = xs
        self.description = description
        self.alpha = alpha

    def draw_on(self, (ax, bx, cx)):
        ax.set_title(self.description)

        ax.hist(self.xs, bins=10, range=(0.0, 1.0))

        self._draw_edf_vs_r01(bx)

        self._draw_r01_kolm_smir(cx)


def display_sample_analyses(prng, sizes=(100, 10000), find_examples=True):
    plt.rcParams['font.family'] = 'serif'

    plt.rcParams['xtick.labelsize'] = 'x-small'
    plt.rcParams['xtick.color'] = '#545454'
    plt.rcParams['ytick.labelsize'] = 'x-small'
    plt.rcParams['ytick.color'] = '#545454'

    analyses = [
        SampleAnalysis(
            prng.get_sample(n, first=True),
            "First ${:d}$ states".format(n)
        ) for n in sizes
    ]

    if analyses[0].is_positive():
        unique = list(take_unique(prng.forever(first=True), 100))

        while SampleAnalysis.will_result_positive(unique) and len(unique) > 2:
            unique.pop()

        analyses.insert(0,
            SampleAnalysis(
                unique,
                "First ${:d}$ unique states".format(len(unique))
            )
        )

    if not analyses[-1].is_positive():
        n_repeat = 2
        xs = []

        for n_repeat, size in product(xrange(2, 10), (10000, 100)):
            xs = prng.get_sample(size, first=True)

            if SampleAnalysis.will_result_positive(xs * n_repeat):
                break

        analyses.append(
            SampleAnalysis(
                xs * n_repeat,
                "First ${:d}$ states ${:d}$ times over".format(len(xs), n_repeat)
            )
        )

    fig = plt.figure(figsize=(5 * len(analyses), 8))

    fig.suptitle("Fitness of $R(0; 1)$ to samples from %s" % prng.description)

    gs = GridSpec(3, len(analyses), height_ratios=[6, 6, 1])
    all_axes = [fig.add_subplot(gs[i]) for i in xrange(3 * len(analyses))]

    for i, analysis in enumerate(analyses):
        analysis.draw_on(all_axes[i::len(analyses)])

    plt.savefig("~figure.png", dpi=300)
    system("open ./~figure.png")

