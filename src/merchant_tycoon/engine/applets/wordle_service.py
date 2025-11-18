from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from merchant_tycoon.repositories.wordle_repository import WordleRepository


@dataclass
class GuessResult:
    # per-letter marks: "correct" | "present" | "absent"
    marks: List[str]
    # True when the guess exactly matches the secret
    is_correct: bool
    # Total attempts used after this guess
    attempts_used: int
    # Optional message for UI
    message: str = ""


class WordleService:
    """Pure Wordle game logic with minimal state.

    UI communicates only via this service. The service does not import Textual
    nor touch UI directly. Secret/dictionary are provided by repository.
    """

    def __init__(
        self,
        repo: Optional[WordleRepository] = None,
        *,
        max_tries: int = 10,
        validate_in_dictionary: bool = True,
    ) -> None:
        self.repo = repo or WordleRepository()
        self.max_tries = int(max_tries)
        self.validate_in_dictionary = bool(validate_in_dictionary)
        self._secret: str = ""
        self._attempts: List[str] = []

    # ----- State API -----
    def reset(self, *, secret: Optional[str] = None) -> None:
        self._attempts = []
        if secret:
            self._secret = secret.strip().lower()[:5]
        else:
            try:
                self._secret = (self.repo.get_random() or "apple").strip().lower()[:5]
            except Exception:
                self._secret = "apple"

    @property
    def attempts(self) -> Sequence[str]:
        return tuple(self._attempts)

    @property
    def secret(self) -> str:
        return self._secret

    # ----- Validation & rules -----
    def validate_guess(self, word: str) -> tuple[bool, str]:
        w = (word or "").strip().lower()
        if len(w) != 5 or not w.isalpha():
            return False, "Word must be exactly 5 letters (a-z)!"
        if self.validate_in_dictionary:
            try:
                words = set(self.repo.get_all())
            except Exception:
                words = set()
            if w not in words:
                return False, "Word not in dictionary!"
        return True, w

    def make_guess(self, word: str) -> GuessResult:
        # assumes prior validate_guess call in UI or caller
        w = (word or "").strip().lower()[:5]
        self._attempts.append(w)
        marks = self._score_guess(w, self._secret)
        is_correct = (w == self._secret)
        msg = ""
        if is_correct:
            msg = "Correct! You guessed the word!"
        elif len(self._attempts) >= self.max_tries:
            msg = f"No more tries. The word was: {self._secret.upper()}"
        return GuessResult(marks=marks, is_correct=is_correct, attempts_used=len(self._attempts), message=msg)

    @staticmethod
    def _score_guess(guess: str, secret: str) -> List[str]:
        # Two-pass scoring (greens first, then present up to counts)
        counts: dict[str, int] = {}
        for ch in secret:
            counts[ch] = counts.get(ch, 0) + 1
        marks = ["absent"] * 5
        for i in range(min(5, len(secret), len(guess))):
            if guess[i] == secret[i]:
                marks[i] = "correct"
                counts[guess[i]] -= 1
        for i in range(min(5, len(secret), len(guess))):
            if marks[i] == "correct":
                continue
            ch = guess[i]
            if counts.get(ch, 0) > 0:
                marks[i] = "present"
                counts[ch] -= 1
            else:
                marks[i] = "absent"
        return marks
