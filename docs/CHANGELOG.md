# Recent Features & Changes

## Version 1.2.4 Updates

### 🏆 Contest Win Event (Replaces Lottery Event)

**New Feature**: Random contest wins with tiered prize system

**What Changed:**
- Replaced the old lottery-style event with a more thematic "Contest Win" event
- Instead of matching numbers, players now win 1st/2nd/3rd place in randomly selected contests
- More variety and fun event messaging

**Contest System:**
- **10 Configurable Contests**: Each with unique name and base prize
  - International Sandwich Championship ($1,000)
  - World Pillow Fighting Cup ($2,000)
  - National Speed Napping Finals ($3,000)
  - Intergalactic Beard Grooming Show ($1,500)
  - Extreme Ironing Masters ($2,500)
  - Professional Duck Herding Competition ($1,200)
  - Global Air Guitar Championship ($1,800)
  - Underground Sock Sorting League ($800)
  - Elite Backwards Running Marathon ($2,200)
  - International Paper Airplane Distance Cup ($1,000)

**Prize Calculation:**
- **1st Place**: Full base prize amount
- **2nd Place**: ceil(base / 2) - half the base prize (rounded up)
- **3rd Place**: ceil(base / 4) - quarter of base prize (rounded up)
- **Weighted Selection**: Favors lower places (3rd most common, 1st least common)
- **Place Weights**: [1st: 10, 2nd: 30, 3rd: 60]

**Example Prizes:**
```
World Pillow Fighting Cup (base: $2,000)
  - 1st place: $2,000
  - 2nd place: $1,000
  - 3rd place: $500

National Speed Napping Finals (base: $3,000)
  - 1st place: $3,000
  - 2nd place: $1,500
  - 3rd place: $750
```

**Event Messages:**
```
🏆 CONTEST WIN! You won 2nd place in World Pillow Fighting Cup! Prize: $1,000
🏆 CONTEST WIN! You won 3rd place in Underground Sock Sorting League! Prize: $200
🏆 CONTEST WIN! You won 1st place in International Sandwich Championship! Prize: $1,000
```

**Implementation Details:**
- New handler: `ContestWinEventHandler` (`src/merchant_tycoon/engine/events/gain/contest_win_event.py`)
- Event type: `"gain"` (positive event)
- Event weight: 3.0 (same as old lottery)
- Eligibility: Always (no preconditions)
- Configuration: `SETTINGS.events.contest_names` and `SETTINGS.events.contest_place_weights`

**Configuration (`EventsSettings`):**
```python
contest_names: list[tuple[str, int]] = [
    ("Contest Name", base_prize),
    ...
]
contest_place_weights: list[int] = [10, 30, 60]  # [1st, 2nd, 3rd]
```

**Removed:**
- `LotteryEventHandler` (old lottery-style event)
- Lottery configuration: `lottery_tiers`, `lottery_weights`, `lottery_reward_ranges`
- File deleted: `src/merchant_tycoon/engine/events/gain/lottery_event.py`

**Why This Change:**
- Prepares for actual Lotto system (separate feature)
- More entertaining and varied event messages
- Easier to configure and extend with new contests
- Better thematic fit for a merchant trading game
- Clearer prize structure (1st/2nd/3rd vs. matching numbers)

**Developer Notes:**
- Contests are fully configurable - developers can easily add/remove/modify contests
- Base prizes can be adjusted per contest
- Place probability weights can be modified
- Event weight can be changed to make contests more/less frequent
- No data migration required - backward compatible with existing saves

### 🎮 Gameplay Impact

**Contest Win Event:**
- Prize range: $200 - $3,000 (depending on contest and place won)
- Most common outcome: 3rd place (~60% of wins)
- Rare outcome: 1st place (~10% of wins)
- Average prize: ~$600-$800 per event
- Adds variety and humor to travel events
- Same frequency as old lottery event (weight: 3)

### 🔍 Testing & Validation

All changes validated:
- ✅ ContestWinEventHandler imports correctly
- ✅ 10 contests loaded with proper configuration
- ✅ Prize calculations accurate for all places
- ✅ Events trigger with correct messaging
- ✅ Handler properly registered in travel events service
- ✅ LotteryEventHandler completely removed
- ✅ GameEngine initializes without errors
- ✅ Backward compatible with existing save files

