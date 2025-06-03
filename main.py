import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

from line_handler import handle_message

# 環境変数からLINEの認証情報を取得
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

app = Flask(__name__)

# Webhookエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# メッセージイベントに対する処理
@handler.add(MessageEvent, message=TextMessage)
def on_message(event):
    reply = handle_message(event)
    if reply:
        line_bot_api.reply_message(event.reply_token, reply)

# 🔧 Render対応：Flaskを指定ポートで起動（デフォルト: 10000）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
