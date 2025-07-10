# api/webhook.py
from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

def handler(request):
def handler(request):
    """
    Vercel Serverless Function Handler
    接收 Finnhub Webhook 資料
    """
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({"error": "Method not allowed"})
        }
    
    try:
        # 獲取 JSON 資料
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            # 處理 Vercel 的 request 格式
            data = json.loads(request.body) if request.body else {}
        
        if not data:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "No data received"})
            }
        
        # 記錄接收到的資料
        print(f"Received webhook data at {datetime.now()}: {json.dumps(data, indent=2)}")
        
        processed_trades = []
        
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
                    
                    processed_trades.append(processed_data)
                    print(f"NVDA Trade: {json.dumps(processed_data, indent=2)}")
                    
                    # 這裡可以加入你的業務邏輯
                    # 例如：儲存到資料庫、發送通知、觸發交易等
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                "status": "success", 
                "message": "Webhook processed successfully",
                "processed_trades": len(processed_trades),
                "trades": processed_trades
            })
        }
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }

# 如果是 GET 請求，返回健康檢查
def health_check():
    return {
        'statusCode': 200,
        'body': json.dumps({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Finnhub Webhook Receiver"
        })
    }

# 主要的處理函數
def main(request):
    if request.method == 'GET':
        return health_check()
    else:
        return handler(request)