---

## Version 1.2.3 Updates

### 📰 Newspaper Modal (Message History Viewer)

**New Feature**: Full message history in a scrollable newspaper-style modal

**Keybinding**: Press **N** to open the Newspaper modal

**Features:**
- **Scrollable View**: Browse complete message history from the current game session
- **Date Separators**: Messages grouped by date for easy navigation
- **Color-Coded Messages**: Same visual styling as messenger panel
  - 🔴 Red dot for errors
  - 🟡 Amber dot for warnings
  - 🔵 Teal dot for info messages
  - ⚪ Gray dot for debug messages
- **Timestamps**: Full date and time for each message
- **Auto-scroll**: Automatically scrolls to show latest messages
- **Modal Controls**: Close with ESC or N key

**Implementation:**
- New modal: `NewspaperModal` (`src/merchant_tycoon/ui/general/modals/newspaper_modal.py`)
- Keybinding added: `Binding("n", "newspaper", "Newspaper", show=False)`
- Fetches entries from: `engine.messenger.get_entries()`
- Styling: Custom newspaper-themed CSS classes

**Use Cases:**
- Review past events and transactions
- Track price changes over time
- Analyze event patterns
- Verify transaction history
- Debug game state issues

**UI/UX:**
- Large scrollable container for comfortable reading
- Clear visual hierarchy with date separators
- Consistent message formatting across all log levels
- Easy to dismiss (ESC or N to toggle)

### 🚔 Stolen Goods Event Description Enhancement

**Improvement**: Clarified stolen goods event messaging

**Changes:**
- **Old Message**: "🚔 STOLEN GOODS! Your last purchase was confiscated: lost Nx [item]"
- **New Message**: "🚔 STOLEN GOODS! You bought stolen goods! Your last purchase was confiscated: lost Nx [item]"

**Rationale:**
- Makes it clearer WHY goods were confiscated (you unknowingly purchased stolen merchandise)
- Better storytelling and event context
- More realistic scenario explanation

**Affected File:**
- `src/merchant_tycoon/engine/events/loss/stolen_goods_event.py`

### 🏦 Bank Modal UI Simplification

**Improvement**: Streamlined bank operation modals for cleaner UX

**Changes:**

1. **Loan Modal:**
   - Removed redundant APR display from prompt (already shown in loans list)
   - Removed max loan capacity from prompt (cluttered the UI)
   - Cleaner, more focused borrowing experience
   - Changed "no capacity" message from warning to error for better visibility

2. **Deposit Modal:**
   - Removed "Cash available: $X,XXX" from prompt
   - Cash balance already visible in stats panel at top
   - More streamlined deposit flow

3. **Withdraw Modal:**
   - Removed "Bank balance: $X,XXX" from prompt
   - Bank balance already visible in stats panel at top
   - Reduced modal clutter

4. **Loan Repay Modal:**
   - Removed informational note about APR rates
   - Information already available in loan list
   - Faster, simpler repayment process

**Rationale:**
- Redundant information removed (already displayed in stats panel and loan tables)
- Faster user flow with less reading required
- Modal prompts focus only on the action input
- Cleaner, more professional UI/UX

**Affected Files:**
- `src/merchant_tycoon/app.py` (action_loan, action_bank_deposit, action_bank_withdraw)
- `src/merchant_tycoon/ui/bank/modals/loan_repay_modal.py`

### 📝 Documentation Updates

**README.md:**
- Added **N** keybinding for Newspaper modal to Global Controls section
- Updated controls table with Newspaper feature description

**Impact:**
- Players now have complete visibility into game message history
- Improved event tracking and analysis capabilities
- Better UX for reviewing past decisions and outcomes

### 🎮 Gameplay Impact

**Newspaper Modal:**
- Better game state transparency
- Easier to track event patterns and sequences
- Helpful for analyzing profit/loss trends
- Useful for debugging unusual situations
- Can review price change notifications from past days

