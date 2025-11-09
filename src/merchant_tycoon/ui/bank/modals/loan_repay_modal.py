from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.domain.model.loan import Loan


class LoanRepayModal(ModalScreen):
    """Modal for repaying a specific loan.

    Shows a Select listing active loans and an Input for amount. Switching the
    selection auto-fills the amount with the selected loan's remaining balance.
    On confirm, calls the provided callback with (loan_id: int, amount: int).
    """

    def __init__(self, engine: GameEngine, callback, default_loan_id: int | None = None, default_amount: int | None = None):
        super().__init__()
        self.engine = engine
        self.callback = callback
        self._loan_map: dict[str, Loan] = {}
        self.default_loan_id = default_loan_id
        self.default_amount = default_amount
        self._suppress_autofill = False

    def compose(self) -> ComposeResult:
        with Container(id="repay-modal"):
            yield Label("💳 Repay Loan", id="modal-title")

            # Informational note about rates (APR)
            try:
                offer_pct = float(getattr(self.engine.bank_service, "loan_apr_today", 0.10)) * 100.0
            except Exception:
                offer_pct = 10.0
            try:
                bank_apr_pct = float(getattr(self.engine.state.bank, "interest_rate_annual", 0.02)) * 100.0
            except Exception:
                bank_apr_pct = 2.0
            yield Label(
                f"Today's new-loan APR: {offer_pct:.1f}% · Bank savings APR: {bank_apr_pct:.1f}%",
                id="repay-rates-info",
            )
            yield Label("Note: Each loan keeps its own fixed rate set on the day it was taken.", id="repay-rates-note")

            # Build options from active loans (remaining > 0)
            options: list[tuple[str, str]] = []
            active_loans = [ln for ln in (self.engine.state.loans or []) if getattr(ln, "remaining", 0) > 0]
            # Sort by oldest first
            active_loans.sort(key=lambda ln: ln.day_taken)
            for ln in active_loans:
                apr = float(getattr(ln, 'rate_annual', 0.10))
                label = (
                    f"#${ln.loan_id}  Day {ln.day_taken}  Principal: ${ln.principal:,}  "
                    f"Remaining: ${ln.remaining:,}  Rate APR: {apr*100:.1f}%"
                )
                key = str(ln.loan_id)
                options.append((label, key))
                self._loan_map[key] = ln

            yield Label("Select loan to repay:")
            yield Select(options, prompt="Choose a loan...", id="loan-select")
            yield Label("Enter amount to repay:")
            yield Input(placeholder="Amount...", type="integer", id="amount-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Repay", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        """Preselect loan and preflll amount if defaults provided; otherwise use remaining."""
        try:
            select_widget = self.query_one("#loan-select", Select)
            amount_input = self.query_one("#amount-input", Input)
        except Exception:
            return
        if self.default_loan_id is not None:
            try:
                self._suppress_autofill = True
                select_widget.value = str(int(self.default_loan_id))
            except Exception:
                pass
            finally:
                self._suppress_autofill = False
        # Determine base amount: default_amount if provided else remaining for selected loan
        loan_key = select_widget.value
        ln = self._loan_map.get(loan_key) if loan_key else None
        base_amount = None
        if self.default_amount is not None:
            try:
                base_amount = int(self.default_amount)
            except Exception:
                base_amount = None
        if base_amount is None and ln is not None:
            base_amount = int(getattr(ln, "remaining", 0))
        if base_amount is not None:
            try:
                amount_input.value = str(int(base_amount))
            except Exception:
                pass

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "loan-select" and event.value:
            if getattr(self, "_suppress_autofill", False):
                return
            ln = self._loan_map.get(event.value)
            if ln:
                try:
                    amt_input = self.query_one("#amount-input", Input)
                    amt_input.value = str(int(ln.remaining))
                except Exception:
                    pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#loan-select", Select)
            input_widget = self.query_one("#amount-input", Input)

            loan_key = select_widget.value
            amount_str = input_widget.value.strip()
            self.dismiss()
            if loan_key and amount_str:
                try:
                    loan_id = int(loan_key)
                    amount = int(amount_str)
                    self.callback(loan_id, amount)
                except ValueError:
                    # Ignore invalid input silently
                    pass
        else:
            self.dismiss()
