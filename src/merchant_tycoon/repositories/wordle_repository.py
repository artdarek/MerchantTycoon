import random
from typing import List

from merchant_tycoon.domain.wordle import WORDLE_WORDS


class WordleRepository:
    """Repository providing access to Wordle word list."""

    def get_all(self) -> List[str]:
        return list(WORDLE_WORDS)

    def get_random(self) -> str:
        try:
            return random.choice(WORDLE_WORDS)
        except Exception:
            return "apple"

