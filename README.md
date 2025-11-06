# 🎮 Merchant Tycoon

A terminal-based trading game where you buy low, sell high, travel between cities, and build your fortune through smart trading and investing!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-purple.svg)

## 📖 About The Game

**Merchant Tycoon** is a terminal-based economic simulation game inspired by classic trading games. Your goal is simple: start with $5,000 and become a wealthy merchant tycoon through strategic trading and smart investments.

The game combines:
- **City Trading**: Buy and sell goods in different cities with varying prices
- **Stock Market**: Invest in real company stocks (Google, Meta, Apple, Microsoft)
- **Commodities**: Trade in Gold, Oil, Silver, and Copper
- **Risk Management**: Balance between inventory (vulnerable to events) and investments (safe)
- **Loan System**: Borrow money to grow faster, but watch the 10% daily interest!

## 🎯 Game Objective

**Main Strategy: TRAVEL → BUY → SELL → INVEST INCOME**

1. Travel between cities to find the best prices
2. Buy goods when prices are low
3. Sell goods when prices are high in other cities
4. Invest your profits in the stock market for safe, long-term growth
5. Build a diversified portfolio while continuing to trade

## 🚀 How To Play

### Installation

```bash
# Install dependencies
pip install textual

# Run the game
python3 merchant_tycoon.py
```

### Controls

| Key | Action | Description |
|-----|--------|-------------|
| **T** | Travel | Move to another city to find better prices |
| **B** | Buy | Purchase goods at current city prices |
| **S** | Sell | Sell goods from your inventory |
| **E** | Exchange | Access the stock market to trade stocks & commodities |
| **L** | Loan | Borrow money (10% interest per day) |
| **R** | Repay | Pay back your debt |
| **I** | Inventory | View detailed purchase history with profit/loss |
| **H** | Help | Show in-game instructions |
| **Q** | Quit | Exit the game |

### Game Mechanics

#### 🏙️ Cities & Pricing
- **5 Cities**: Warsaw, Berlin, Prague, Vienna, Budapest
- Each city has different price multipliers for each good
- Prices fluctuate randomly within a range
- Look for arbitrage opportunities between cities

#### 📦 Inventory Management
- **Capacity**: 50 units maximum
- **FIFO System**: Goods are sold in First In, First Out order
- **Purchase Lots**: Track each purchase separately to calculate profit/loss accurately
- **Random Events**: Can affect your inventory (theft, damage, etc.)

#### 💼 Stock Exchange
- **Stocks**: Google (GOOGL), Meta (META), Apple (AAPL), Microsoft (MSFT)
- **Commodities**: Gold, Oil, Silver, Copper
- **Price Trends**: Watch for ▲ (up), ▼ (down), or ─ (stable) indicators
- **Safety**: Investments are protected from random events!
- **Long-term**: Build wealth through diversified portfolio

#### 💰 Loans & Debt
- Borrow money when you need capital
- 10% interest charged every day
- Debt compounds, so repay as soon as profitable
- Use strategically to accelerate growth

## 📊 Game Panels

The interface is divided into several panels:

1. **Stats Panel**: Current cash, debt, day, city, and investment value
2. **Market Prices**: Current prices for goods in your city with trend indicators
3. **Exchange Prices**: Live stock and commodity prices
4. **Your Inventory**: Goods you own with quantities
5. **Your Investments**: Portfolio with profit/loss tracking
6. **Message Log**: Game events and transaction history

## 💡 Tips & Strategy

### For Beginners
1. Start by learning which cities have good prices for specific goods
2. Travel to a city, buy what's cheap, travel to another, sell what's expensive
3. Keep some cash reserve for opportunities
4. Once you have steady profit, start investing in stocks

### Advanced Strategy
1. **Diversify**: Don't put all money in one asset type
2. **Arbitrage**: Find goods with big price differences between cities
3. **Trend Following**: Buy stocks showing ▲ uptrend, avoid ▼ downtrend
4. **Risk Balance**: Keep 60-70% in safe investments, 30-40% in active trading
5. **Debt Leverage**: Use loans only when you have clear profit opportunity
6. **Event Protection**: Move wealth to stocks/commodities before risky situations

## 🛠️ Technical Details

### Built With
- **Python 3.8+**
- **Textual Framework**: Modern TUI (Text User Interface) framework
- **Architecture**: Event-driven with modal screens
- **Data Structures**: FIFO queues for inventory tracking

### Features
- Real-time price updates
- FIFO (First In, First Out) inventory accounting
- Investment lot tracking with profit/loss calculations
- Random event system
- Price trend indicators
- Responsive terminal UI with colors and styling

## 🤖 Created Entirely with Claude Code

This game was **100% created using Claude Code** - Anthropic's AI-powered coding assistant. Every line of code, every feature, and every design decision was made through conversation with Claude Code.

### Development Process

The entire development was done through natural language conversations. The development process included:

1. **Initial Concept**: "Let's create a terminal trading game"
2. **Iterative Development**: Feature by feature through conversation
3. **UI Refinements**: Adjusting layouts, adding panels, fixing alignment
4. **Feature Additions**:
   - Started with basic buy/sell mechanics
   - Added city travel system
   - Implemented loan system
   - Created stock exchange with real company names
   - Added investment tracking with profit/loss
   - Built inventory details with FIFO tracking
   - Created help system

5. **Polish & UX**:
   - Changed keybindings for better UX
   - Fixed data alignment in tables
   - Removed unnecessary UI elements
   - Added proper column formatting

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

## 🎮 Start Playing!

```bash
python3 merchant_tycoon.py
```

Good luck, and may your trades be profitable! 🚀💰

---

*"In code we trust, in Claude we build."* - A demonstration of AI-powered software development
