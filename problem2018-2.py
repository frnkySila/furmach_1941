
from matplotlib import pyplot as plt, gridspec
from scipy.stats import kstest
from os import system


class LCG:
    def __init__(self, init, a=113, b=10, m=10000):
        self._a, self._b, self._m = a, b, m

        if init >= m:
            raise ValueError("Initial state can't be greater than `m`")

        self._init = init
        self._current = init

    @property
    def description(self):
        return "$LCG(a=%d, b=%d, m=%d, z_0=%d)$" % (self._a, self._b, self._m, self._init, )

    @property
    def range(self):
        return (0, self._m)

    def reset(self):
        self._current = self._init

    def next(self):
        old = self._current

        self._current = (self._a * self._current + self._b) % self._m

        return old


def annotate_max_diff(xs, fs, gs, g_is_step=True, s_format="$%.4f$"):
    x, f, g = xs[0], fs[0], gs[0]

    for i, (xx, fx, gx) in enumerate(zip(xs, fs, gs)[1:]):
        if abs(fx - gx) > abs(f - g):
            x, f, g = xx, fx, gx

        if g_is_step and abs(fx - gs[i]) > abs(f - g):
            x, f, g = xx, fx, gs[i]

    y_text = (f + g) / 2.0

    text_on_the_right = x < 0.5

    if text_on_the_right:
        x_text = x + 0.1
    else:
        x_text = x - 0.1

    for is_top_one in (True, False):
        plt.annotate(
            s=s_format % abs(f - g),
            xy=(x, is_top_one and f or g),
            xytext=(x_text, y_text),
            arrowprops=dict(arrowstyle='->', alpha=0.5, clip_on=False),
            ha=text_on_the_right and 'left' or 'right',
            va='center',
            alpha=is_top_one and 0.75 or 0.0)

    plt.plot([x, x], [f, g], 'b', alpha=0.25)

    plt.plot([x], [f], 'r.', ms=7.5)
    plt.plot([x], [g], 'b.', ms=7.5)


def draw_ecdf_vs_r01(xs):
    plot_xs = [0.0] + sorted(xs) + [1.0]
    
    plt.plot(plot_xs, plot_xs, 'r', label="$F_{R(0; 1)}$")

    edf_values = [0.0] + [float(i) / len(xs) for i in xrange(1, len(xs))] + [1.0, 1.0]

    plt.step(plot_xs, edf_values, 'b', where='post', label="EDF")

    annotate_max_diff(plot_xs, plot_xs, edf_values, s_format="$D_n = %.4f$")

    plt.legend(loc='best')


def draw_r01_kolm_smir(xs, alpha=0.05):
    ks_stat, p_value = kstest(xs, lambda x: x)

    reject = p_value < alpha

    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)

    plt.annotate(
        s="  $D_n = %.4f$, $p = %.2f$ (%s at $\\alpha=%d\\%%$)" % (ks_stat, p_value, reject and "doesn't fit" or "fits", int(alpha * 100), ),
        xy=(0, 0),
        xytext=(0, 0.5),
        textcoords='axes fraction',
        ha='left',
        va='center')


def centered(xs, (x_min, x_max)):
    x_max = float(x_max)

    return [(x - x_min) / x_max for x in xs]


def display_results(prg, sizes=(100, 10000, )):
    plt.rcParams['font.family'] = 'serif'

    plt.rcParams['xtick.labelsize'] = 'x-small'
    plt.rcParams['xtick.color'] = '#545454'
    plt.rcParams['ytick.labelsize'] = 'x-small'
    plt.rcParams['ytick.color'] = '#545454'

    fig = plt.figure(figsize=(6 * len(sizes), 8))

    fig.suptitle("Fitness of $R(0; 1)$ to first $n$ states of %s" % prg.description)

    gs = gridspec.GridSpec(3, len(sizes), height_ratios=[6, 6, 1])

    for i, n in enumerate(sizes):
        prg.reset()

        xs = [prg.next() for _ in xrange(n)]

        fig.add_subplot(gs[i])

        plt.hist(xs, bins=10, range=prg.range)
        plt.title("$n = %d$" % n)

        xs_centered = centered(xs, prg.range)

        fig.add_subplot(gs[i + len(sizes)])

        draw_ecdf_vs_r01(xs_centered)

        fig.add_subplot(gs[i + 2 * len(sizes)])

        draw_r01_kolm_smir(xs_centered)

    # plt.tight_layout(pad=2.5, rect=[0.0, 0.0, 1.0, 0.97])

    plt.savefig("~figure.png", dpi=300)
    system("open ./~figure.png")


if __name__ == '__main__':

    display_results(LCG(2456), sizes=(100, 10000))

    # display_results(LCG(110, a=10, b=570, m=290))

