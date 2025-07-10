# setup_webhook.py
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def setup_finnhub_webhook():
    """
    設定 Finnhub Webhook
    """
    api_key = os.getenv('FINNHUB_API_KEY')
    webhook_url = "https://your-vercel-app.vercel.app/api/webhook"  # 替換成你的 Vercel 部署網址
    
    if not api_key:
        print("請先設定 FINNHUB_API_KEY 環境變數")
        return
    
    # 註冊 Webhook
    webhook_data = {
        "symbol": "NVDA",  # Nvidia 股票代碼
        "webhook": webhook_url
    }
    
    headers = {
        "X-Finnhub-Token": api_key,
        "Content-Type": "application/json"
    }
    
    # 註冊 Webhook (這是假設的 API，實際可能不同)
    response = requests.post(
        "https://finnhub.io/api/v1/webhook",
        json=webhook_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print("Webhook 註冊成功！")
        print(f"已註冊 NVDA 的即時資料推送到: {webhook_url}")
    else:
        print(f"註冊失敗: {response.status_code}")
        print(response.text)

def test_webhook():
    """
    測試 Webhook 端點
    """
    webhook_url = "https://your-vercel-app.vercel.app/api/webhook"
    
    # 模擬 Finnhub 的 Webhook 資料格式
    test_data = {
        "data": [
            {
                "s": "NVDA",        # 股票代碼
                "p": 450.25,        # 價格
                "v": 1000,          # 成交量
                "t": 1634567890000, # 時間戳 (毫秒)
                "c": [1, 2, 3]      # 交易條件
            }
        ],
        "type": "trade"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"測試回應狀態碼: {response.status_code}")
        print(f"測試回應內容: {response.text}")
        
    except Exception as e:
        print(f"測試失敗: {str(e)}")

if __name__ == "__main__":
    print("1. 設定 Webhook")
    print("2. 測試 Webhook")
    choice = input("請選擇操作 (1/2): ")
    
    if choice == "1":
        setup_finnhub_webhook()
    elif choice == "2":
        test_webhook()
    else:
        print("無效選擇")