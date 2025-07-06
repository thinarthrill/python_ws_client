# 🧠 realtime\_deepscalper.py — Realtime Inference Engine for Trading

This script performs real-time inference using a trained DeepScalper model. It connects to a live WebSocket tick data feed (e.g. from NinjaTrader), buffers incoming ticks, makes predictions using a PyTorch model, and sends `BUY` / `SELL` signals back to the platform.

---

## 🔧 Key Features

* Real-time tick data buffering via WebSocket
* Sliding window of last N ticks (default: 60)
* Feature engineering: price, volume, pivots, support/resistance, order flow metrics
* Preprocessing with fitted `StandardScaler`
* Inference with PyTorch model (`DeepScalper`)
* Signal transmission via TCP socket to NinjaTrader

---

## 📁 Required Files

* `deep_scalper_model.pt` — trained PyTorch model
* `scaler.save` — fitted `StandardScaler` (joblib format)
* `model.py` — contains the `DeepScalper` class (must match training setup)

---

## 🧾 Input Tick Format

Each tick must be a JSON object with the following structure:

```json
{
  "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...,
  "pivot": ..., "support": ..., "resistance": ...,
  "support30": ..., "resistance30": ...,
  "isCloseAboveP": ..., "isCloseAboveS": ..., "isCloseAboveR": ...,
  "isHighAboveP": ..., "isLowAboveS": ..., "isOpenAboveR30": ...,
  "bidVolumeSum": ..., "askVolumeSum": ..., "delta": ..., "imbalance": ...,
  "ts": "..."
}
```

---

## 🚀 How to Run

Make sure your NinjaTrader or any platform is sending tick data via WebSocket on port `8765`, and that a TCP listener is ready to receive signals on port `9999`.

```bash
python realtime_deepscalper.py
```

---

## 📦 Dependencies

```bash
pip install torch pandas numpy joblib websocket-client
```

---

## 🧠 Signal Logic

* If model predicts `1` → Send `BUY`
* If model predicts `0` → Send `SELL`

You can modify this to include `HOLD` or confidence thresholds as needed.

---

## 📬 Author

Developed by **Igor Volnukhin**. For research, prototyping, and live signal testing.
