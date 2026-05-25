"""Configuration management."""


class Config:
    """
    A recursive configuration class that converts a dictionary into an object
    with attributes accessible using dot notation.
    """

    def __init__(self, dictionary: dict):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = Config(value)
            setattr(self, key, value)


def set_seed(seed: int = 531) -> None:
    pass