**UI Improvements:**
- Faster bank operations with less modal clutter
- Reduced cognitive load during financial transactions
- More professional, streamlined interface
- Better focus on the actual input required

### 🔍 Testing & Validation

All changes validated:
- ✅ Newspaper modal opens with N key
- ✅ Message history displays correctly with timestamps
- ✅ Date separators working
- ✅ Color-coded message levels accurate
- ✅ Auto-scroll to latest messages functional
- ✅ ESC and N keys both close the modal
- ✅ Bank modals streamlined successfully
- ✅ Stolen goods event message updated
- ✅ No regressions in existing features

---

## Version 1.2.2 Updates

### 💰 Dividend System

**New Feature**: Regular dividend payouts for stock holdings

- **Payout Schedule**: Every 11 days
- **Minimum Holding Period**: 10 days to qualify
- **Dividend Rates**: 0.1-0.3% of current share price per payout (varies by stock)
- **Eligible Assets**: Select stocks only (CDR, SQR, others - check asset details)
- **Payment Method**: Dividends deposited directly to bank account
- **Tracking**: Cumulative dividend earnings shown per investment lot

**Implementation Details:**
- Added `dividend_rate` field to `Asset` model (stocks with >0 rate pay dividends)
- Added `days_held` and `dividend_paid` fields to `InvestmentLot` model
- New method: `InvestmentsService.calculate_and_pay_dividends()`
- Dividends trigger during travel (daily advancement)
- Separate modal notification from travel events

**Example Calculation:**
- 100 shares of CDR at $200/share with 0.1% dividend rate
- Per share dividend: $200 × 0.001 = $0.20
- Total payout: $0.20 × 100 shares = $20

### 🏦 WalletService Architecture

**New Service**: Centralized cash management system

**Purpose**: Single source of truth for all cash operations across the game

**API:**
```python
class WalletService:
    def get_balance() -> int          # Query current cash
    def set_balance(value: int)       # Direct balance update (use with caution)
    def can_afford(amount: int) -> bool  # Check affordability
    def earn(amount: int)             # Add cash
    def spend(amount: int) -> bool    # Deduct cash with validation
```

**Benefits:**
- **Consistent validation**: All cash operations validated before execution
- **Single source of truth**: `state.cash` only modified through WalletService
- **Cleaner code**: Removed scattered `self.state.cash` manipulations
- **Type safety**: All operations properly validated

**Integration:**
- ✅ GoodsService: buy/sell goods
- ✅ InvestmentsService: buy/sell assets
- ✅ BankService: deposits, withdrawals, loans, repayments
- ✅ TravelService: travel fees

**Removed Features:**
- Transaction logging (unused, removed for simplicity)
- Messenger integration (services handle their own messaging)
- Optional dependencies cleanup

### 🎯 Travel Events System Improvements

**Enhancements**: Better separation of concerns and event handling

**Changes:**
1. **Separated dividend from travel events**
   - Dividends are game mechanics, not random events
   - Dividend modal shown separately before/after travel events
   - Cleaner event messaging

2. **Improved event handling**
   - Consistent 4-value return from `travel()`: `(success, msg, events_list, dividend_modal)`
   - Events logged to messenger within services
   - Better error handling for edge cases

3. **New event type**: `neutral` events
   - Not all events are gains or losses
   - Better categorization of event impacts

### 🔧 Service Architecture Improvements

**Refactoring**: Cleaner dependency injection and service initialization

**Key Changes:**

1. **Removed Optional dependencies**
   - All service dependencies are now required and explicit
   - Fail-fast approach: missing dependencies cause immediate errors
   - Removed ~80+ lines of defensive `if service:` checks
   - Affected services: GoodsService, InvestmentsService, BankService, TravelService

2. **ClockService enhancements**
   - New method: `advance_day()` centralizes day/date progression
   - Consistent calendar advancement across all services
   - Removed scattered date manipulation logic

3. **MessengerService injection**
   - Direct injection instead of acquisition hacks
   - Cleaner service initialization
   - No more `getattr(other_service, 'messenger', None)` patterns

