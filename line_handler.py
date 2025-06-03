from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from questions import questions
from diagnosis_logic import generate_result_text

# ユーザーごとの状態を一時記録（Renderでは短期記憶しか使えません）
user_states = {}

def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 🔍 デバッグ用ログ
    print(f"[DEBUG] message from {user_id}: '{text}'")

    # 栄養チェックの開始（柔軟にマッチ）
    if "栄養チェック" in text:
        user_states[user_id] = {"current_q": 1, "answers": {}}
        return send_question(user_id, 1)

    # 診断中のユーザーか？
    if user_id in user_states:
        state = user_states[user_id]
        q_num = state["current_q"]

        # 回答としてA/B/Cを受け取る
        if text in ["A", "B", "C"]:
            state["answers"][q_num] = text
            q_num += 1
            if q_num > 10:
                # 診断終了、結果を出力
                result = generate_result_text(state["answers"])
                del user_states[user_id]
                return TextSendMessage(text=result)
            else:
                state["current_q"] = q_num
                return send_question(user_id, q_num)
        else:
            return TextSendMessage(text="A〜Cで選んでください。")

    # 診断以外のとき
    return TextSendMessage(text="診断を始めるには「栄養チェック開始」と送信してください。")

def send_question(user_id, q_num):
    q = questions[q_num]
    text = q["text"]
    choices = q["choices"]
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label=f"{k}: {v}", text=k)) for k, v in choices.items()
    ])
    return TextSendMessage(text=text, quick_reply=quick_reply)
