# api/index.py
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        健康檢查端點
        """
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Finnhub Webhook Receiver for NVDA"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

    def do_POST(self):
        """
        處理 Finnhub Webhook 資料
        """
        try:
            # 讀取請求內容
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # 解析 JSON
            data = json.loads(post_data.decode('utf-8'))
            
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
                            'datetime': datetime.fromtimestamp(timestamp/1000).isoformat() if timestamp else '',
                            'processed_at': datetime.now().isoformat()
                        }
                        
                        processed_trades.append(processed_data)
                        print(f"NVDA Trade: {json.dumps(processed_data, indent=2)}")
                        
                        # 在這裡加入你的業務邏輯
                        self.process_nvda_trade(processed_data)
            
            # 返回成功響應
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "success",
                "message": "Webhook processed successfully",
                "processed_trades": len(processed_trades),
                "trades": processed_trades
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def process_nvda_trade(self, trade_data):
        """
        處理 NVDA 交易資料的業務邏輯
        """
        price = trade_data['price']
        volume = trade_data['volume']
        
        # 價格警報
        if price > 500:
            print(f"🚨 NVDA 價格警報: 超過 $500 - 當前價格 ${price}")
        elif price < 400:
            print(f"🚨 NVDA 價格警報: 低於 $400 - 當前價格 ${price}")
        
        # 大量交易警報
        if volume > 10000:
            print(f"📈 NVDA 大量交易: {volume} 股，價格 ${price}")
        
        # 這裡可以加入更多邏輯：
        # - 儲存到資料庫
        # - 發送通知
        # - 觸發交易決策
        # - 更新快取
        
        return True
