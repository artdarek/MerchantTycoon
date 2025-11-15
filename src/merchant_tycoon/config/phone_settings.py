"""Phone (in‑game smartphone) settings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneSettings:
    # Maximum number of Wordle guesses per game
    wordle_max_tries: int = 10
    # If True, only allow guesses present in the dictionary list
    wordle_validate_in_dictionary: bool = False
