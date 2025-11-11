from dataclasses import dataclass


@dataclass(frozen=True)
class GameDifficultyLevel:
    """Defines a difficulty level preset for game initialization.

    Difficulty levels control the starting conditions for a new game, providing
    experiences ranging from sandbox experimentation to extreme survival challenges.
    Once set at game start, the difficulty determines initial cash and cargo capacity.

    Attributes:
        name: Internal identifier for this difficulty level (e.g., "normal", "insane").
            Used for save/load and configuration references. Should be lowercase,
            no spaces, unique across all difficulty levels.
        display_name: User-facing name shown in menus and UI (e.g., "Normal", "Insane").
            Properly capitalized, human-readable label for the difficulty.
        start_cash: Initial cash amount in dollars when starting a new game.
            Range: $0 (Insane) to $1,000,000 (Playground)
            Examples:
            - Playground: $1,000,000 (unlimited experimentation)
            - Easy: $100,000 (generous start)
            - Normal: $50,000 (balanced)
            - Hard: $10,000 (limited resources)
            - Insane: $0 (must take loans immediately)
        start_capacity: Initial cargo inventory capacity (max units of goods).
            Range: 1 slot (Insane) to 1000 slots (Playground)
            Examples:
            - Playground: 1000 (effectively unlimited)
            - Easy: 100 (comfortable trading)
            - Normal: 50 (strategic choices required)
            - Hard: 10 (very limited)
            - Insane: 1 (single item at a time)
        description: Brief explanation of the difficulty shown in selection UI.
            Should describe the challenge level and starting conditions in 1-2 sentences.

    Examples:
        >>> normal = GameDifficultyLevel(
        ...     name="normal",
        ...     display_name="Normal",
        ...     start_cash=50_000,
        ...     start_capacity=50,
        ...     description="Balanced challenge"
        ... )
        >>> insane = GameDifficultyLevel(
        ...     name="insane",
        ...     display_name="Insane",
        ...     start_cash=0,
        ...     start_capacity=1,
        ...     description="Start with nothing, maximum challenge"
        ... )

    Notes:
        - Frozen dataclass prevents modification after creation (immutable)
        - Difficulty only affects starting conditions, not ongoing gameplay mechanics
        - Players can still expand capacity and earn money regardless of starting difficulty
        - Default difficulty is "normal" if not specified
    """
    name: str
    display_name: str
    start_cash: int
    start_capacity: int
    description: str
