from dataclasses import dataclass


@dataclass(frozen=True)
class SaveUiSettings:
    # Directory name under user home for saves
    save_dir_name: str = ".merchant_tycoon"
    # Max number of messages retained in the in-game log
    messages_save_limit: int = 100
    # Max number of bank transactions shown/saved
    bank_transactions_limit: int = 100

