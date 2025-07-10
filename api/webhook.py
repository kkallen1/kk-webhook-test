# api/webhook.py
from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """
    接收 Finnhub Webhook 資料
    """
    try:
        # 獲取 JSON 資料
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # 記錄接收到的資料
        print(f"Received webhook data at {datetime.now()}: {json.dumps(data, indent=2)}")
        
        # 處理股票資料
        if 'data' in data:
            for trade in data['data']:
                symbol = trade.get('s', '')  # 股票代碼
                price = trade.get('p', 0)    # 價格
                volume = trade.get('v', 0)   # 成交量
                timestamp = trade.get('t', 0) # 時間戳
                
                # 只處理 Nvidia (NVDA) 的資料
                if symbol == 'NVDA':
                    processed_data = {
                        'symbol': symbol,
                        'price': price,
                        'volume': volume,
                        'timestamp': timestamp,
                        'datetime': datetime.fromtimestamp(timestamp/1000).isoformat(),
                        'processed_at': datetime.now().isoformat()
                    }
                    
                    print(f"NVDA Trade: {json.dumps(processed_data, indent=2)}")
                    
                    # 這裡可以加入你的業務邏輯
                    # 例如：儲存到資料庫、發送通知、觸發交易等
                    
        return jsonify({"status": "success", "message": "Webhook processed successfully"}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康檢查端點
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Finnhub Webhook Receiver"
    })

# Vercel 需要這個
if __name__ == '__main__':
    app.run(debug=True)