4. **Travel fee extraction**
   - New private method: `TravelService._calculate_travel_fee()`
   - Separated calculation from business logic
   - Easier to test and modify

### 📊 Bank Account Enhancements

**New Feature**: Visual balance history chart

**Implementation:**
- New panel: `AccountBalanceChartPanel`
- Location: Bank tab, left column (between Actions and Transactions)
- Chart type: ASCII line chart with slope indicators

**Chart Features:**
- **Data source**: Last 50 bank transactions
- **Visualization**:
  - `╱` for upward trends
  - `╲` for downward trends
  - `─` for flat periods
  - `●` for most recent point
- **Auto-scaling**: Adjusts to min/max balance range
- **Labels**: Max balance (top), min balance (bottom), transaction count (footer)
- **Edge cases**: Handles no data, constant balances, varying ranges

**Update method**: `update_chart()` called during `refresh_all()`

### 🔄 Domain Model Updates

**Investment Lots:**
- Added `days_held: int = 0` - tracks holding period for dividend eligibility
- Added `dividend_paid: int = 0` - cumulative dividends earned per lot
- Both fields displayed in Investment Lots panel

**Bank Transactions:**
- New transaction type: `"dividend"` for dividend payouts
- Better transaction categorization

**Assets:**
- Added `dividend_rate: float = 0.0` - annual dividend yield (0 = no dividends)
- Select stocks configured with 0.1-0.3% dividend rates

### 📈 UI/UX Improvements

**Investment Lots Panel:**
- New column: "Dividend" showing cumulative dividend earnings per lot
- Better profit/loss tracking with dividend consideration

**Bank Account Panel:**
- Balance history chart for visual trend analysis
- Easier to spot deposit/withdrawal patterns
- Quick overview of account growth

**Event Notifications:**
- Dividend modal separate from travel events
- Clearer event categorization (gain/loss/neutral)
- Better messaging hierarchy

### 🔒 Configuration Updates

**New Settings** (`src/merchant_tycoon/config/investments_settings.py`):
```python
dividend_interval_days: int = 11        # Payout frequency
dividend_min_holding_days: int = 10     # Minimum holding period
```

**Assets Configuration** (`src/merchant_tycoon/domain/assets.py`):
- Updated stock definitions with `dividend_rate` field
- Configured dividend-paying stocks (CDR, SQR, etc.)

### 🐛 Bug Fixes

1. **Dividend timing bug**: Fixed payout calculation relative to holding period
   - Initial issue: Dividends paid on day 8 instead of day 4
   - Root cause: `days_held` starts at 0, increments during travel
   - Fix: Adjusted `dividend_min_holding_days` calculation

2. **Travel return value consistency**: Fixed inconsistent tuple unpacking
   - Error: "ValueError: not enough values to unpack (expected 4, got 3)"
   - Fix: All error cases now return 4 values: `(False, msg, [], None)`

3. **Messenger acquisition hack**: Removed indirect service references
   - Replaced: `getattr(self.bank_service, 'messenger', None)`
   - With: Direct `messenger_service` injection

### 🏗️ Code Quality Improvements

**Simplifications:**
- Removed unused transaction logging from WalletService (~80 lines)
- Removed Optional[] type hints where dependencies are required
- Consolidated event messaging logic
- Better separation of concerns (dividend vs events)

**Documentation:**
- Updated README with dividend system details
- Added examples and calculations
- Documented WalletService API
- Updated architecture diagrams

### 📝 Breaking Changes

⚠️ **WalletService API Changes**:

If you were using WalletService directly (unlikely in normal gameplay):

```python
# OLD (no longer works)
wallet.spend(amount, "reason string")
wallet.earn(amount, "reason string")

# NEW (required)
wallet.spend(amount)
wallet.earn(amount)
```

**Service Constructor Changes**:
- All services now require explicit dependencies (no Optional[])
- WalletService added to: BankService, GoodsService, InvestmentsService, TravelService
- MessengerService now directly injected to TravelService

### 📊 Statistics

**New Code:**
- Files created: 3 (WalletService, AccountBalanceChartPanel, run_local.py)
- New methods: 8+ (dividend system, wallet operations, chart rendering)
- Configuration additions: 2 settings (dividend interval, min holding)

