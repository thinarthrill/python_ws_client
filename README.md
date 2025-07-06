# python_ws_client
It connects to a WebSocket feed (e.g., from NinjaTrader), buffers live tick data, processes the latest N ticks using a StandardScaler, runs predictions with a PyTorch model (DeepScalper), and sends trading signals (BUY or SELL) back to the trading platform via TCP socket.
