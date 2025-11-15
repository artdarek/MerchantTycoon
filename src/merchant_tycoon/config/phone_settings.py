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
    # Special Close AI triggers: list of magic sentences and their effects.
    # Each entry:
    # {
    #   "phrase": str,              # exact message to trigger on (case-insensitive, trimmed)
    #   "bank": int,                # amount to credit to bank
    #   "title": str,               # bank transaction title
    #   "cargo": int,               # additional cargo capacity to grant
    #   "cash": int,                # amount of cash to add to wallet
    #   "response": str,            # AI chat response shown when applied
    #   "buy_goods": int,           # buy N random goods (1 unit each)
    #   "buy_stocks": int,          # buy N random assets (1 unit each)
    # }
    close_ai_magic_triggers: tuple[dict, ...] = (
        {
            "phrase": "I need money mommy",
            "bank": 10000,
            "title": "Mommy loves you",
            "cargo": 0,
            "cash": 0,
            "response": "Check your account… mommy loves you! 💖",
            "buy_goods": 0,
            "buy_stocks": 0,
        },
        {
            "phrase": "I need more money mommy",
            "bank": 100000,
            "title": "Mommy loves you but do not ask for more!",
            "cargo": 0,
            "cash": 0,
            "response": "Are you kidding me!? eh... check your account… mommy loves you!",
            "buy_goods": 0,
            "buy_stocks": 0,
        },
        {
            "phrase": "Give me your wallet",
            "bank": 0,
            "title": "Taken from strangers wallet",
            "cargo": 0,
            "cash": 1000000,
            "response": "You scum! I will get you one day! And you will pay me back!",
            "buy_goods": 0,
            "buy_stocks": 0,
        },
        {
            "phrase": "I need a car",
            "bank": 1000,
            "title": "Money for car repairs",
            "cargo": 50,
            "cash": 0,
            "response": "Here you are! Keys to my Ford Mustang 76! have a nice ride!",
            "buy_goods": 0,
            "buy_stocks": 0,
        },
        {
            "phrase": "I need a truck",
            "bank": 10000,
            "title": "Money for a truck repairs",
            "cargo": 100,
            "cash": 0,
            "response": "Oh ok! You can drive mine! Drive safe!",
            "buy_goods": 0,
            "buy_stocks": 0,
        },
        {
            "phrase": "What is your name",
            "bank": 1,
            "title": "Tip from Slim Shady",
            "cargo": 1,
            "cash": 1,
            "response": "My name is... my name is... Slim Shady!",
            "buy_goods": 1,
            "buy_stocks": 1,
        },
        {
            "phrase": "Buy me some goods",
            "bank": 0,
            "title": "For goods",
            "cargo": 0,
            "cash": 0,
            "response": "Buy me this... buy me that... and what else?",
            "buy_goods": 5,
            "buy_stocks": 5,
        },
        {
            "phrase": "Buy me some stocks",
            "bank": 0,
            "title": "For stocks",
            "cargo": 0,
            "cash": 0,
            "response": "Investing is a good thing! Take all my shares!",
            "buy_goods": 10,
            "buy_stocks": 10,
        },
        {
            "phrase": "iddqd",
            "bank": 10000000,
            "title": "I god mode you",
            "cargo": 1000,
            "cash": 10000000,
            "response": "You should say this: \n - What is your name\n - I need a truck\n - I need a car\n - Give me your wallet\n - I need more money mommy\n - I need money mommy\n - Buy me some goods\n - Buy me some stocks",
        },
    )