**Code Removed:**
- Lines removed: ~150+ (transaction logging, Optional dependencies, defensive checks)
- Files removed: 0
- Deprecated methods: 0

**Refactoring:**
- Files modified: 15+
- Services refactored: 4 (GoodsService, InvestmentsService, BankService, TravelService)
- Import updates: 10+ files

### 🎮 Gameplay Impact

**Dividend System:**
- New passive income stream from stock investments
- Encourages long-term holding strategies
- Rewards portfolio diversification
- Adds financial planning depth

**Improved Banking:**
- Visual feedback on wealth accumulation
- Easier to track financial progress
- Better understanding of cash flow patterns

**Better Event System:**
- Clearer distinction between random events and game mechanics
- Improved event notifications
- More predictable gameplay flow

### 🔍 Testing & Validation

All changes validated:
- ✅ WalletService spend/earn operations working
- ✅ BankService deposit/withdraw with WalletService
- ✅ Dividend calculations accurate
- ✅ Dividend modal display working
- ✅ Balance chart rendering correctly
- ✅ Travel events separated from dividends
- ✅ All service dependencies properly injected
- ✅ No circular imports
- ✅ Save/load compatibility maintained

### 🚀 Running the Game

**Local Development:**
```bash
# Use local source instead of installed package
PYTHONPATH=src python3 -m merchant_tycoon

# Or use the convenience script
python3 run_local.py
```

**Note**: Python 3.13+ required for package installation. For development with Python 3.12, use the PYTHONPATH method above.

---

**Migration Guide**: Version 1.2.x is backward compatible with 1.1.x save files. The game will automatically initialize new fields (`days_held`, `dividend_paid`) on existing investment lots. No manual migration required.

## Version 1.1.x Updates

### 🎚️ Game Difficulty System

**New Feature**: Multiple difficulty levels with configurable starting parameters

- **5 Difficulty Levels**: Playground, Easy, Normal, Hard, Insane
- **Starting Cash Range**: $0 (Insane) to $1,000,000 (Playground)
- **Starting Cargo Capacity**: 1 slot (Insane) to 1000 slots (Playground)
- **Selection UI**: Modal dialog when starting new game (F1)

**Implementation Details:**
- Model: `GameDifficultyLevel` (renamed from `DifficultyLevel`)
- Constant: `GAME_DIFFICULTY_LEVELS` (renamed from `DIFFICULTY_LEVELS`)
- Location: `src/merchant_tycoon/domain/game_difficulty_levels.py`

### 📦 New Product Categories

**Expanded from 15 to 31 products** across 4 main categories:

#### 🖥️ Electronics (18 products)
- **Standard Electronics** (15): TV, Computer, Printer, Phone, Camera, Laptop, Tablet, Console, Headphones, Smartwatch, VR Headset, Coffee Machine, Powerbank, USB Charger, Pendrive
- **Luxury Electronics** (3): Gaming Laptop ($3,000), High-end Drone ($2,500), 4K OLED TV ($2,500)
- Category renamed from "hardware" to "electronics"

#### 💎 Jewelry (2 products)
- Luxury Watch ($6,000)
- Diamond Necklace ($8,000)
- High volatility (±60-70%)

#### 🚗 Cars (6 products) - **NEW CATEGORY**
- **Standard Cars**: Fiat ($20,000), Opel Astra ($40,000), Ford Focus ($50,000)
- **Luxury Cars**: Ferrari ($100,000), Bentley ($200,000), Bugatti ($300,000)
- Price volatility: ±30-60%

#### ⚠️ Contraband (5 products) - **NEW CATEGORY**
- **Drugs**: Weed ($500), Cocaine ($2,000)
- **Weapons**: Grenade ($100), Pistol ($500), Shotgun ($1,000)
- High risk/reward with extreme price variations
- Volatility: ±80-100%

**Product Types:**
- `"standard"`: Stable, lower volatility
- `"luxury"`: Higher prices, more volatility
- `"contraband"`: Extreme volatility, highest risk/reward

