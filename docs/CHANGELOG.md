# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning.

## [1.5.0]

### Added
- CloseAI Chat enhancements (Phone tab):
  - Support for free grants and paid buys via triggers:
    - Free: `grant_goods`, `grant_goods_size`, `grant_stocks`, `grant_stocks_size`
    - Paid: `buy_goods`, `buy_goods_size`, `buy_stocks`, `buy_stocks_size`
  - `phrase` accepts a single string or a list of alternative phrases (case‑insensitive).
  - New phrases: “Grant me some goods”, “Grant me some stocks” (with several aliases).
  - Expanded “iddqd” response with a full command list and notes.
- GoodsService: explicit `grant` (add zero‑cost lots) and `gift` (remove via FIFO without cash) helpers.
- InvestmentsService: explicit `grant_asset` and `gift_asset` helpers.
- README updates documenting the new CloseAI trigger schema and free helpers in services.

## [1.4.0]

### Added
- Phone tab (shortcut `5`) with the following apps:
  - Home: centered ASCII home screen with smooth glow/pulse animation.
  - WhatsUp: live messenger feed (same rendering as Newspaper modal) that keeps up‑to‑date as new messages arrive.
  - Camera (Gallery): centered, scrollable ASCII picture; scroll starts near the middle for best framing.
  - Wordle Game: lightweight, playable 5‑letter word game with per‑letter coloring and restart.
- Phone apps menu redesigned as a 3‑column grid with emoji icons and hover highlighting.
- Wordle improvements:
  - Guess input moved to the bottom; added Guess / Play Again / Restart buttons.
  - Gameplay stats panel (tries used/limit).
  - Duplicate‑letter logic fixed (excess duplicates above target count are grey).
  - Settings (see `phone_settings.py`): `wordle_max_tries` (default 10), `wordle_validate_in_dictionary` (default False).
  - Repository for words + curated list expanded to 500+ common 5‑letter words.
- Lotto: Owned Tickets table shows a Wins column (per‑ticket win count).

### Changed
- WhatsUp panel now shows a title and auto‑refreshes when messages are added (via global refresh).
- Camera/WhatsUp panels fill SCREEN height and are horizontally/vertically centered where appropriate.
- Various UI polish: consistent button sizing/padding in Wordle, Lotto panels, and Phone grid tiles.


## [1.3.0] - 2025-11-14

### Added
- Lotto UI tab with four panels:
  - Buy Ticket (opens numeric input modal)
  - Owned Tickets (DataTable with per‑ticket actions)
  - Today’s Draw (shows latest 6 drawn numbers)
  - Win History (DataTable of past wins)
- Modals for the lotto flow:
  - BuyTicketModal (6 number inputs with validation)
  - TicketActionsModal (Activate/Deactivate, Remove)
  - LottoWinnerModal to summarize daily winnings after travel
- Keyboard shortcut `4` to jump to the Lotto tab.
- Save/Load persistence for lotto data (tickets, today’s draw, win history).
- Owned Tickets table now shows two extra columns: Cost and Reward.
  - Cost accumulates actual spend (initial ticket price + successful renewals).
  - Reward accumulates payouts won by that ticket.

- Lotto Actions panel (compact bar, styled like Bank Actions) with:
  - Buy ticket (opens modal without preset numbers)
  - Lucky shot! (opens modal prefilled with 6 random unique numbers)
- Tickets Summary panel with totals (Owned/Active, Cost, Reward, P/L).
- Today’s Draw shows per‑day totals: Today’s cost, Today’s payout, and P/L.
- Owned Tickets table includes P/L column per ticket.
 - New travel event: LottoTicketLost (loss) — randomly removes one active lotto ticket (no refund). Triggers only if you have at least one active ticket. Shows a loss modal and logs a messenger entry.

### Changed
- Lotto Winner modal styling updated to match the existing dividend/event modal
  (uses the same positive alert chrome and OK button with Enter binding).

- Buy Ticket modal reworked to compact single‑row inputs with labels; fixed
  auto‑height and ensured buttons are always visible.
- Ticket Actions modal:
  - Restyled to match Buy Ticket modal
  - Button spacing standardized; two actions side‑by‑side
  - Deactivate button uses a flat pastel‑orange warning style
- Tables now sort newest first (Owned Tickets by purchase day, Win History by day).
- Panel heights and table scroll behavior aligned with other tabs.

### Integration
- Daily lotto processing is executed on travel:
  - Performs draw, attempts renewals (deactivates on insufficient funds),
    evaluates winnings, credits wallet, and records win history.
  - Winner summary modal is shown after any dividend or travel event modals.

### Notes
- Existing saves from older versions will show Cost/Reward as $0 for historical
  tickets until further renewals/wins occur. Data is tracked going forward.
- No schema version bump required; lotto payload is optional in v2 saves.

[Unreleased]: https://github.com/artdarek/MerchantTycoon/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/artdarek/MerchantTycoon/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/artdarek/MerchantTycoon/compare/v1.3.0...v1.4.0
