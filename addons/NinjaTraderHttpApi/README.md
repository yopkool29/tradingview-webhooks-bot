# NinjaTrader HTTP API AddOn

This AddOn exposes a REST API to control NinjaTrader from external applications like the TradingView Webhooks Bot.

**✅ No external dependencies required** - Uses only built-in .NET libraries

## Features

- ✅ Place orders (MARKET, LIMIT, STOPMARKET)
- ✅ Automatic TP/SL with OCO orders
- ✅ Close positions
- ✅ Get current positions
- ✅ Get account information
- ✅ Real-time order status

## Installation

1. Copy `NinjaTraderHttpApi.cs` to:
   ```
   Documents\NinjaTrader 8\bin\Custom\AddOns\
   ```

2. Open NinjaTrader

3. Go to **Tools > Options > NinjaScript**

4. Click **Compile** (or press F5)

5. Check the output window for compilation success

6. Go to **Control Center > Tools > AddOns**

7. Enable **NinjaTraderHttpApi**

8. The AddOn will start automatically and listen on `http://localhost:8181`

## Configuration

Edit the AddOn code to change host/port:

```csharp
private string host = "localhost";
private int port = 8181;
```

## API Endpoints

### Health Check
```
GET http://localhost:8181/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2025-11-12T13:00:00"
}
```

### Place Order
```
POST http://localhost:8181/order/place
Content-Type: application/json

{
  "account": "Sim101",
  "symbol": "MNQ 12-25",
  "action": "BUY",
  "quantity": 1,
  "orderType": "MARKET",
  "tp": 25700.0,
  "sl": 25600.0
}
```

Response:
```json
{
  "success": true,
  "orderId": "abc123",
  "oco": "OCO_12345678"
}
```

### Flatten Position
```
POST http://localhost:8181/position/flatten
Content-Type: application/json

{
  "account": "Sim101",
  "symbol": "MNQ 12-25"
}
```

### Get Positions
```
GET http://localhost:8181/positions?account=Sim101
```

Response:
```json
[
  {
    "instrument": "MNQ 12-25",
    "quantity": 1,
    "averagePrice": 25650.0,
    "marketPosition": "Long",
    "unrealizedPnL": 50.0
  }
]
```

### Get Orders
```
GET http://localhost:8181/orders?account=Sim101
```

Response:
```json
[
  {
    "orderId": "abc123",
    "name": "Limit",
    "instrument": "MNQ 12-25",
    "orderAction": "Buy",
    "orderType": "Limit",
    "quantity": 1,
    "limitPrice": 25700.0,
    "stopPrice": 0.0,
    "orderState": "Working",
    "oco": "OCO_12345678",
    "timeInForce": "Day"
  }
]
```

### Get Account Info
```
GET http://localhost:8181/account?account=Sim101
```

Response:
```json
{
  "name": "Sim101",
  "balance": 100000.0,
  "realizedPnL": 250.0,
  "unrealizedPnL": 50.0,
  "positionCount": 1
}
```

## Advantages over ATI

| Feature | ATI (File-based) | AddOn (HTTP API) |
|---------|------------------|------------------|
| Place orders | ✅ | ✅ |
| Close positions | ✅ | ✅ |
| Get positions | ❌ | ✅ |
| Get account info | ❌ | ✅ |
| Order confirmations | ❌ | ✅ |
| Real-time status | ❌ | ✅ |
| Network access | ❌ | ✅ |

## Security

⚠️ **Important**: This AddOn listens on localhost only by default. Do NOT expose it to the internet without proper authentication and encryption.

For production use, consider:
- Adding API key authentication
- Using HTTPS with SSL certificates
- Implementing rate limiting
- Restricting IP addresses

## Troubleshooting

### AddOn not appearing in Tools > AddOns
- Make sure the file is in the correct directory
- Check for compilation errors in NinjaScript Editor
- Restart NinjaTrader

### Connection refused errors
- Verify the AddOn is enabled in Tools > AddOns
- Check Windows Firewall settings
- Verify port 8181 is not used by another application

### Orders not executing
- Check NinjaTrader logs (Log tab in Control Center)
- Verify account name matches exactly
- Ensure instrument symbol format is correct (e.g., "MNQ 12-25")

## Support

For issues specific to this AddOn, check the NinjaTrader logs.
For TradingView Webhooks Bot integration, see the main project documentation.
