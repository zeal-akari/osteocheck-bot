import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 環境変数からLINEのAPIキーを取得
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 診断質問と点数
questions = [
    ("牛乳、乳製品をあまりとらない", 2),
    ("小魚、豆腐をあまりとらない", 2),
    ("たばこをよく吸う", 2),
    ("お酒はよく飲む方だ", 1),
    ("天気のいい日でも、あまり外に出ない", 2),
    ("体を動かすことが少ない", 4),
    ("最近、背が縮んだような気がする", 6),
    ("背中が丸くなり、腰が曲がってきた気がする", 6),
    ("ちょっとしたことで骨折した", 10),
    ("体格は細身", 2),
    ("家族に骨粗鬆症の人がいる", 2),
    ("糖尿病や消化管手術の経験がある", 2),
    ("女性：閉経済／男性：70歳以上", 4)
]

# ユーザーごとの診断状態を保持
user_states = {}
user_scores = {}

# 確認用のルート
@app.route("/")
def index():
    return "骨粗鬆症セルフチェックBot 起動中"

# LINE Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ユーザーからのテキストメッセージ処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip().lower()

    if user_id not in user_states:
        if msg == "セルフチェック開始":
            user_states[user_id] = 0
            user_scores[user_id] = 0
            first_q = questions[0][0]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="骨粗鬆症セルフチェックを始めます。\n\n「はい」か「いいえ」で答えてください。\n\nQ1: " + first_q)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="診断を始めるには「セルフチェック開始」と送信してください。")
            )
    else:
        idx = user_states[user_id]
        if msg == "はい":
            user_scores[user_id] += questions[idx][1]

        idx += 1
        if idx >= len(questions):
            score = user_scores[user_id]
            if score <= 2:
                result = "今は心配ないと考えられます。生活習慣を維持しましょう。"
            elif score <= 5:
                result = "骨が弱くなる可能性があります。気をつけましょう。"
            elif score <= 9:
                result = "骨が弱くなっている危険性があります。注意しましょう。"
            else:
                result = "骨が弱くなっていると考えられます。一度医師の診察を受けてください。"

            del user_states[user_id]
            del user_scores[user_id]

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"✅ 診断結果：{score}点\n{result}")
            )
        else:
            user_states[user_id] = idx
            next_q = questions[idx][0]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"Q{idx + 1}: {next_q}")
            )

# Renderのためのポートバインド（これが重要！）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=por
