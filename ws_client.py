# realtime_deepscalper.py
import websocket
import json
import time
import torch
import numpy as np
import joblib
from collections import deque
from model import DeepScalper  # модель должна совпадать с обучением

# === Параметры ===
WINDOW = 60  # как при обучении
BUFFER_DURATION_SECONDS = 200  # запас по времени буфера

# === Буфер тиков ===
tick_buffer = deque()

# === Загрузка модели и scaler ===
scaler = joblib.load("scaler.save")
model = DeepScalper(input_size=len(scaler.mean_))
model.load_state_dict(torch.load("deep_scalper_model.pt"))
model.eval()

# === Предсказание на основе буфера ===
def predict_from_buffer():
    if len(tick_buffer) < WINDOW:
        return None

    sorted_ticks = sorted(tick_buffer, key=lambda x: x['timestamp_unix'])
    window_data = []

    for tick in sorted_ticks[-WINDOW:]:
        features = [
            tick['open'], tick['high'], tick['low'], tick['close'], tick['volume'],
            tick['pivot'], tick['support'], tick['resistance'], tick['support30'], tick['resistance30'],
            tick['isCloseAboveP'], tick['isCloseAboveS'], tick['isCloseAboveR'],
            tick['isHighAboveP'], tick['isLowAboveS'], tick['isOpenAboveR30'],
            tick['bidVolumeSum'], tick['askVolumeSum'], tick['delta'], tick['imbalance']
        ]

        window_data.append(features)

    import pandas as pd  # в начале файла, если ещё не импортировано

    feature_names = ['open','high','low','close','volume',
        'pivot','support','resistance','support30','resistance30',
        'isCloseAboveP','isCloseAboveS','isCloseAboveR',
        'isHighAboveP','isLowAboveS','isOpenAboveR30',
        'bidVolumeSum','askVolumeSum','delta','imbalance']
    input_df = pd.DataFrame(window_data, columns=feature_names)
    input_np = scaler.transform(input_df)

    input_tensor = torch.tensor(input_np.reshape(1, WINDOW, -1), dtype=torch.float32)
    with torch.no_grad():
        output = model(input_tensor)
        prediction = torch.argmax(output).item()
    return prediction

# === Отправка сигнала в NinjaTrader ===
import socket

def send_signal_to_ninjatrader(signal):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 9999))  # порт должен совпадать с NinjaTrader
            s.sendall(signal.encode('utf-8'))
            #print(f"📤 Сигнал отправлен в NinjaTrader: {signal}")
    except Exception as e:
        print("❌ Ошибка отправки сигнала в NinjaTrader:", e)

# === Обработка тиков из WebSocket ===
def on_message(ws, message):
    global tick_buffer
    try:
        tick = json.loads(message)
        tick['timestamp_unix'] = time.time()
        tick_buffer.append(tick)

        # Чистка буфера
        cutoff = time.time() - BUFFER_DURATION_SECONDS
        while tick_buffer and tick_buffer[0]['timestamp_unix'] < cutoff:
            tick_buffer.popleft()

        #print(f"[{tick['ts']}] Tick received. Buffer size: {len(tick_buffer)}")

        signal = predict_from_buffer()
        if signal == 1:
            send_signal_to_ninjatrader("BUY")
        elif signal == 0:
            send_signal_to_ninjatrader("SELL")

    except Exception as e:
        print("❌ Ошибка обработки тика:", e)

def on_error(ws, error):
    print("❌ WebSocket ошибка:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 WebSocket закрыт.")

def on_open(ws):
    print("✅ Подключено к NinjaTrader WebSocket.")

# === Запуск WebSocket клиента ===
if __name__ == "__main__":
    ws = websocket.WebSocketApp("ws://localhost:8765",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
