import numpy as np

from matplotlib import pyplot as plt, gridspec

from os import system, path

from jinja2 import Template

def pr04_part1((x2s, x3s, x4s, ys, ), var_number):
    y_vector = np.array(ys)

    x_matrix = np.array([
        np.ones(len(x2s)),
        x2s,
        x3s,
        x4s,
        ]).transpose()

    # Find least-squares solution for X * beta = y
    beta_vector, residues, rank, s = np.linalg.lstsq(x_matrix, y_vector)

    template_path = path.join(path.dirname(__file__), 'output_template.md')

    with open(template_path, mode='r') as f:
        template = Template(f.read().decode('utf-8'))

    for line in template.render(var_number=var_number, beta_hats=beta_vector.tolist()).split('\n'):
        print line.encode('utf-8')



    # plt.scatter(x3s, ys, s=5.0)

    # plt.legend()
    # plt.savefig("~figure.png")

    # system("open ./~figure.png")
