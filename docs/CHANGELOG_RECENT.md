# Recent Features & Changes

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