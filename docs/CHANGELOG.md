# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning.

## [Unreleased]

## [1.4.0] - 2025-11-14

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

[Unreleased]: https://github.com/artdarek/MerchantTycoon/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/artdarek/MerchantTycoon/compare/v1.3.0...v1.4.0
