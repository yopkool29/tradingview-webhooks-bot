# NinjaTrader Integration Guide

This guide explains how to use the NinjaTrader integration with the TradingView Webhooks Bot.

## Overview

The NinjaTrader integration uses the **ATI (Automated Trading Interface)** to send trading commands from TradingView webhooks to NinjaTrader 8/7. This implementation is based on the [NinjaView](https://github.com/NinjaView/NinjaViewPythonSnip) approach and follows the same pattern as the MT5 integration.

## Prerequisites

1. **NinjaTrader 8 or 7** installed and running on Windows
2. **ATI enabled** in NinjaTrader (Tools > Options > Automated Trading Interface)
3. **Python dependencies**: `psutil`, `python-dotenv`

## Configuration

### 1. Environment Variables

Update your `.env` file with NinjaTrader settings:

```env
# NinjaTrader Configuration
NT_ACCOUNT=Sim101
NT_CHECK_PROCESS=true
```

**Variables:**
- `NT_ACCOUNT`: Default NinjaTrader account name (e.g., "Sim101", "Live")
- `NT_CHECK_PROCESS`: Check if NinjaTrader.exe is running before executing commands

### 2. Enable ATI in NinjaTrader

1. Open NinjaTrader
2. Go to **Tools > Options > Automated Trading Interface**
3. Check **"Enable ATI"**
4. Note the **incoming folder path** (usually in `Documents\NinjaTrader 8\incoming\`)

## Available Actions

### NtPlaceOrder

Places orders in NinjaTrader using market, limit, stop, or stop-limit orders.

**Webhook Payload Example:**
```json
{
  "symbol": "NQ 12-24",
  "order_type": "BUY",
  "quantity": 1,
  "account": "Sim101",
  "order_kind": "MARKET",
  "tif": "DAY"
}
```

**Parameters:**
- `symbol` (required): Instrument name (e.g., "NQ 12-24", "ES 03-25")
- `order_type` (required): "BUY" or "SELL"
- `quantity` (required): Number of contracts (integer)
- `account` (optional): Account name (defaults to `NT_ACCOUNT` from .env)
- `order_kind` (optional): "MARKET", "LIMIT", "STOP", "STOPLIMIT" (default: "MARKET")
- `limit_price` (optional): Limit price for LIMIT/STOPLIMIT orders
- `stop_price` (optional): Stop price for STOP/STOPLIMIT orders
- `tif` (optional): Time in force - "DAY", "GTC", "GTD", "IOC", "FOK" (default: "DAY")
- `oco` (optional): OCO order ID
- `order_id` (optional): Custom order ID
- `strategy` (optional): Strategy name
- `strategy_id` (optional): Strategy ID

**ATI Command Format:**
```
PLACE;<account>;<instrument>;<action>;<qty>;<orderType>;<limitPrice>;<stopPrice>;<tif>;<oco>;<orderId>;<strategy>;<strategyId>
```

### NtFlatten

Closes all positions for a specific instrument or strategy.

**Webhook Payload Example:**
```json
{
  "symbol": "NQ 12-24",
  "account": "Sim101"
}
```

**Parameters:**
- `symbol` (required): Instrument name
- `account` (optional): Account name (defaults to `NT_ACCOUNT`)
- `strategy` (optional): Strategy name (for strategy-specific flatten)
- `strategy_id` (optional): Strategy ID (for strategy-specific flatten)

**ATI Command Format:**
```
CLOSEPOSITION;<account>;<instrument>;<action>;<qty>;<orderType>;<limitPrice>;<stopPrice>;<tif>;<oco>;<orderId>;<strategy>;<strategyId>
```

### NtAccountInfo

Retrieves account information and verifies connection status.

**Webhook Payload Example:**
```json
{
  "account": "Sim101"
}
```

**Note:** ATI doesn't provide direct account balance/equity queries. For real-time account data, you need to implement a custom NinjaScript addon.

## Webhook Events

### WebhookReceivedNtOrder

Triggered when an order webhook is received. Linked to:
- `NtFlatten` (executes first to close existing positions)
- `NtPlaceOrder` (executes after to place new orders)

### WebhookReceivedNtFlatten

Triggered when a flatten webhook is received. Linked to:
- `NtFlatten`

### WebhookReceivedNtInfo

Triggered when an account info webhook is received. Linked to:
- `NtAccountInfo`

## TradingView Alert Setup

### Example 1: Market Order

**Alert Message:**
```json
{
  "event": "WebhookReceivedNtOrder",
  "data": {
    "symbol": "NQ 12-24",
    "order_type": "BUY",
    "quantity": 1,
    "order_kind": "MARKET",
    "tif": "DAY"
  }
}
```

### Example 2: Limit Order

**Alert Message:**
```json
{
  "event": "WebhookReceivedNtOrder",
  "data": {
    "symbol": "ES 03-25",
    "order_type": "SELL",
    "quantity": 2,
    "order_kind": "LIMIT",
    "limit_price": 4500.00,
    "tif": "GTC"
  }
}
```

### Example 3: Stop Order

**Alert Message:**
```json
{
  "event": "WebhookReceivedNtOrder",
  "data": {
    "symbol": "NQ 12-24",
    "order_type": "BUY",
    "quantity": 1,
    "order_kind": "STOP",
    "stop_price": 16000.00,
    "tif": "DAY"
  }
}
```

### Example 4: Flatten All Positions

**Alert Message:**
```json
{
  "event": "WebhookReceivedNtFlatten",
  "data": {
    "symbol": "NQ 12-24"
  }
}
```

### Example 5: Close Then Long (Reverse Position)

**Alert Message:**
```json
{
  "event": "WebhookReceivedNtOrder",
  "data": {
    "symbol": "NQ 12-24",
    "order_type": "BUY",
    "quantity": 1,
    "order_kind": "MARKET"
  }
}
```

This will first flatten existing positions (via `NtFlatten`), then place a new BUY order (via `NtPlaceOrder`).

## How It Works

1. **Webhook Received**: TradingView sends a webhook to your bot
2. **Event Triggered**: The appropriate event (e.g., `WebhookReceivedNtOrder`) is triggered
3. **Actions Executed**: Linked actions are executed in order:
   - `NtFlatten` (if configured) closes existing positions
   - `NtPlaceOrder` places the new order
4. **ATI Command**: The action generates an ATI command string
5. **File Written**: The command is written to NinjaTrader's `incoming` folder with a unique filename
6. **NinjaTrader Executes**: NinjaTrader reads the file and executes the command

## ATI Command Reference

### PLACE Command
```
PLACE;<account>;<instrument>;<action>;<qty>;<orderType>;<limitPrice>;<stopPrice>;<tif>;<oco>;<orderId>;<strategy>;<strategyId>
```

**Example:**
```
PLACE;Sim101;NQ 12-24;BUY;1;MARKET;;;DAY;;;;
```

### CLOSEPOSITION Command
```
CLOSEPOSITION;<account>;<instrument>;<action>;<qty>;<orderType>;<limitPrice>;<stopPrice>;<tif>;<oco>;<orderId>;<strategy>;<strategyId>
```

**Example:**
```
CLOSEPOSITION;Sim101;NQ 12-24;;;;;;;;;
```

## Instrument Naming

NinjaTrader uses specific instrument naming conventions:

- **Futures**: `<Symbol> <Month>-<Year>` (e.g., "NQ 12-24", "ES 03-25")
- **Stocks**: `<Symbol>` (e.g., "AAPL", "MSFT")
- **Forex**: `<Symbol>` (e.g., "EUR/USD", "GBP/USD")

**Month Codes:**
- 01 = January (F)
- 02 = February (G)
- 03 = March (H)
- 04 = April (J)
- 05 = May (K)
- 06 = June (M)
- 07 = July (N)
- 08 = August (Q)
- 09 = September (U)
- 10 = October (V)
- 11 = November (X)
- 12 = December (Z)

## Troubleshooting

### NinjaTrader.exe Not Running

**Error:** `NinjaTrader.exe is not running`

**Solution:**
1. Start NinjaTrader
2. Or set `NT_CHECK_PROCESS=false` in `.env` to skip the check

### Personal Root Not Found

**Error:** `Personal root not found in registry`

**Solution:**
1. Ensure NinjaTrader is installed correctly
2. Check Windows Registry at `HKEY_CURRENT_USER\SOFTWARE\NinjaTrader, LLC\NinjaTrader 8`
3. Verify the `PERSONAL_ROOT` value exists

### ATI Not Enabled

**Error:** Commands not executing in NinjaTrader

**Solution:**
1. Open NinjaTrader
2. Go to **Tools > Options > Automated Trading Interface**
3. Check **"Enable ATI"**
4. Restart NinjaTrader

### Order Not Executing

**Possible Causes:**
1. Invalid instrument name (check exact naming in NinjaTrader)
2. Account name mismatch
3. Insufficient margin/buying power
4. Market closed
5. Invalid order parameters

**Debug Steps:**
1. Check the logs in `src/components/logs/`
2. Verify the ATI command in the log output
3. Check NinjaTrader's Log tab (Tools > Output Window > Log)
4. Verify the file was created in the `incoming` folder

## Comparison with MT5 Integration

| Feature | MT5 | NinjaTrader |
|---------|-----|-------------|
| **Connection** | Direct API (MetaTrader5 library) | File-based ATI |
| **Order Placement** | Direct API calls | Write to incoming folder |
| **Account Info** | Real-time via API | Limited (requires custom NinjaScript) |
| **Position Management** | Full API access | ATI commands |
| **Platform** | Windows/Linux/Mac | Windows only |
| **Dependencies** | MetaTrader5 library | psutil, winreg |

## Advanced Usage

### Custom Strategy Orders

To place orders for a specific strategy:

```json
{
  "event": "WebhookReceivedNtOrder",
  "data": {
    "symbol": "NQ 12-24",
    "order_type": "BUY",
    "quantity": 1,
    "strategy": "MyStrategy",
    "strategy_id": "12345"
  }
}
```

### OCO Orders

To create OCO (One-Cancels-Other) orders:

```json
{
  "event": "WebhookReceivedNtOrder",
  "data": {
    "symbol": "ES 03-25",
    "order_type": "BUY",
    "quantity": 1,
    "order_kind": "LIMIT",
    "limit_price": 4500.00,
    "oco": "OCO123"
  }
}
```

## Additional Resources

- [NinjaTrader ATI Documentation](https://ninjatrader.com/support/helpguides/nt8/automated_trading_interface_at.htm)
- [NinjaView GitHub](https://github.com/NinjaView/NinjaViewPythonSnip)
- [NinjaTrader Support](https://ninjatrader.com/support/)

## Dependencies

Add these to your `requirements.txt`:

```
psutil>=5.9.0
python-dotenv>=1.0.0
```

## License

This integration follows the same license as the main project.
