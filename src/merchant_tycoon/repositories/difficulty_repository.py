"""Repository for accessing and querying game difficulty levels.

This repository provides a clean, read-only interface to the GAME_DIFFICULTY_LEVELS
domain constant, encapsulating all lookup logic for difficulty settings.
"""
from typing import List, Optional

from merchant_tycoon.domain.model.game_difficulty_level import GameDifficultyLevel
from merchant_tycoon.domain.game_difficulty_levels import GAME_DIFFICULTY_LEVELS


class DifficultyRepository:
    """Repository for querying game difficulty levels.

    Provides methods for retrieving difficulty levels without directly exposing
    the underlying GAME_DIFFICULTY_LEVELS constant to services and UI components.

    Examples:
        >>> repo = DifficultyRepository()
        >>> all_levels = repo.get_all()
        >>> normal = repo.get_by_name("normal")
        >>> default = repo.get_default()
    """

    def __init__(self, levels: Optional[List[GameDifficultyLevel]] = None):
        """Initialize repository with difficulty levels.

        Args:
            levels: Optional custom difficulty levels. Defaults to GAME_DIFFICULTY_LEVELS constant.
        """
        self._levels = levels if levels is not None else GAME_DIFFICULTY_LEVELS

    def get_all(self) -> List[GameDifficultyLevel]:
        """Get all available difficulty levels.

        Returns:
            Complete list of all difficulty levels in the game.
        """
        return list(self._levels)

    def get_by_name(self, name: str) -> Optional[GameDifficultyLevel]:
        """Find a difficulty level by its internal name.

        Args:
            name: Internal name of the difficulty (e.g., "normal", "hard").

        Returns:
            The GameDifficultyLevel if found, None otherwise.

        Examples:
            >>> repo.get_by_name("normal")
            GameDifficultyLevel(name="normal", display_name="Normal", ...)
            >>> repo.get_by_name("invalid")
            None
        """
        for level in self._levels:
            if level.name == name:
                return level
        return None

    def get_by_display_name(self, display_name: str) -> Optional[GameDifficultyLevel]:
        """Find a difficulty level by its display name.

        Args:
            display_name: Display name shown to users (e.g., "Normal", "Hard").

        Returns:
            The GameDifficultyLevel if found, None otherwise.

        Examples:
            >>> repo.get_by_display_name("Normal")
            GameDifficultyLevel(name="normal", display_name="Normal", ...)
        """
        for level in self._levels:
            if level.display_name == display_name:
                return level
        return None

    def get_default(self) -> GameDifficultyLevel:
        """Get the default difficulty level.

        Returns:
            The "normal" difficulty level. Falls back to first level if "normal" not found.

        Examples:
            >>> repo.get_default()
            GameDifficultyLevel(name="normal", ...)
        """
        # Try to find "normal" difficulty
        for level in self._levels:
            if level.name == "normal":
                return level

        # Fallback to first level if "normal" not found
        if self._levels:
            return self._levels[0]

        # Should never happen with valid GAME_DIFFICULTY_LEVELS
        raise ValueError("No difficulty levels available")

    def exists(self, name: str) -> bool:
        """Check if a difficulty level exists by name.

        Args:
            name: Internal name to check.

        Returns:
            True if a level with that name exists, False otherwise.

        Examples:
            >>> repo.exists("normal")
            True
            >>> repo.exists("invalid")
            False
        """
        return self.get_by_name(name) is not None

    def count(self) -> int:
        """Get total number of difficulty levels.

        Returns:
            Total count of available difficulty levels.
        """
        return len(self._levels)

    def get_display_names(self) -> List[str]:
        """Get all difficulty display names for UI selection.

        Returns:
            List of display names in order.

        Examples:
            >>> repo.get_display_names()
            ['Playground', 'Easy', 'Normal', 'Hard', 'Insane']
        """
        return [level.display_name for level in self._levels]

    def get_choices(self) -> List[tuple[str, str]]:
        """Get all difficulties as (display_name, name) tuples for UI dropdowns.

        Returns:
            List of (display_name, internal_name) tuples.

        Examples:
            >>> repo.get_choices()
            [('Playground', 'playground'), ('Easy', 'easy'), ...]
        """
        return [(level.display_name, level.name) for level in self._levels]
