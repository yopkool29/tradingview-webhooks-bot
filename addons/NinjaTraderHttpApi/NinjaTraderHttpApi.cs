// NinjaTrader HTTP API AddOn
// Place this file in: Documents\NinjaTrader 8\bin\Custom\AddOns\

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript;

namespace NinjaTrader.NinjaScript.AddOns
{
    public class NinjaTraderHttpApi : AddOnBase
    {
        private HttpListener listener;
        private Thread listenerThread;
        private bool isRunning = false;
        private string host = "localhost";
        private int port = 8181;
        private JavaScriptSerializer serializer = new JavaScriptSerializer();

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "HTTP API for NinjaTrader control";
                Name = "NinjaTraderHttpApi";
            }
            else if (State == State.Active)
            {
                StartServer();
                Print("NinjaTrader HTTP API started on http://" + host + ":" + port);
            }
            else if (State == State.Terminated)
            {
                StopServer();
                Print("NinjaTrader HTTP API stopped");
            }
        }

        private void StartServer()
        {
            try
            {
                listener = new HttpListener();
                listener.Prefixes.Add($"http://{host}:{port}/");
                listener.Start();
                isRunning = true;

                listenerThread = new Thread(HandleRequests);
                listenerThread.IsBackground = true;
                listenerThread.Start();
            }
            catch (Exception ex)
            {
                Print("Error starting HTTP server: " + ex.Message);
            }
        }

        private void StopServer()
        {
            isRunning = false;
            if (listener != null && listener.IsListening)
            {
                listener.Stop();
                listener.Close();
            }
        }

        private void HandleRequests()
        {
            while (isRunning)
            {
                try
                {
                    HttpListenerContext context = listener.GetContext();
                    Task.Run(() => ProcessRequest(context));
                }
                catch (Exception ex)
                {
                    if (isRunning)
                    {
                        Print("Error handling request: " + ex.Message);
                    }
                }
            }
        }

        private void ProcessRequest(HttpListenerContext context)
        {
            HttpListenerRequest request = context.Request;
            HttpListenerResponse response = context.Response;

            try
            {
                string responseString = "";
                int statusCode = 200;

                // Enable CORS
                response.AddHeader("Access-Control-Allow-Origin", "*");
                response.AddHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
                response.AddHeader("Access-Control-Allow-Headers", "Content-Type");

                if (request.HttpMethod == "OPTIONS")
                {
                    response.StatusCode = 200;
                    response.Close();
                    return;
                }

                string path = request.Url.AbsolutePath;

                // Route requests
                if (path == "/health" && request.HttpMethod == "GET")
                {
                    responseString = serializer.Serialize(new { status = "ok", timestamp = DateTime.Now });
                }
                else if (path == "/order/place" && request.HttpMethod == "POST")
                {
                    string body = ReadRequestBody(request);
                    responseString = PlaceOrder(body);
                }
                else if (path == "/position/flatten" && request.HttpMethod == "POST")
                {
                    string body = ReadRequestBody(request);
                    responseString = Flatten(body);
                }
                else if (path == "/positions" && request.HttpMethod == "GET")
                {
                    string accountName = request.QueryString["account"] ?? "Sim101";
                    responseString = GetPositions(accountName);
                }
                else if (path == "/orders" && request.HttpMethod == "GET")
                {
                    string accountName = request.QueryString["account"] ?? "Sim101";
                    responseString = GetOrders(accountName);
                }
                else if (path == "/account" && request.HttpMethod == "GET")
                {
                    string accountName = request.QueryString["account"] ?? "Sim101";
                    responseString = GetAccountInfo(accountName);
                }
                else
                {
                    statusCode = 404;
                    responseString = serializer.Serialize(new { error = "Not found" });
                }

                // Send response
                byte[] buffer = Encoding.UTF8.GetBytes(responseString);
                response.ContentType = "application/json";
                response.ContentLength64 = buffer.Length;
                response.StatusCode = statusCode;
                response.OutputStream.Write(buffer, 0, buffer.Length);
                response.OutputStream.Close();
            }
            catch (Exception ex)
            {
                Print("Error processing request: " + ex.Message);
                response.StatusCode = 500;
                byte[] buffer = Encoding.UTF8.GetBytes(serializer.Serialize(new { error = ex.Message }));
                response.OutputStream.Write(buffer, 0, buffer.Length);
                response.OutputStream.Close();
            }
        }

        private string ReadRequestBody(HttpListenerRequest request)
        {
            using (StreamReader reader = new StreamReader(request.InputStream, request.ContentEncoding))
            {
                return reader.ReadToEnd();
            }
        }

        private string PlaceOrder(string jsonBody)
        {
            try
            {
                var data = serializer.Deserialize<Dictionary<string, object>>(jsonBody);
                
                string accountName = data.ContainsKey("account") ? data["account"].ToString() : "Sim101";
                string symbol = data["symbol"].ToString();
                string action = data["action"].ToString();
                int quantity = data.ContainsKey("quantity") ? Convert.ToInt32(data["quantity"]) : 1;
                string orderType = data.ContainsKey("orderType") ? data["orderType"].ToString() : "MARKET";
                double? limitPrice = data.ContainsKey("limitPrice") ? Convert.ToDouble(data["limitPrice"]) : (double?)null;
                double? stopPrice = data.ContainsKey("stopPrice") ? Convert.ToDouble(data["stopPrice"]) : (double?)null;
                double? tp = data.ContainsKey("tp") ? Convert.ToDouble(data["tp"]) : (double?)null;
                double? sl = data.ContainsKey("sl") ? Convert.ToDouble(data["sl"]) : (double?)null;

                // Get account
                Account account = Account.All.FirstOrDefault(a => a.Name == accountName);
                if (account == null)
                    return serializer.Serialize(new { success = false, error = "Account not found" });

                // Get instrument
                Instrument instrument = Instrument.GetInstrument(symbol);
                if (instrument == null)
                    return serializer.Serialize(new { success = false, error = "Instrument not found" });

                // Determine order action
                OrderAction orderAction = action.ToUpper() == "BUY" ? OrderAction.Buy : OrderAction.Sell;

                // Place main order
                Order mainOrder = null;
                string ocoId = (tp != null || sl != null) ? "OCO_" + Guid.NewGuid().ToString("N").Substring(0, 8) : "";
                bool useOcoOnEntry = false;
                
                // Only use OCO on entry order if it's not MARKET
                if (!string.IsNullOrEmpty(ocoId) && orderType.ToUpper() != "MARKET")
                {
                    useOcoOnEntry = true;
                    Print("Using OCO on entry order (order type: " + orderType + ")");
                }
                else if (!string.IsNullOrEmpty(ocoId))
                {
                    Print("MARKET order - TP/SL will be placed as separate OCO pair after fill");
                }

                if (orderType.ToUpper() == "MARKET")
                {
                    // Don't use OCO on MARKET entry orders
                    mainOrder = account.CreateOrder(instrument, orderAction, OrderType.Market, OrderEntry.Manual, 
                        TimeInForce.Day, quantity, 0, 0, "", "", Core.Globals.MaxDate, null);
                }
                else if (orderType.ToUpper() == "LIMIT")
                {
                    mainOrder = account.CreateOrder(instrument, orderAction, OrderType.Limit, OrderEntry.Manual,
                        TimeInForce.Day, quantity, limitPrice ?? 0, 0, useOcoOnEntry ? ocoId : "", "", Core.Globals.MaxDate, null);
                }
                else if (orderType.ToUpper() == "STOPMARKET")
                {
                    mainOrder = account.CreateOrder(instrument, orderAction, OrderType.StopMarket, OrderEntry.Manual,
                        TimeInForce.Day, quantity, 0, stopPrice ?? 0, useOcoOnEntry ? ocoId : "", "", Core.Globals.MaxDate, null);
                }

                if (mainOrder != null)
                {
                    account.Submit(new Order[] { mainOrder });

                    // Place TP/SL orders if specified
                    if (tp != null || sl != null)
                    {
                        OrderAction exitAction = orderAction == OrderAction.Buy ? OrderAction.Sell : OrderAction.Buy;

                        if (tp != null)
                        {
                            Order tpOrder = account.CreateOrder(instrument, exitAction, OrderType.Limit, OrderEntry.Manual,
                                TimeInForce.Day, quantity, tp.Value, 0, ocoId, "", Core.Globals.MaxDate, null);
                            account.Submit(new Order[] { tpOrder });
                        }

                        if (sl != null)
                        {
                            Order slOrder = account.CreateOrder(instrument, exitAction, OrderType.StopMarket, OrderEntry.Manual,
                                TimeInForce.Day, quantity, 0, sl.Value, ocoId, "", Core.Globals.MaxDate, null);
                            account.Submit(new Order[] { slOrder });
                        }
                    }

                    return serializer.Serialize(new { success = true, orderId = mainOrder.OrderId, oco = ocoId });
                }

                return serializer.Serialize(new { success = false, error = "Failed to create order" });
            }
            catch (Exception ex)
            {
                return serializer.Serialize(new { success = false, error = ex.Message });
            }
        }

        private string Flatten(string jsonBody)
        {
            try
            {
                var data = serializer.Deserialize<Dictionary<string, object>>(jsonBody);
                
                string accountName = data.ContainsKey("account") ? data["account"].ToString() : "Sim101";
                string symbol = data["symbol"].ToString();

                Account account = Account.All.FirstOrDefault(a => a.Name == accountName);
                if (account == null)
                    return serializer.Serialize(new { success = false, error = "Account not found" });

                Instrument instrument = Instrument.GetInstrument(symbol);
                if (instrument == null)
                    return serializer.Serialize(new { success = false, error = "Instrument not found" });

                Position position = account.Positions.FirstOrDefault(p => p.Instrument == instrument);
                if (position == null || position.Quantity == 0)
                    return serializer.Serialize(new { success = true, message = "No position to close" });

                // Cancel all working orders for this instrument (TP/SL orders)
                var workingOrders = account.Orders.Where(o => 
                    o.Instrument == instrument && 
                    (o.OrderState == OrderState.Working || o.OrderState == OrderState.Accepted)).ToList();
                
                foreach (var order in workingOrders)
                {
                    account.Cancel(new Order[] { order });
                    Print("Cancelled order: " + order.Name + " (" + order.OrderType + ")");
                }

                // Close position
                OrderAction closeAction = position.MarketPosition == MarketPosition.Long ? OrderAction.Sell : OrderAction.Buy;
                Order closeOrder = account.CreateOrder(instrument, closeAction, OrderType.Market, OrderEntry.Manual,
                    TimeInForce.Day, Math.Abs(position.Quantity), 0, 0, "", "", Core.Globals.MaxDate, null);
                
                account.Submit(new Order[] { closeOrder });

                return serializer.Serialize(new { 
                    success = true, 
                    orderId = closeOrder.OrderId, 
                    quantity = Math.Abs(position.Quantity),
                    cancelledOrders = workingOrders.Count
                });
            }
            catch (Exception ex)
            {
                return serializer.Serialize(new { success = false, error = ex.Message });
            }
        }

        private string GetPositions(string accountName)
        {
            try
            {
                Account account = Account.All.FirstOrDefault(a => a.Name == accountName);
                if (account == null)
                    return serializer.Serialize(new { error = "Account not found" });

                var positions = account.Positions.Where(p => p.Quantity != 0)
                    .Select(p => new
                    {
                        instrument = p.Instrument.FullName,
                        quantity = p.Quantity,
                        averagePrice = p.AveragePrice,
                        marketPosition = p.MarketPosition.ToString(),
                        unrealizedPnL = p.GetUnrealizedProfitLoss(PerformanceUnit.Currency)
                    })
                    .ToList();

                return serializer.Serialize(positions);
            }
            catch (Exception ex)
            {
                return serializer.Serialize(new { error = ex.Message });
            }
        }

        private string GetOrders(string accountName)
        {
            try
            {
                Account account = Account.All.FirstOrDefault(a => a.Name == accountName);
                if (account == null)
                    return serializer.Serialize(new { error = "Account not found" });

                var orders = account.Orders.Where(o => 
                    o.OrderState == OrderState.Working || 
                    o.OrderState == OrderState.Accepted)
                    .Select(o => new
                    {
                        orderId = o.OrderId,
                        name = o.Name,
                        instrument = o.Instrument.FullName,
                        orderAction = o.OrderAction.ToString(),
                        orderType = o.OrderType.ToString(),
                        quantity = o.Quantity,
                        limitPrice = o.LimitPrice,
                        stopPrice = o.StopPrice,
                        orderState = o.OrderState.ToString(),
                        oco = o.Oco,
                        timeInForce = o.TimeInForce.ToString()
                    })
                    .ToList();

                return serializer.Serialize(orders);
            }
            catch (Exception ex)
            {
                return serializer.Serialize(new { error = ex.Message });
            }
        }

        private string GetAccountInfo(string accountName)
        {
            try
            {
                Account account = Account.All.FirstOrDefault(a => a.Name == accountName);
                if (account == null)
                    return serializer.Serialize(new { error = "Account not found" });

                double unrealizedPnL = account.Positions.Sum(p => p.GetUnrealizedProfitLoss(PerformanceUnit.Currency));
                int positionCount = account.Positions.Count(p => p.Quantity != 0);

                return serializer.Serialize(new
                {
                    name = account.Name,
                    balance = account.Get(AccountItem.CashValue, Currency.UsDollar),
                    realizedPnL = account.Get(AccountItem.RealizedProfitLoss, Currency.UsDollar),
                    unrealizedPnL = unrealizedPnL,
                    positionCount = positionCount
                });
            }
            catch (Exception ex)
            {
                return serializer.Serialize(new { error = ex.Message });
            }
        }
    }
}
