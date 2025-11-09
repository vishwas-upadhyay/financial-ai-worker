# Multi-Account Support Implementation Guide

## Overview
This document outlines the complete implementation plan for adding multi-account support to the Financial AI Worker application, allowing you to track portfolios for multiple family members across both Zerodha and Trading212 brokers.

## Current Status

### ✅ Phase 1: Token Manager (COMPLETED)
**File Modified:** `src/services/token_manager.py`

#### Changes Made:
1. **Save Methods** - Now accept `account_name` parameter:
   ```python
   save_zerodha_token(..., account_name="primary")
   save_trading212_token(..., account_name="primary")
   ```

2. **Get Methods** - Now accept `account_name` parameter:
   ```python
   get_zerodha_token(account_name="primary")
   get_trading212_token(account_name="primary")
   ```

3. **New Helper Methods**:
   - `list_zerodha_accounts()` - Returns list of account names
   - `list_trading212_accounts()` - Returns list of account names
   - `delete_zerodha_token(account_name)` - Delete specific account
   - `delete_trading212_token(account_name)` - Delete specific account

4. **Backward Compatibility**:
   - Automatically migrates old single-account format to new format
   - Old data becomes "primary" account
   - No data loss during migration

#### New Token Structure:
```json
{
  "zerodha": {
    "primary": {
      "api_key": "your_key",
      "api_secret": "your_secret",
      "access_token": "token",
      "expires_at": "2025-11-08T23:59:59",
      "updated_at": "2025-11-08T10:00:00"
    },
    "spouse": {
      "api_key": "spouse_key",
      "api_secret": "spouse_secret",
      "access_token": "spouse_token",
      "expires_at": "2025-11-08T23:59:59",
      "updated_at": "2025-11-08T10:00:00"
    },
    "parent": {
      "api_key": "parent_key",
      "api_secret": "parent_secret",
      "access_token": "parent_token",
      "expires_at": "2025-11-08T23:59:59",
      "updated_at": "2025-11-08T10:00:00"
    }
  },
  "trading212": {
    "primary": {
      "api_key": "your_t212_key",
      "updated_at": "2025-11-08T10:00:00"
    },
    "child1": {
      "api_key": "child1_t212_key",
      "updated_at": "2025-11-08T10:00:00"
    }
  }
}
```

---

## ⏳ Phase 2: Broker Clients (PENDING)

### Files to Modify:
- `src/brokers/zerodha_client.py`
- `src/brokers/trading212_client.py`

### Required Changes:

#### 2.1 Zerodha Client Updates
**File:** `src/brokers/zerodha_client.py`

**Constructor Modification:**
```python
class ZerodhaClient:
    def __init__(self, account_name: str = "primary"):
        self.account_name = account_name
        # Get tokens for specific account
        tokens = token_manager.get_zerodha_token(account_name)
        if not tokens:
            raise ValueError(f"No Zerodha credentials for account: {account_name}")

        self.api_key = tokens['api_key']
        self.api_secret = tokens['api_secret']
        self.access_token = tokens['access_token']
```

**Usage Example:**
```python
# Primary account
async with ZerodhaClient(account_name="primary") as client:
    portfolio = await client.get_portfolio()

# Spouse account
async with ZerodhaClient(account_name="spouse") as client:
    portfolio = await client.get_portfolio()
```

#### 2.2 Trading212 Client Updates
**File:** `src/brokers/trading212_client.py`

**Similar constructor changes:**
```python
class Trading212Client:
    def __init__(self, account_name: str = "primary"):
        self.account_name = account_name
        tokens = token_manager.get_trading212_token(account_name)
        if not tokens:
            raise ValueError(f"No Trading212 credentials for account: {account_name}")

        self.api_key = tokens['api_key']
```

---

## ⏳ Phase 3: API Endpoints (PENDING)

### Files to Modify:
- `src/api/main.py`

### Required Changes:

#### 3.1 Add Account Query Parameter
All portfolio endpoints need to accept optional `account` parameter:

**Current:**
```python
@app.get("/portfolio/zerodha")
async def get_zerodha_portfolio(currency: Optional[str] = None):
    async with ZerodhaClient() as client:
        # ...
```

**Updated:**
```python
@app.get("/portfolio/zerodha")
async def get_zerodha_portfolio(
    currency: Optional[str] = None,
    account: Optional[str] = "primary"
):
    async with ZerodhaClient(account_name=account) as client:
        # ...
```

