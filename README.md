# 🎮 Merchant Tycoon

A terminal-based trading game where you buy low, sell high, travel between cities, and build your fortune through smart trading and investing!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-purple.svg)

## 📸 Screenshots

### 📦 Goods Trading
![Merchant Tycoon - Goods Trading Screen](docs/images/goods.png)
*Main trading interface with market prices, inventory management, and real-time price trends*

### 💼 Investments & Stock Market
![Merchant Tycoon - Investments Screen](docs/images/investments.png)
*Stock market and commodities trading with portfolio tracking and profit/loss analysis*

### 🏦 Bank & Loans
![Merchant Tycoon - Bank Screen](docs/images/bank.png)
*Banking interface for managing loans and financial operations*

## 📖 About The Game

**Merchant Tycoon** is a terminal-based economic simulation game inspired by classic trading games. Your goal is simple: start with $5,000 and become a wealthy merchant tycoon through strategic trading and smart investments.

The game combines:
- **City Trading**: Buy and sell goods across 11 European cities with varying prices
- **Stock Market**: Invest in 12 real company stocks (Tech giants like Google, Apple, NVIDIA, Tesla, and more)
- **Commodities**: Trade in Gold, Oil, Silver, and Copper
- **Cryptocurrency**: Invest in Bitcoin, Ethereum, Solana, and Dogecoin
- **Cargo Upgrades**: Extend inventory capacity; each added slot doubles in price (starts at 50)
- **Banking System**: Deposit cash to earn interest (1-3% APR, compounded daily), manage your savings
- **Loan System**: Take multiple loans to grow faster with variable APR (1-20%, compounded daily)
- **Risk Management**: Balance between inventory (vulnerable to events) and investments (safe)

## 🎯 Game Objective

**Main Strategy: TRAVEL → BUY → SELL → INVEST → SAVE**

1. Travel between cities to find the best prices
2. Buy goods when prices are low
3. Sell goods when prices are high in other cities
4. Invest your profits in the stock market for safe, long-term growth
5. Save excess cash in the bank to earn interest
6. Build a diversified portfolio while continuing to trade

## 🚀 How To Play

### Installation

**Option 1: Install with uv (recommended)**
```bash
# Clone the repository
git clone https://github.com/artdarek/MerchantTycoon.git
cd MerchantTycoon

# Install the game and dependencies
uv pip install -e .

# Run the game
merchant-tycoon
```

**Option 2: Run as Python module**
```bash
# Clone the repository
git clone https://github.com/artdarek/MerchantTycoon.git
cd MerchantTycoon

# Install dependencies
uv pip install textual

# Run the game as a module
python -m merchant_tycoon
```

**Option 3: Using Makefile (developer-friendly)**
```bash
# Clone the repository
git clone https://github.com/artdarek/MerchantTycoon.git
cd MerchantTycoon

# See all available commands
make help

# Create virtual environment
make venv

# Activate the virtual environment
source .venv/bin/activate

# Sync dependencies (creates uv.lock and installs exact versions)
make sync

# Or install in development mode (editable)
make install-dev

# Run the game
make run

# Update dependencies to latest versions
make upgrade

# Clean build artifacts and venv
make clean
```

