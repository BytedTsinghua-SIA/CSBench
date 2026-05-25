# Calculate the accuracy of a baseline that simply predicts "London" for every
#   example in the dev set.
# Hint: Make use of existing code.
# Your solution here should only be a few lines.

from tqdm import tqdm  # noqa: F401 (the import is provided for convenience)
import utils


def main():
    """Compute the accuracy of always predicting 'London' on the dev set."""
    raise NotImplementedError(
        "Use utils.evaluate_places to score the constant 'London' predictions."
    )


if __name__ == "__main__":
    main()