#### 3.2 New Endpoints to Add

**List All Accounts:**
```python
@app.get("/accounts/list")
async def list_all_accounts():
    """List all configured accounts"""
    return {
        "zerodha": token_manager.list_zerodha_accounts(),
        "trading212": token_manager.list_trading212_accounts()
    }
```

**Combined Family Portfolio:**
```python
@app.get("/portfolio/family-combined")
async def get_family_combined_portfolio(currency: Optional[str] = "INR"):
    """
    Get combined portfolio for all family members
    Aggregates all Zerodha and Trading212 accounts
    """
    all_portfolios = []

    # Get all Zerodha accounts
    for account_name in token_manager.list_zerodha_accounts():
        try:
            portfolio = await get_zerodha_portfolio(currency=currency, account=account_name)
            portfolio['account_name'] = account_name
            portfolio['account_owner'] = account_name.title()
            all_portfolios.append(portfolio)
        except Exception as e:
            logger.warning(f"Failed to fetch Zerodha {account_name}: {e}")

    # Get all Trading212 accounts
    for account_name in token_manager.list_trading212_accounts():
        try:
            portfolio = await get_trading212_portfolio(currency=currency, account=account_name)
            portfolio['account_name'] = account_name
            portfolio['account_owner'] = account_name.title()
            all_portfolios.append(portfolio)
        except Exception as e:
            logger.warning(f"Failed to fetch Trading212 {account_name}: {e}")

    # Aggregate totals
    total_value = sum(p['total_value'] for p in all_portfolios)
    total_investment = sum(p['total_investment'] for p in all_portfolios)
    total_pnl = sum(p['total_pnl'] for p in all_portfolios)

    return {
        "broker": "family-combined",
        "total_value": total_value,
        "total_investment": total_investment,
        "total_pnl": total_pnl,
        "total_pnl_percentage": (total_pnl / total_investment * 100) if total_investment > 0 else 0,
        "accounts": all_portfolios,
        "account_count": len(all_portfolios)
    }
```

---

## ⏳ Phase 4: Portfolio Cache (PENDING)

### File to Modify:
- `src/services/portfolio_cache.py`

### Required Changes:

Update cache key generation to include account name:

**Current:**
```python
def _get_cache_path(self, broker: str, currency: str = "INR") -> Path:
    filename = f"portfolio_{broker}_{currency.lower()}.json"
    return self.cache_dir / filename
```

**Updated:**
```python
def _get_cache_path(self, broker: str, currency: str = "INR", account: str = "primary") -> Path:
    filename = f"portfolio_{broker}_{account}_{currency.lower()}.json"
    return self.cache_dir / filename

def save(self, broker: str, data: Dict[str, Any], currency: str = "INR", account: str = "primary"):
    # Update to use new cache path with account

def load(self, broker: str, currency: str = "INR", account: str = "primary"):
    # Update to use new cache path with account
```

**Cache File Examples:**
- `portfolio_zerodha_primary_inr.json`
- `portfolio_zerodha_spouse_inr.json`
- `portfolio_trading212_child1_eur.json`

---

## ⏳ Phase 5: Dashboard UI (PENDING)

### File to Modify:
- `src/web/dashboard.html`

### Required Changes:

#### 5.1 Add Account Selector
Add a new dropdown in the controls section:

```html
<div class="controls">
    <!-- Existing broker selector -->
    <select id="brokerSelect" class="select">
        <option value="combined">🌐 Combined Portfolio</option>
        <option value="family-combined">👨‍👩‍👧‍👦 Family Combined</option>
        <option value="zerodha">🇮🇳 Zerodha</option>
        <option value="trading212">🌍 Trading 212</option>
    </select>

    <!-- NEW: Account selector (shown only for single broker selection) -->
    <select id="accountSelect" class="select" style="display: none;">
        <option value="primary">Primary Account</option>
        <!-- Dynamically populated based on selected broker -->
    </select>

    <!-- Existing currency selector -->
    <select id="currencySelect" class="select">
        <option value="INR">₹ INR (Indian Rupee)</option>
        <option value="EUR">€ EUR (Euro)</option>
    </select>

    <!-- Existing buttons -->
    <button id="refreshBtn" class="btn">🔄 Refresh Data</button>
</div>
```

#### 5.2 JavaScript Updates

