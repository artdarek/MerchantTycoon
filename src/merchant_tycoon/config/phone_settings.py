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
    #   "phrase": str | list[str],  # exact message(s) to trigger on (case-insensitive, trimmed)
    #   "bank": int,                # amount to credit to bank
    #   "title": str,               # bank transaction title
    #   "cargo": int,               # additional cargo capacity to grant
    #   "cash": int,                # amount of cash to add to wallet
    #   "response": str,            # AI chat response shown when applied
    #   "grant_goods": int,          # grant N random goods (free)
    #   "grant_stocks": int,         # grant N random assets (free)
    #   "grant_goods_size": int,     # quantity per goods purchase
    #   "grant_stocks_size": int,    # quantity per asset grant
    #   "buy_goods": int,             # buy N random goods (paid)
    #   "buy_stocks": int,            # buy N random assets (paid)
    #   "buy_goods_size": int,        # quantity per goods buy
    #   "buy_stocks_size": int,       # quantity per asset buy
    close_ai_magic_triggers: tuple[dict, ...] = (
        {
            "phrase": [
                "I need money mommy",
                "Blik"
            ],
            "response": "Check your account…\nmommy loves you! 💖",
            "bank": 10000,
            "title": "Mommy loves you",
            "cargo": 0,
            "cash": 0,
            "grant_goods": 0,
            "grant_stocks": 0,
            "grant_goods_size": 0,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": [
                "I need more money mommy",
                "Transfer"
            ],
            "response": "Are you kidding me!? eh...\ncheck your account…\nmommy loves you!",
            "bank": 100000,
            "title": "Mommy loves you but do not ask for more!",
            "cargo": 0,
            "cash": 0,
            "grant_goods": 0,
            "grant_stocks": 0,
            "grant_goods_size": 0,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": [
                "Give me your wallet",
                "Give me all your money",
                "Your wallet please",
            ],
            "response": "You scum!\nI will get you one day!\nAnd you will pay me back!",
            "bank": 0,
            "title": "Taken from strangers wallet",
            "cargo": 0,
            "cash": 1000000,
            "grant_goods": 0,
            "grant_stocks": 0,
            "grant_goods_size": 0,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": [
                "I need a car",
                "Let me drive your car",
                "Buy a car",
            ],
            "response": "Here you are! Keys to my Ford Mustang 76!\nhave a nice ride!",
            "bank": 1000,
            "title": "Money for car repairs",
            "cargo": 50,
            "cash": 0,
            "grant_goods": 0,
            "grant_stocks": 0,
            "grant_goods_size": 0,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": [
                "I need a truck",
                "Let me drive your truck",
                "Buy a truck",
            ],
            "response": "Oh ok! You can drive mine!\n...and drive safe!",
            "bank": 10000,
            "title": "Money for a truck repairs",
            "cargo": 100,
            "cash": 0,
            "grant_goods": 0,
            "grant_stocks": 0,
            "grant_goods_size": 0,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": ["What is your name", "Who are you"],
            "response": "My name is... my name is... \n...Slim Shady!",
            "bank": 1,
            "title": "Tip from Slim Shady",
            "cargo": 1,
            "cash": 1,
            "grant_goods": 1,
            "grant_goods_size": 1,
            "grant_stocks": 1,
            "grant_stocks_size": 1,
        },
        {
            "phrase": [
                "Buy me some goods",
                "Buy goods",
            ],
            "response": "Buy me this... buy me that... and what else?",
            "bank": 0,
            "title": "For goods",
            "cargo": 0,
            "cash": 0,
            "grant_goods": 0,
            "grant_stocks": 0,
            "grant_goods_size": 0,
            "grant_stocks_size": 0,
            "buy_goods": 5,
            "buy_goods_size": 10,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": ["Buy me some stocks", "Buy stocks" "Buy buy buy"],
            "response": "Investing is a good thing! Take all my shares!",
            "bank": 0,
            "title": "For stocks",
            "cargo": 0,
            "cash": 0,
            "grant_goods": 0,
            "grant_stocks": 0,
            "grant_goods_size": 0,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 5,
            "buy_stocks_size": 10,
        },
        {
            "phrase": [
                "Grant me some goods",
                "Give me some goods",
                "Need free goods",
            ],
            "response": "As you wish! Distributing free goods…",
            "bank": 0,
            "title": "Free goods",
            "cargo": 0,
            "cash": 0,
            "grant_goods": 5,
            "grant_stocks": 0,
            "grant_goods_size": 10,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": [
                "Grant me some stocks",
                "Give me some stocks",
                "Need free stocks",
                "Make me an owner",
            ],
            "response": "Granting you shiny new assets!",
            "bank": 0,
            "title": "Free stocks",
            "cargo": 0,
            "cash": 0,
            "grant_goods": 0,
            "grant_goods_size": 0,
            "grant_stocks": 5,
            "grant_stocks_size": 10,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": [
                "I am not sure how to talk to you anymore",
                "I do not know how to talk to you anymore",
                "Help me",
            ],
            "response": "Well, maybe you should’ve said that in the first place: \n - What is your name\n - I need a truck\n - I need a car\n - Give me your wallet\n - I need more money mommy\n - I need money mommy\n - Buy me some goods\n - Buy me some stocks\n - Grant me some goods\n - Grant me some stocks",
            "bank": 0,
            "title": "To help you",
            "cargo": 0,
            "cash": 0,
            "grant_goods": 0,
            "grant_goods_size": 0,
            "grant_stocks": 0,
            "grant_stocks_size": 0,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
        {
            "phrase": "iddqd",
            "response": "IDDQD? Oh, we’re doing god mode now. Health: ∞. Ammo: ∞. Financial restraint\nNow go break the economy. I’ll be here pretending this is balanced.",
            "bank": 9999999999,
            "title": "I god mode you",
            "cargo": 9999999,
            "cash": 9999999999,
            "grant_goods": 100,
            "grant_goods_size": 9999,
            "grant_stocks": 100,
            "grant_stocks_size": 9999,
            "buy_goods": 0,
            "buy_goods_size": 0,
            "buy_stocks": 0,
            "buy_stocks_size": 0,
        },
    )
    # }
