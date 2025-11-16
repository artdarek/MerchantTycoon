# Changelog (Compact)

All notable changes to this project, condensed for quick scanning. Follows a Keep a Changelog–style structure and Semantic Versioning.

## [Unreleased]

- Added: ...
- Changed: ...
- Fixed: ...
- Removed: ...

---

## [1.5.0]

### Added
- CloseAI Chat (Phone) triggers for free grants and paid buys:
  - Free: `grant_goods`, `grant_goods_size`, `grant_stocks`, `grant_stocks_size`
  - Paid: `buy_goods`, `buy_goods_size`, `buy_stocks`, `buy_stocks_size`
- Phrases now accept a single string or alternatives list (case-insensitive); new grant-related phrases and expanded `iddqd` help output.
- Services helpers for non-cash flows:
  - GoodsService: `grant` (zero-cost add), `gift` (remove via FIFO without cash)
  - InvestmentsService: `grant_asset`, `gift_asset`

### Docs
- README updates: CloseAI trigger schema and free helper usage.

---

## [1.4.0]

### Added
- Phone tab (key 5) with apps:
  - Home (animated), WhatsUp (live messenger feed), Camera/Gallery (scrollable ASCII), Wordle game.
- Wordle improvements: bottom input, Guess/Play Again/Restart, stats, duplicate-letter logic, settings (`wordle_max_tries`, `wordle_validate_in_dictionary`), 500+ words.
- Lotto: Owned Tickets table shows Wins column.

### Changed
- WhatsUp auto-refresh and titled panel; camera/WhatsUp panels fill screen and center; consistent UI polish across phone apps.

---

## [1.3.0]

### Added
- Lotto tab (key 4): Buy Ticket, Owned Tickets, Today’s Draw, Win History.
- Modals: BuyTicket, TicketActions (activate/deactivate, remove), LottoWinner.
- Persistence: tickets, draw, win history; Owned Tickets include Cost, Reward, and P/L; summary panels and actions (including "Lucky shot!").
- New travel loss event: `LottoTicketLost` (removes one active ticket if any; logs and shows loss modal).

### Changed
- Consistent lotto UI: compact inputs, standardized modals, sorted tables, improved heights/scroll.

---

## [1.2.4]

### Added / Changed
- Replaced lottery event with Contest Win event (configurable contests, tiered prizes, weighted outcomes).
- New handler: `ContestWinEventHandler`; old `LotteryEventHandler` removed and related config deleted.

### Notes
- Configurable lists: contest names with base prize, place weights; same event frequency as old lottery.

---

## [1.2.3]

### Added
- Newspaper modal (key N): full message history with date grouping, color-coded levels, timestamps, auto-scroll; toggle via N/ESC.

### Changed
- Stolen goods event message clarified; bank modals simplified (removed redundant info across loan/deposit/withdraw/repay).

### Docs
- README: added Newspaper keybinding and description.

---

## [1.2.2]

### Added
- Dividend system for selected stocks: every 11 days, 10-day minimum holding; rates 0.1–0.3% of current price; paid to bank; tracked per lot.
- WalletService as single source of truth for cash ops (`get_balance`, `set_balance`, `can_afford`, `earn`, `spend`).
- Bank Account balance history chart panel (ASCII line graph) using last 50 transactions.

### Changed
- Separated dividends from random travel events; standardized travel return tuple; introduced `neutral` event type.
- Service initialization refactor: explicit required dependencies; improved `ClockService` (`advance_day()`), clearer travel fee calc.

### Compatibility
- Backward compatible with 1.1.x saves; new fields initialized automatically.

---

## [1.1.x]

### Added
- Game difficulty system (5 levels: Playground → Insane) affecting starting cash and cargo capacity; selection modal on new game.
- Expanded goods from ~15 to 31 across categories: electronics (incl. luxury), jewelry, cars (new), contraband (new); volatility differentiated by type.

### Changed
- Domain refactor: split constants into `domain/goods.py`, `cities.py`, `assets.py`, `game_difficulty_levels.py`.
- Model rename: `DifficultyLevel` → `GameDifficultyLevel`.

### Breaking
- Import path updates required for refactor and rename.

### Docs
- README: difficulty levels, goods/categories, domain architecture; updated features and inventory management sections.

---

## Maintenance Tips

- Add new entries under [Unreleased] using Added/Changed/Fixed/Removed subsections.
- On release, duplicate the [Unreleased] block under a new version header and clear [Unreleased].
- Keep entries concise and user-focused; link to files only when necessary.
