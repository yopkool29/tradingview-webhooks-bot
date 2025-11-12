# NinjaTrader Integration Modes

The TradingView Webhooks Bot supports two modes for NinjaTrader integration:

## 🔧 Mode 1: ATI (Automated Trading Interface)

**File-based communication** - Simple and secure

### Advantages
- ✅ No network configuration needed
- ✅ Built into NinjaTrader (no AddOn required)
- ✅ Very secure (local file system only)
- ✅ Simple setup

### Limitations
- ❌ Cannot retrieve positions
- ❌ Cannot get account info
- ❌ No order confirmations
- ❌ One-way communication only

### Setup
1. Enable ATI in NinjaTrader:
   - Tools > Options > Automated Trading Interface
   - Check "Enable"
   - Click OK

2. Configure `.env`:
   ```bash
   NT_ENABLED=true
   NT_MODE=ATI
   NT_ACCOUNT=Sim101
   NT_CHECK_PROCESS=true
   ```

3. Start the bot:
   ```bash
   python tvwb.py start
   ```

---

## 🌐 Mode 2: AddOn (HTTP API)

**Network-based communication** - Full control and monitoring

### Advantages
- ✅ Can retrieve positions in real-time
- ✅ Can get account information
- ✅ Order confirmations and status
- ✅ Two-way communication
- ✅ Can be accessed remotely (if configured)

### Limitations
- ⚠️ Requires AddOn installation
- ⚠️ Requires NinjaScript compilation
- ⚠️ Network port must be available

### Setup

#### 1. Install the AddOn

Copy the AddOn file:
```
addons/NinjaTraderHttpApi/NinjaTraderHttpApi.cs
→ Documents\NinjaTrader 8\bin\Custom\AddOns\
```

#### 2. Compile in NinjaTrader

1. Open NinjaTrader
2. Go to **Tools > Options > NinjaScript**
3. Click **Compile** (or press F5)
4. Check for compilation success in output window

#### 3. Enable the AddOn

1. Go to **Control Center > Tools > AddOns**
2. Find **NinjaTraderHttpApi**
3. Check the box to enable it
4. The AddOn will start automatically

#### 4. Configure `.env`

```bash
NT_ENABLED=true
NT_MODE=ADDON
NT_ACCOUNT=Sim101
NT_CHECK_PROCESS=false
NT_ADDON_HOST=localhost
NT_ADDON_PORT=8181
```

#### 5. Start the bot

```bash
python tvwb.py start
```

---

## 📊 Feature Comparison

| Feature | ATI Mode | AddOn Mode |
|---------|----------|------------|
| Place orders | ✅ | ✅ |
| TP/SL support | ✅ | ✅ |
| Close positions | ✅ | ✅ |
| Get positions | ❌ | ✅ |
| Get account info | ❌ | ✅ |
| Order confirmations | ❌ | ✅ |
| Real-time status | ❌ | ✅ |
| Setup complexity | Easy | Medium |
| Security | High | Medium |
| Network required | No | Yes |

---

## 🔄 Switching Between Modes

Simply change `NT_MODE` in your `.env` file:

```bash
# Use ATI mode (file-based)
NT_MODE=ATI

# Use AddOn mode (HTTP API)
NT_MODE=ADDON
```

Restart the bot after changing modes.

---

## 🧪 Testing

### Test ATI Mode
```bash
# Set NT_MODE=ATI in .env
python tvwb.py util:test-nt-order-tpsl
```

### Test AddOn Mode
```bash
# Set NT_MODE=ADDON in .env
# Make sure AddOn is running in NinjaTrader
python tvwb.py util:test-nt-order-tpsl
```

---

## 🛠️ Architecture

```
TradingView Webhook
       ↓
Bot (Python)
       ↓
   NtWrapper ← Chooses mode based on NT_MODE
       ↓
   ┌───────────────┐
   │               │
NtATI          NtAddOn
(Files)        (HTTP)
   │               │
   └───────┬───────┘
           ↓
    NinjaTrader 8
```

### Code Structure

```
src/components/actions/
├── nt_place_order.py      # Main action (uses wrapper)
├── nt_flatten.py          # Flatten action (uses wrapper)
├── nt_utils.py            # ATI utilities (registry, process check)
└── nt_wrapper/
    ├── __init__.py
    ├── nt_wrapper.py      # Mode selector
    ├── nt_ati.py          # ATI implementation
    └── nt_addon.py        # AddOn implementation

addons/
└── NinjaTraderHttpApi/
    ├── NinjaTraderHttpApi.cs  # C# AddOn code
    └── README.md              # AddOn documentation
```

---

## 🔒 Security Considerations

### ATI Mode
- ✅ Very secure - no network exposure
- ✅ Only local file system access
- ✅ NinjaTrader validates all commands

### AddOn Mode
- ⚠️ Listens on localhost by default
- ⚠️ **DO NOT** expose to internet without authentication
- ⚠️ Consider using firewall rules
- ⚠️ For production, add API key authentication

---

## 📝 Recommendations

### Use ATI Mode if:
- You only need to send orders
- You want maximum security
- You don't need position monitoring
- You prefer simple setup

### Use AddOn Mode if:
- You need to monitor positions
- You want order confirmations
- You need account information
- You're building advanced strategies

---

## 🐛 Troubleshooting

### ATI Mode Issues
1. Check ATI is enabled in NinjaTrader
2. Verify `incoming` folder exists in NinjaTrader personal root
3. Check NinjaTrader process is running
4. Review NinjaTrader logs (Log tab)

### AddOn Mode Issues
1. Verify AddOn is compiled successfully
2. Check AddOn is enabled in Tools > AddOns
3. Test health endpoint: `http://localhost:8181/health`
4. Check Windows Firewall settings
5. Verify port 8181 is not used by another application
6. Review NinjaTrader logs for AddOn errors

---

## 📚 Additional Resources

- [ATI Documentation](https://ninjatrader.com/support/helpguides/nt8/automated_trading_interface_at.htm)
- [NinjaScript AddOn Development](https://ninjatrader.com/support/helpguides/nt8/addon.htm)
- [AddOn API Reference](addons/NinjaTraderHttpApi/README.md)
