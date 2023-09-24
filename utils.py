import itertools
def combinations_string(string):
    """Return a list of all possible combinations characters of a string."""

    # Create a list of all possible combinations of characters of a string
    combinations = []
    for i in range(1, len(string) + 1):
        combinations += list(itertools.combinations(string, i))

    # Convert the list of tuples to a list of strings
    combinations = [''.join(x) for x in combinations]

    return combinations