> **Note**: This project uses [uv](https://github.com/astral-sh/uv) - a fast Python package installer written in Rust. If you don't have uv installed, you can install it with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
>
> **Dependency Management Tips**:
> - `make sync` - Install dependencies from uv.lock (reproducible builds)
> - `make upgrade` - Upgrade all packages to latest compatible versions
> - `make install-dev` - Install in editable mode (for development)

### Controls

The game has **3 tabs** (Goods, Investments, Bank) with context-sensitive controls:

#### Global Controls (Always Available)
| Key | Action | Description |
|-----|--------|-------------|
| **N** | New Game | Start a new game (deletes current save) |
| **A** | Save | Save current game progress |
| **O** | Load | Load saved game |
| **H** | Help | Show in-game instructions |
| **Q** | Quit | Exit the game |
| **C** | Cargo | Extend cargo capacity by +1 slot (cost doubles per slot) |

#### 📦 Goods Tab Controls
| Key | Action | Description |
|-----|--------|-------------|
| **T** | Travel | Move to another city to find better prices |
| **B** | Buy | Purchase goods at current city prices |
| **S** | Sell | Sell goods from your inventory |
| **I** | Transactions | View detailed purchase history with profit/loss |
| **L** | Loan | Borrow money (up to $10,000 per loan) |
| **R** | Repay | Pay back your loans |

#### 💼 Investments Tab Controls
| Key | Action | Description |
|-----|--------|-------------|
| **B** | Buy | Purchase stocks, commodities, or crypto |
| **S** | Sell | Sell assets from your portfolio |
| **I** | Transactions | View detailed investment history with profit/loss |

#### 🏦 Bank Tab Controls
| Key | Action | Description |
|-----|--------|-------------|
| **D** | Deposit | Deposit cash into bank account (earns interest APR 1-3%) |
| **W** | Withdraw | Withdraw cash from bank account |
| **L** | Loan | Take out a new loan (APR 1-20%, max $10,000) |
| **R** | Repay | Repay existing loans |

### Game Mechanics

#### 🏙️ Cities & Pricing
- **11 European Cities**: Warsaw, Berlin, Prague, Vienna, Budapest, Paris, London, Rome, Amsterdam, Barcelona, Stockholm
- Each city has different price multipliers for each good
- Prices fluctuate randomly within a range (±30%)
- Look for arbitrage opportunities between cities
- Travel between cities to exploit price differences

#### 📦 Inventory Management
- **Capacity**: Starts at 50; press C to extend by +1 slot (each added slot doubles in price)
- **FIFO System**: Goods are sold in First In, First Out order
- **Purchase Lots**: Track each purchase separately to calculate profit/loss accurately
- **Random Events**: Can affect your inventory (theft, damage, etc.)

#### 💼 Stock Exchange & Investments
- **Stocks** (12 companies): Google (GOOGL), Meta (META), Apple (AAPL), Microsoft (MSFT), Amazon (AMZN), Netflix (NFLX), NVIDIA (NVDA), Tesla (TSLA), AMD, Oracle (ORCL), Adobe (ADBE), Intel (INTC)
- **Commodities** (4 types): Gold, Oil, Silver, Copper
- **Cryptocurrency** (4 coins): Bitcoin (BTC), Ethereum (ETH), Solana (SOL), Dogecoin (DOGE)
- **Price Trends**: Watch for ▲ (up), ▼ (down), or ─ (stable) indicators
- **Price Volatility**: Stocks ±50%, Commodities ±30-80%, Crypto ±70-90%
- **Safety**: Investments are protected from random events!
- **Long-term**: Build wealth through diversified portfolio

#### 💰 Loans & Debt
- Take **multiple loans** to grow your business faster
- Each loan has its own **variable APR** (1-20% annual rate, randomized each travel)
- Loan APR is converted to daily rate (APR ÷ 365) and compounds daily
- Interest rates change with each travel, but **existing loans keep their original APR**
- Maximum $10,000 per loan
- **Example:** 10% APR loan = 0.027% daily interest, but compounds over time
- Fractional interest accrues until it reaches $1, then adds to loan balance
- Use loans strategically when you have clear profit opportunities (>20-25% margin)

#### 🏦 Banking System
- **Deposit cash** into your bank account to keep it safe
- Earn **interest** on deposits (1-3% APR, randomized each travel)
- Interest is converted to daily rate (APR ÷ 365) and compounds daily
- **Example:** 2% APR = 0.0055% daily interest ≈ $55/day on $1,000,000
- Fractional interest accrues until it reaches $1, then adds to your balance
- **Withdraw** anytime without penalties
- Bank balance is protected from random events
- Lower risk, lower reward compared to goods trading or investments

## 📊 Game Interface

The game uses a **tabbed interface** with three main tabs:

### 📦 Goods Tab
- **Market Prices**: Current prices for all goods in your city with trend indicators
- **Trade Actions**: Buy and Sell buttons
- **Your Inventory**: List of goods you own with quantities, costs, and profit/loss
- Travel between cities to find the best prices

### 💼 Investments Tab
- **Exchange Prices**: Live prices for stocks, commodities, and cryptocurrencies
- **Trade Actions**: Buy and Sell buttons
- **Your Portfolio**: List of assets you own with purchase history and profit/loss

### 🏦 Bank Tab
- **Bank Account**: Your deposit balance and daily interest rate
- **Your Loans**: List of active loans with details (principal, remaining, rate, day taken)
- **Actions**: Deposit, Withdraw, Take Loan, Repay Loan

### Common Elements (All Tabs)
- **Stats Panel** (Top): Cash, Bank Balance, Investments Total, Debt, Day, Location, Cargo
- **Message Log** (Bottom): Game events, transactions, and system messages
- **Global Actions Bar** (Very Top): New Game, Save, Load, Help, Quit

## 💡 Tips & Strategy

### For Beginners
1. Start by learning which cities have good prices for specific goods
2. Travel to a city, buy what's cheap, travel to another, sell what's expensive
3. Keep some cash reserve for opportunities
4. Once you have steady profit, start investing in stocks
5. Use the bank to protect excess cash and earn interest

### Advanced Strategy
1. **Diversify**: Spread wealth across goods, stocks, commodities, crypto, and bank deposits
2. **Arbitrage**: Find goods with big price differences between cities (check all 11 cities!)
3. **Trend Following**: Buy stocks showing ▲ uptrend, avoid ▼ downtrend
4. **Risk Balance**:
   - 40% in safe investments (stocks/commodities)
   - 30% in bank (earning interest, protected)
   - 20% in active trading (goods)
   - 10% in high-risk crypto
5. **Debt Leverage**:
   - Take multiple small loans instead of one big loan
   - Compare loan APR before borrowing (changes with each travel)
   - Only borrow when you have clear profit opportunity (>20-25% margin)
   - Remember: Even 1% APR = 0.0027% daily, which compounds over time
6. **Event Protection**: Move wealth to stocks/commodities/bank before risky situations
7. **Banking Strategy**:
   - Bank interest (1-3% APR) is modest but safe
   - Best for parking large amounts of cash you don't need immediately
   - **Not** a primary wealth-building strategy (too low APR)
   - Use for safety, not growth
8. **Crypto Timing**: High volatility = high risk and high reward, time your trades carefully

## 🛠️ Technical Details

### Built With
- **Python 3.8+**
- **Textual Framework**: Modern TUI (Text User Interface) framework
- **Architecture**: Event-driven with modal screens
- **Data Structures**: FIFO queues for inventory tracking

### Features
- **Tabbed Interface**: 3 main tabs (Goods, Investments, Bank) with context-sensitive controls
- **Real-time price updates**: All prices fluctuate dynamically
- **FIFO Accounting**: First In, First Out inventory and investment tracking
- **Profit/Loss Tracking**: Detailed transaction history with real-time P/L calculations
- **Random Event System**: Unexpected events affect your inventory (25% chance per travel)
- **Price Trend Indicators**: Visual ▲▼─ indicators for all assets
- **Multi-Loan System**: Take multiple loans with individual APR (1-20%), daily compounding
- **Banking System**: Deposit/withdraw with interest accrual (1-3% APR, daily compounding)
- **Realistic Interest Model**: APR converted to daily rates (APR÷365), fractional cents tracked
- **Cryptocurrency Trading**: High-risk, high-reward crypto investments
- **11 European Cities**: Each with unique price multipliers
- **Auto-save/Load**: Persistent game state across sessions
- **Responsive Terminal UI**: Colorful, styled interface using Textual framework

## 🤖 Created Entirely with Claude Code

This game was **100% created using Claude Code** - Anthropic's AI-powered coding assistant. Every line of code, every feature, and every design decision was made through conversation with Claude Code.

### Development Process

The entire development was done through natural language conversations. The development process included:

1. **Initial Concept**: "Let's create a terminal trading game"
2. **Iterative Development**: Feature by feature through conversation
3. **UI Refinements**: Adjusting layouts, adding panels, fixing alignment
4. **Feature Additions**:
   - Started with basic buy/sell mechanics
   - Added city travel system (5 cities → 11 cities)
   - Implemented multi-loan system with variable rates
   - Created stock exchange with 12 real company stocks
   - Added 4 commodities (Gold, Oil, Silver, Copper)
   - Integrated cryptocurrency trading (Bitcoin, Ethereum, Solana, Dogecoin)
   - Built banking system with deposits and interest
   - Added investment tracking with FIFO and profit/loss calculations
   - Created detailed transaction history modals
   - Implemented tabbed interface (Goods, Investments, Bank)
   - Added context-sensitive keyboard controls
   - Built help system and alert modals

5. **Polish & UX**:
   - Changed keybindings to be context-sensitive per tab
   - Fixed data alignment in tables
   - Added dynamic profit/loss coloring (green/red)
   - Refactored UI into modular panels and modals
   - Added proper column formatting and scrolling
   - Improved modal layouts and styling

### No Manual Coding

- **Zero lines** written by hand in a traditional code editor
- All logic, UI, styling, and documentation generated through AI conversation
- Demonstrates the power of conversational programming
- Shows how complex applications can be built through natural language

### What This Demonstrates

This project showcases:
- **Natural Language Programming**: Building software by describing what you want
- **Iterative Development**: Refining features through conversation
- **AI-Human Collaboration**: Combining human creativity with AI implementation
- **Rapid Prototyping**: From concept to working game in a single session

## 📝 License

MIT License - feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual) by Textualize
- Inspired by classic trading games like Dope Wars and Drug Wars
- **Entirely created using [Claude Code](https://www.anthropic.com/) by Anthropic**
- Special thanks to JuniePro for stepping in to support development whenever Claude Code's rate limit hits

## 🎮 Start Playing!

```bash
python3 merchant_tycoon.py
```

Good luck, and may your trades be profitable! 🚀💰

---

*"In code we trust, in Claude we build."* - A demonstration of AI-powered software development
