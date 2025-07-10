# api/advanced_webhook.py
from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import sqlite3
import threading
from collections import deque
import statistics

app = Flask(__name__)

# 記憶體中儲存最近的資料 (生產環境建議使用 Redis)
recent_trades = deque(maxlen=1000)
price_history = deque(maxlen=100)

def init_db():
    """
    初始化資料庫
    """
    conn = sqlite3.connect('/tmp/trades.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            volume INTEGER,
            timestamp INTEGER,
            datetime TEXT,
            processed_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_trade_to_db(trade_data):
    """
    將交易資料儲存到資料庫
    """
    try:
        conn = sqlite3.connect('/tmp/trades.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (symbol, price, volume, timestamp, datetime, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['symbol'],
            trade_data['price'],
            trade_data['volume'],
            trade_data['timestamp'],
            trade_data['datetime'],
            trade_data['processed_at']
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {str(e)}")

def analyze_price_movement(current_price):
    """
    分析價格走勢
    """
    if len(price_history) < 2:
        return {"trend": "insufficient_data"}
    
    # 計算移動平均
    recent_prices = list(price_history)[-10:]  # 最近10筆
    moving_avg = statistics.mean(recent_prices)
    
    # 判斷趨勢
    price_change = current_price - recent_prices[-1]
    percentage_change = (price_change / recent_prices[-1]) * 100
    
    trend = "up" if price_change > 0 else "down" if price_change < 0 else "flat"
    
    return {
        "trend": trend,
        "price_change": round(price_change, 2),
        "percentage_change": round(percentage_change, 2),
        "moving_average": round(moving_avg, 2),
        "current_price": current_price,
        "volatility": round(statistics.stdev(recent_prices), 2) if len(recent_prices) > 1 else 0
    }

def check_price_alerts(price, symbol):
    """
    檢查價格警報
    """
    alerts = []
    
    # 設定警報條件
    if symbol == "NVDA":
        if price > 500:
            alerts.append({"type": "high_price", "message": f"NVDA 價格超過 $500: ${price}"})
        elif price < 400:
            alerts.append({"type": "low_price", "message": f"NVDA 價格低於 $400: ${price}"})
    
    # 檢查急劇變動
    if len(price_history) >= 2:
        last_price = price_history[-1]
        change_percent = abs((price - last_price) / last_price) * 100
        
        if change_percent > 2:  # 超過2%變動
            alerts.append({
                "type": "price_spike",
                "message": f"{symbol} 價格急劇變動 {change_percent:.2f}%: ${price}"
            })
    
    return alerts

@app.route('/api/advanced_webhook', methods=['POST'])
def advanced_webhook():
    """
    進階 Webhook 處理器
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        print(f"Received data: {json.dumps(data, indent=2)}")
        
        processed_trades = []
        
        if 'data' in data:
            for trade in data['data']:
                symbol = trade.get('s', '')
                price = trade.get('p', 0)
                volume = trade.get('v', 0)
                timestamp = trade.get('t', 0)
                
                if symbol == 'NVDA':
                    # 建立交易資料
                    trade_data = {
                        'symbol': symbol,
                        'price': price,
                        'volume': volume,
                        'timestamp': timestamp,
                        'datetime': datetime.fromtimestamp(timestamp/1000).isoformat(),
                        'processed_at': datetime.now().isoformat()
                    }
                    
                    # 儲存到記憶體
                    recent_trades.append(trade_data)
                    price_history.append(price)
                    
                    # 儲存到資料庫 (在背景執行)
                    threading.Thread(
                        target=save_trade_to_db,
                        args=(trade_data,)
                    ).start()
                    
                    # 分析價格走勢
                    analysis = analyze_price_movement(price)
                    
                    # 檢查警報
                    alerts = check_price_alerts(price, symbol)
                    
                    # 組合結果
                    result = {
                        **trade_data,
                        'analysis': analysis,
                        'alerts': alerts
                    }
                    
                    processed_trades.append(result)
                    
                    print(f"Processed NVDA trade: {json.dumps(result, indent=2)}")
                    
                    # 如果有警報，可以在這裡發送通知
                    if alerts:
                        print(f"⚠️ ALERTS: {alerts}")
        
        return jsonify({
            "status": "success",
            "processed_trades": len(processed_trades),
            "trades": processed_trades
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    獲取統計資料
    """
    try:
        if not recent_trades:
            return jsonify({"message": "No trades data available"}), 200
        
        # 計算統計資料
        total_trades = len(recent_trades)
        total_volume = sum(trade['volume'] for trade in recent_trades)
        
        prices = [trade['price'] for trade in recent_trades]
        latest_price = prices[-1] if prices else 0
        highest_price = max(prices) if prices else 0
        lowest_price = min(prices) if prices else 0
        average_price = statistics.mean(prices) if prices else 0
        
        return jsonify({
            "total_trades": total_trades,
            "total_volume": total_volume,
            "latest_price": latest_price,
            "highest_price": highest_price,
            "lowest_price": lowest_price,
            "average_price": round(average_price, 2),
            "price_range": round(highest_price - lowest_price, 2),
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recent_trades', methods=['GET'])
def get_recent_trades():
    """
    獲取最近的交易記錄
    """
    limit = request.args.get('limit', 10, type=int)
    trades = list(recent_trades)[-limit:]
    
    return jsonify({
        "trades": trades,
        "count": len(trades),
        "total_available": len(recent_trades)
    })

# 初始化資料庫
init_db()

if __name__ == '__main__':
    app.run(debug=True)