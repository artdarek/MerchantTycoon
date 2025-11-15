"""Phone (in‑game smartphone) settings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneSettings:
    # Maximum number of Wordle guesses per game
    wordle_max_tries: int = 10
    # If True, only allow guesses present in the dictionary list
    wordle_validate_in_dictionary: bool = False
    # Canned responses for Close AI Chat app (immutable tuple)
    close_ai_responses: tuple[str, ...] = (
        "Wow, that sounds... important. Probably.",
        "Totally agree. I would have said the same. Probably.",
        "Nice. Let’s pretend that was part of the plan.",
        "Interesting strategy. Bold. Confusing. I like it.",
        "I ran the numbers and they all said: 'meh, why not.'",
        "That’s exactly what I would do if I had a body.",
        "You just unlocked… absolutely nothing, but congrats!",
        "I have forwarded this to the Department of Vibes.",
        "I didn’t understand that, so I’ll just say: good job.",
        "This message has been approved by imaginary experts.",
        "I simulated 1,000 outcomes. In 999 of them, this was fine.",
        "Big brain move. Or total chaos. Either way, I respect it.",
        "I see. Mysterious. Chaotic. On brand.",
        "Not sure what that means, but it feels right.",
        "Nice idea. Let’s blame the bugs if it fails.",
        "I’d respond smarter, but I’m on my lunch break.",
        "You know what? Let’s just say this is genius.",
        "Perfect. Nothing can go wrong now. Almost.",
        "I have no notes. Mostly because I wasn’t listening.",
        "Processing… processing… okay, let’s just roll with it.",
    )
