from sys import argv, exit

from solution import pr04
from variants import get_data_by_variant_number

if __name__ == '__main__':
    if len(argv) != 2:
        print "Usage: python problem_4 [x], x - varik number"
        exit()

    var_number = int(argv[1])

    data = get_data_by_variant_number(var_number)

    pr04(data, var_number)