**Add account management:**
```javascript
class FinancialDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.currentBroker = 'combined';
        this.currentCurrency = 'INR';
        this.currentAccount = 'primary';  // NEW
        this.availableAccounts = {};       // NEW
        this.initializeEventListeners();
        this.loadAccounts();              // NEW
        this.loadInitialData();
    }

    async loadAccounts() {
        try {
            const response = await axios.get(`${this.apiBase}/accounts/list`);
            this.availableAccounts = response.data;
            this.updateAccountSelector();
        } catch (error) {
            console.error('Failed to load accounts:', error);
        }
    }

    updateAccountSelector() {
        const accountSelect = document.getElementById('accountSelect');
        const broker = this.currentBroker;

        // Hide for combined views
        if (broker === 'combined' || broker === 'family-combined') {
            accountSelect.style.display = 'none';
            return;
        }

        // Show and populate for single broker
        accountSelect.style.display = 'block';
        accountSelect.innerHTML = '';

        const accounts = this.availableAccounts[broker] || ['primary'];
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account;
            option.textContent = account.charAt(0).toUpperCase() + account.slice(1);
            accountSelect.appendChild(option);
        });
    }

    async fetchPortfolio() {
        let url = `${this.apiBase}/portfolio/${this.currentBroker}`;
        const params = new URLSearchParams();
        params.append('currency', this.currentCurrency);

        // Add account parameter for single broker views
        if (this.currentBroker !== 'combined' && this.currentBroker !== 'family-combined') {
            params.append('account', this.currentAccount);
        }

        const response = await axios.get(`${url}?${params.toString()}`);
        return response.data;
    }
}
```

#### 5.3 Family Combined View
Add special handling for family-combined view to show breakdown by account owner:

```javascript
updateMetricsForFamilyView(portfolioData) {
    const currencySymbol = this.currentCurrency === 'INR' ? '₹' : '€';
    let metricsHTML = `
        <div class="metric-card">
            <div class="metric-value">${currencySymbol}${portfolioData.total_value.toLocaleString()}</div>
            <div class="metric-label">👨‍👩‍👧‍👦 Total Family Wealth</div>
        </div>
        <div class="metric-card">
            <div class="metric-value ${portfolioData.total_pnl >= 0 ? 'positive' : 'negative'}">
                ${portfolioData.total_pnl >= 0 ? '+' : ''}${currencySymbol}${Math.abs(portfolioData.total_pnl).toLocaleString()}
            </div>
            <div class="metric-label">Family P&L</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">👥 ${portfolioData.account_count}</div>
            <div class="metric-label">Family Members</div>
        </div>
    `;

    // Add breakdown by member
    portfolioData.accounts.forEach(account => {
        metricsHTML += `
        <div class="metric-card">
            <div class="metric-label">${account.account_owner}</div>
            <div class="metric-value">${currencySymbol}${account.total_value.toLocaleString()}</div>
            <div style="font-size: 0.9em; color: ${account.total_pnl >= 0 ? '#27ae60' : '#e74c3c'}">
                ${account.total_pnl >= 0 ? '+' : ''}${currencySymbol}${Math.abs(account.total_pnl).toLocaleString()}
            </div>
        </div>`;
    });

    document.getElementById('metricsGrid').innerHTML = metricsHTML;
}
```

---

## ⏳ Phase 6: Settings Page (PENDING)

### File to Modify:
- `src/web/settings.html`

### Required Changes:

#### 6.1 Add Account Management Section

```html
<div class="card">
    <h3>🏠 Family Account Management</h3>

    <div class="account-section">
        <h4>Zerodha Accounts</h4>
        <div id="zerodhaAccountsList"></div>
        <button onclick="addZerodhaAccount()" class="btn">➕ Add Zerodha Account</button>
    </div>

    <div class="account-section">
        <h4>Trading212 Accounts</h4>
        <div id="trading212AccountsList"></div>
        <button onclick="addTrading212Account()" class="btn">➕ Add Trading212 Account</button>
    </div>
</div>
```

#### 6.2 Account Management Functions

