"""Lotto service for daily lottery system."""

import random
from typing import TYPE_CHECKING, List, Tuple, Optional

from merchant_tycoon.domain.model.lotto_ticket import LottoTicket
from merchant_tycoon.domain.model.lotto_draw import LottoDraw
from merchant_tycoon.domain.model.lotto_win_history import LottoWinHistory
from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.messenger_service import MessengerService
    from merchant_tycoon.engine.services.wallet_service import WalletService
    from merchant_tycoon.engine.services.modal_queue_service import ModalQueueService


class LottoService:
    """Service for handling daily lottery operations.

    Manages:
    - Ticket purchasing and removal
    - Daily draws
    - Win evaluation and payouts
    - Ticket renewal fees
    - Win history tracking
    """

    def __init__(
        self,
        state: "GameState",
        messenger_service: "MessengerService",
        wallet_service: "WalletService",
        modal_queue_service: "ModalQueueService"
    ):
        """Initialize LottoService.

        Args:
            state: Game state containing lotto data
            messenger: Messenger service for logging
            wallet: Wallet service for payments
            modal_queue: Modal queue for adding lotto winner modals
        """
        self.state = state
        self.messenger_service = messenger_service
        self.wallet_service = wallet_service
        self.modal_queue_service = modal_queue_service

    def buy_ticket(self, numbers: List[int]) -> Tuple[bool, str]:
        """Purchase a new lottery ticket.

        Args:
            numbers: List of 6 unique numbers to play

        Returns:
            Tuple of (success, message)
        """
        # Validate numbers
        if len(numbers) != SETTINGS.lotto.numbers_per_ticket:
            return False, f"Must select exactly {SETTINGS.lotto.numbers_per_ticket} numbers"

        if len(set(numbers)) != len(numbers):
            return False, "Numbers must be unique"

        if any(n < 1 or n > SETTINGS.lotto.number_range_max for n in numbers):
            return False, f"Numbers must be between 1 and {SETTINGS.lotto.number_range_max}"

        # Check ticket limit
        if SETTINGS.lotto.max_tickets > 0:
            if len(self.state.lotto_tickets) >= SETTINGS.lotto.max_tickets:
                return False, f"Maximum {SETTINGS.lotto.max_tickets} tickets allowed"

        # Check if player can afford
        if not self.wallet_service.can_afford(SETTINGS.lotto.ticket_price):
            return False, f"Not enough cash! Need ${SETTINGS.lotto.ticket_price:,}"

        # Charge player
        if not self.wallet_service.spend(SETTINGS.lotto.ticket_price):
            return False, "Payment failed"
        # Track today's cost (purchase)
        try:
            self.state.lotto_today_cost = int(getattr(self.state, "lotto_today_cost", 0) or 0) + int(SETTINGS.lotto.ticket_price)
        except Exception:
            pass

        # Create and add ticket
        ticket = LottoTicket(
            numbers=sorted(numbers),  # Sort for consistent display
            purchase_day=self.state.day,
            active=True,
            total_cost=int(SETTINGS.lotto.ticket_price),
            total_reward=0,
        )
        self.state.lotto_tickets.append(ticket)

        self.messenger_service.info(
            f"Bought lotto ticket: {sorted(numbers)} for ${SETTINGS.lotto.ticket_price:,}",
            tag="lotto"
        )

        return True, f"Ticket purchased! Numbers: {sorted(numbers)}"

    def remove_ticket(self, ticket_index: int) -> Tuple[bool, str]:
        """Remove (discard) a ticket.

        Args:
            ticket_index: Index of ticket to remove

        Returns:
            Tuple of (success, message)
        """
        if ticket_index < 0 or ticket_index >= len(self.state.lotto_tickets):
            return False, "Invalid ticket index"

        ticket = self.state.lotto_tickets[ticket_index]
        self.state.lotto_tickets.pop(ticket_index)

        self.messenger_service.info(
            f"Removed lotto ticket: {ticket.numbers}",
            tag="lotto"
        )

        return True, f"Ticket removed: {ticket.numbers}"

    def toggle_ticket_active(self, ticket_index: int) -> Tuple[bool, str]:
        """Toggle ticket active status.

        Args:
            ticket_index: Index of ticket to toggle

        Returns:
            Tuple of (success, message)
        """
        if ticket_index < 0 or ticket_index >= len(self.state.lotto_tickets):
            return False, "Invalid ticket index"

        ticket = self.state.lotto_tickets[ticket_index]
        ticket.active = not ticket.active

        status = "activated" if ticket.active else "deactivated"
        self.messenger_service.info(
            f"Ticket {ticket.numbers} {status}",
            tag="lotto"
        )

        return True, f"Ticket {status}: {ticket.numbers}"

    def perform_daily_draw(self) -> LottoDraw:
        """Perform daily lottery draw.

        Generates 6 unique random numbers and saves as today's draw.

        Returns:
            LottoDraw object with today's numbers
        """
        # Generate 6 unique random numbers
        numbers = random.sample(
            range(1, SETTINGS.lotto.number_range_max + 1),
            SETTINGS.lotto.numbers_per_ticket
        )

        draw = LottoDraw(
            day=self.state.day,
            numbers=sorted(numbers)
        )

        # Save as today's draw
        self.state.lotto_today_draw = draw
        # Reset today's aggregates for the new day
        try:
            self.state.lotto_today_cost = 0
            self.state.lotto_today_payout = 0
        except Exception:
            pass

        self.messenger_service.info(
            f"Daily lotto draw: {sorted(numbers)}",
            tag="lotto"
        )

        return draw

    def charge_renewal_fees(self) -> Tuple[int, int]:
        """Charge daily renewal fees for all active tickets.

        Deactivates tickets if player cannot afford renewal.

        Returns:
            Tuple of (tickets_renewed, tickets_deactivated)
        """
        renewed_count = 0
        deactivated_count = 0

        for ticket in self.state.lotto_tickets:
            if not ticket.active:
                continue

            # Try to charge renewal fee
            if self.wallet_service.can_afford(SETTINGS.lotto.ticket_renewal_cost):
                if self.wallet_service.spend(SETTINGS.lotto.ticket_renewal_cost):
                    renewed_count += 1
                    # Track cost actually paid for this specific ticket
                    try:
                        ticket.total_cost = int(getattr(ticket, "total_cost", 0)) + int(SETTINGS.lotto.ticket_renewal_cost)
                    except Exception:
                        pass
                    # Also add to today's cost aggregate
                    try:
                        self.state.lotto_today_cost = int(getattr(self.state, "lotto_today_cost", 0) or 0) + int(SETTINGS.lotto.ticket_renewal_cost)
                    except Exception:
                        pass
                else:
                    # Payment failed, deactivate
                    ticket.active = False
                    deactivated_count += 1
            else:
                # Cannot afford, deactivate
                ticket.active = False
                deactivated_count += 1

        if renewed_count > 0:
            total_cost = renewed_count * SETTINGS.lotto.ticket_renewal_cost
            self.messenger_service.info(
                f"Renewed {renewed_count} lotto ticket(s) for ${total_cost:,}",
                tag="lotto"
            )

        if deactivated_count > 0:
            self.messenger_service.warn(
                f"Deactivated {deactivated_count} ticket(s) - insufficient funds for renewal",
                tag="lotto"
            )

        return renewed_count, deactivated_count

    def evaluate_winnings(self, drawn_numbers: List[int]) -> List[dict]:
        """Evaluate all active tickets against drawn numbers.

        Args:
            drawn_numbers: List of today's drawn numbers

        Returns:
            List of win records (dicts with ticket, matched, payout)
        """
        wins = []

        for ticket in self.state.lotto_tickets:
            if not ticket.active:
                continue

            # Count matches
            matched = ticket.matches(drawn_numbers)

            # Check if eligible for payout
            if matched >= 2 and matched in SETTINGS.lotto.payouts:
                payout = SETTINGS.lotto.payouts[matched]

                # Award payout
                self.wallet_service.earn(payout)
                # Track total reward on the ticket
                try:
                    ticket.total_reward = int(getattr(ticket, "total_reward", 0)) + int(payout)
                except Exception:
                    pass
                # Aggregate today's payout
                try:
                    self.state.lotto_today_payout = int(getattr(self.state, "lotto_today_payout", 0) or 0) + int(payout)
                except Exception:
                    pass

                # Record win
                win_record = LottoWinHistory(
                    day=self.state.day,
                    ticket_numbers=ticket.numbers.copy(),
                    matched=matched,
                    payout=payout
                )
                self.state.lotto_win_history.append(win_record)

                wins.append({
                    "ticket": ticket.numbers,
                    "matched": matched,
                    "payout": payout
                })

                self.messenger_service.info(
                    f"Lotto win! Matched {matched} numbers: {ticket.numbers} - Won ${payout:,}",
                    tag="lotto"
                )

        return wins

    def process_daily_lotto(self) -> None:
        """Process complete daily lotto operations.

        Performs:
        1. Daily draw
        2. Charge renewal fees
        3. Evaluate winnings
        4. Add lotto winners to modal queue if available

        Lotto winners modal is added directly to modal_queue.
        """
        # Perform daily draw
        draw = self.perform_daily_draw()

        # Charge renewal fees
        self.charge_renewal_fees()

        # Evaluate winnings
        wins = self.evaluate_winnings(draw.numbers)

        # Add lotto winners summary to modal queue
        if wins:
            try:
                total_payout = sum(int(w.get("payout", 0)) for w in wins)
                win_count = len(wins)
                if win_count == 1:
                    summary = f"You had 1 winning ticket and received ${total_payout:,}.\n\n"
                else:
                    summary = f"You had {win_count} winning tickets and received ${total_payout:,}.\n\n"
                lines = ["Winning Tickets:"]
                for i, win in enumerate(wins, 1):
                    numbers_str = ", ".join(str(n) for n in win.get("ticket", []))
                    matched = int(win.get("matched", 0))
                    payout = int(win.get("payout", 0))
                    lines.append(f"#{i}: [{numbers_str}] - {matched} matches → ${payout:,}")
                message = summary + "\n".join(lines)
                self.modal_queue_service.add(message, "gain")
            except Exception:
                pass

    def get_active_ticket_count(self) -> int:
        """Get count of active tickets."""
        return sum(1 for t in self.state.lotto_tickets if t.active)

    def get_total_ticket_count(self) -> int:
        """Get total count of all tickets (active + inactive)."""
        return len(self.state.lotto_tickets)