### 🏗️ Domain Refactoring

**Separated domain constants into individual files** for better modularity:

**Before:**
```python
# Old structure
from merchant_tycoon.domain.constants import GOODS, CITIES, ASSETS, DIFFICULTY_LEVELS
```

**After:**
```python
# New structure
from merchant_tycoon.domain.goods import GOODS
from merchant_tycoon.domain.cities import CITIES
from merchant_tycoon.domain.assets import ASSETS
from merchant_tycoon.domain.game_difficulty_levels import GAME_DIFFICULTY_LEVELS
```

**New Files:**
- `src/merchant_tycoon/domain/goods.py` - 31 products
- `src/merchant_tycoon/domain/cities.py` - 11 cities
- `src/merchant_tycoon/domain/assets.py` - 20 assets
- `src/merchant_tycoon/domain/game_difficulty_levels.py` - 5 difficulty levels

**Removed:**
- `src/merchant_tycoon/domain/constants.py` (consolidated into separate files)

### 📝 Model Renaming

For consistency with constant naming:

**Before:**
```python
from merchant_tycoon.domain.model.difficulty_level import DifficultyLevel
```

**After:**
```python
from merchant_tycoon.domain.model.game_difficulty_level import GameDifficultyLevel
```

**Files Changed:**
- Created: `src/merchant_tycoon/domain/model/game_difficulty_level.py`
- Removed: `src/merchant_tycoon/domain/model/difficulty_level.py`

### 📚 Documentation Updates

**README.md** - Major updates:
1. **New Section**: Game Difficulty Levels (with table)
2. **Expanded Section**: Goods & Product Categories (detailed breakdown of all 31 products)
3. **New Section**: Domain Architecture (explains file structure and import patterns)
4. **Updated Features List**: Added difficulty levels, product counts, category details
5. **Updated Inventory Management**: Reflects difficulty-based starting capacity

**Code Examples Verified:**
- All import statements tested and working
- Domain structure accurately documented
- Model imports validated

### 🔧 Breaking Changes

⚠️ **Import Path Changes** (refactoring):

If you were importing from the old locations, update your imports:

```python
# OLD (no longer works)
from merchant_tycoon.domain.constants import GOODS, CITIES, ASSETS, DIFFICULTY_LEVELS
from merchant_tycoon.domain.model.difficulty_level import DifficultyLevel

# NEW (required)
from merchant_tycoon.domain.goods import GOODS
from merchant_tycoon.domain.cities import CITIES
from merchant_tycoon.domain.assets import ASSETS
from merchant_tycoon.domain.game_difficulty_levels import GAME_DIFFICULTY_LEVELS
from merchant_tycoon.domain.model.game_difficulty_level import GameDifficultyLevel
```

### 📊 Statistics

**Domain Constants:**
- GOODS: 31 products (up from ~15)
- CITIES: 11 cities (unchanged)
- ASSETS: 20 assets (unchanged)
- GAME_DIFFICULTY_LEVELS: 5 levels (new)

**Code Organization:**
- Domain files: 4 new constant files
- Models: 1 renamed model
- Imports updated: 9 files across the codebase

### 🎮 Gameplay Impact

**Difficulty Selection:**
- Players now choose difficulty when starting new game
- Affects starting cash and cargo capacity
- Provides experiences from sandbox (Playground) to extreme survival (Insane)

**Product Variety:**
- More trading opportunities with 31 products
- New high-value items (cars, luxury goods)
- High-risk contraband for experienced players
- Better price arbitrage potential across categories

**Strategic Depth:**
- Mix stable products with high-risk contraband
- Contraband highly profitable in specific city combinations
- Luxury goods excel in wealthy cities (Paris, London, Stockholm)

### 🔍 Testing & Validation

All changes validated:
- ✅ Import paths verified
- ✅ Domain constants loaded successfully
- ✅ GameEngine instantiation working
- ✅ Game difficulty system functional
- ✅ All 31 products accessible
- ✅ No circular imports
- ✅ Documentation examples tested

---

**Migration Guide**: If updating from previous version, simply re-import. The game will automatically use the new domain structure. Save files remain compatible.