```javascript
async function loadAccounts() {
    const response = await axios.get('http://localhost:8000/accounts/list');
    const accounts = response.data;

    // Display Zerodha accounts
    const zerodhaList = document.getElementById('zerodhaAccountsList');
    zerodhaList.innerHTML = '';
    accounts.zerodha.forEach(account => {
        zerodhaList.innerHTML += `
            <div class="account-item">
                <span>${account}</span>
                <button onclick="removeAccount('zerodha', '${account}')">Remove</button>
            </div>
        `;
    });

    // Display Trading212 accounts
    const t212List = document.getElementById('trading212AccountsList');
    t212List.innerHTML = '';
    accounts.trading212.forEach(account => {
        t212List.innerHTML += `
            <div class="account-item">
                <span>${account}</span>
                <button onclick="removeAccount('trading212', '${account}')">Remove</button>
            </div>
        `;
    });
}

function addZerodhaAccount() {
    const accountName = prompt('Enter account name (e.g., spouse, parent, child1):');
    if (!accountName) return;

    // Show Zerodha login form with account_name parameter
    // ... existing Zerodha login flow with account_name parameter
}

async function removeAccount(broker, accountName) {
    if (!confirm(`Remove ${accountName} account from ${broker}?`)) return;

    try {
        await axios.delete(`http://localhost:8000/auth/${broker}/logout`, {
            params: { account: accountName }
        });
        await loadAccounts();
        alert('Account removed successfully');
    } catch (error) {
        alert('Failed to remove account: ' + error.message);
    }
}
```

---

## 🎯 Implementation Phases Summary

### Phase 1: Foundation ✅ DONE
- Token manager updated
- Multi-account data structure implemented
- Backward compatibility ensured

### Phase 2: Backend Integration (Estimated: 2-3 hours)
- Update broker clients
- Update API endpoints
- Update caching system
- Add new combined endpoints

### Phase 3: Frontend Updates (Estimated: 2-3 hours)
- Dashboard account selector
- Family combined view
- Settings page account management
- Account-specific authentication flows

### Phase 4: Testing & Polish (Estimated: 1-2 hours)
- Test all account combinations
- Verify cache works per account
- Test authentication flows
- Ensure backward compatibility

**Total Estimated Time: 5-8 hours of development**

---

## 📝 Usage Examples (After Implementation)

### Adding Family Member Accounts

1. **Go to Settings Page** (http://localhost:8000/settings)
2. **Add Zerodha Account:**
   - Click "Add Zerodha Account"
   - Enter account name: "spouse"
   - Complete Zerodha login flow
   - Tokens saved as `zerodha.spouse`

3. **Add Trading212 Account:**
   - Click "Add Trading212 Account"
   - Enter account name: "child1"
   - Enter Trading212 API key
   - Tokens saved as `trading212.child1`

### Viewing Portfolios

**Individual Account:**
- Select "Zerodha" → Select "Spouse" → View spouse's portfolio

**Family Combined:**
- Select "Family Combined" → View all accounts aggregated

**Example URLs:**
- `http://localhost:8000/portfolio/zerodha?account=primary&currency=INR`
- `http://localhost:8000/portfolio/zerodha?account=spouse&currency=INR`
- `http://localhost:8000/portfolio/trading212?account=child1&currency=EUR`
- `http://localhost:8000/portfolio/family-combined?currency=INR`

---

## 🚨 Important Considerations

### Security
- Each account has separate encrypted credentials
- Tokens remain encrypted in `data/tokens/broker_tokens.enc`
- No credentials shared between accounts

### Performance
- Cache files created per account (no conflicts)
- API calls made independently per account
- Family combined view may be slower (multiple API calls)

### Data Privacy
- Each family member's portfolio data is separate
- No data mixing between accounts
- Individual account deletion doesn't affect others

### Migration
- Existing single-account data automatically becomes "primary"
- No manual migration needed
- All existing functionality preserved

---

## ✅ Next Steps

**Option A: Full Implementation**
Proceed with implementing all phases (5-8 hours total)

**Option B: Phased Approach**
1. Implement Phase 2 (Backend) first
2. Test with API calls (Postman/curl)
3. Then implement Phase 3 (Frontend)

**Option C: Minimal MVP**
- Just update broker clients and API endpoints
- Skip UI changes initially
- Use API directly with `?account=` parameter

**Recommended:** Option B - This allows thorough testing before UI changes.

---

## 📞 Questions to Resolve

1. **Account Naming Convention:**
   - Suggested: primary, spouse, parent1, parent2, child1, child2
   - Or allow free-form names?

2. **Account Display Names:**
   - Use account identifier (spouse) or allow custom display names?

3. **Default Behavior:**
   - Should "Combined" show family-combined or just your accounts?
   - Should primary account be the default always?

4. **Authorization:**
   - Should there be any access control between accounts?
   - Or full access to all family accounts?

---

Ready to proceed? Let me know which option you prefer!
