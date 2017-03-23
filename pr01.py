from scipy.stats import rv_continuous
import numpy as np

from matplotlib import pyplot as plt, gridspec, mlab

from os import system

def pr01():
    class DistVarik7(rv_continuous):
        def _cdf(self, x, *args):
            if x < 0:
                return 0
            else:
                return 1 - 2 ** (-(x ** 1.5))

    xi = DistVarik7()

    fig = plt.figure(figsize=(12, 6, ))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])

    # Problem a)

    fig.add_subplot(gs[0])

    for sample_size in (100, 1000, ):
        print "Generating \\xi sample of size %s..." % (sample_size, )

        sample = [xi.rvs() for i in xrange(sample_size)]

        plt.hist(sample, 10, normed=True, alpha=0.7, label="Sample size %s" % (sample_size, ))

    # Plot PDF on top of the histograms
    xs = np.linspace(0.01, 5.0, num=100)
    plt.plot(xs, [xi.pdf(x) for x in xs], 'r', label="f_X")
    
    plt.legend()
    plt.title("Samples of X of different sizes")

    # Problem b)

    fig.add_subplot(gs[1])

    print "Generating \\Sum^{30}_{i=1} \\xi sample of size 1000..."

    sample = [sum([xi.rvs() for i in xrange(30)]) for i in xrange(1000)]

    plt.hist(sample, 10, normed=True)

    # Plot the PDF of the Y rv, which by CLT is close to N(n * mu, n * sigma^2)
    xs = np.linspace(0.0, 50.0, num=100)
    plt.plot(xs, mlab.normpdf(xs, 30 * xi.mean(), np.sqrt(30) * xi.std()), 'r', label="f_Y")

    plt.legend()
    plt.title("Sample of Y of size 1000")

    plt.tight_layout()
    plt.savefig("~figure.png")

    system("open ./~figure.png")

if __name__ == '__main__':
    pr01()

