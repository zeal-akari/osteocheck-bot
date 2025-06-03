from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from questions import questions
from diagnosis_logic import generate_result_text

# ユーザー状態管理
user_states = {}

def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 栄養チェック開始
    if text == "栄養チェック開始":
        user_states[user_id] = {"mode": "nutrition", "current_q": 1, "answers": {}}
        intro = (
            "🦴 1日分の栄養と生活習慣から、骨の健康バランスをチェックします！\n"
            "このチェックは、AIによる簡易的なセルフチェックです。\n"
            "「もう1品足してみようかな」くらいの軽い気持ちで試してみてください。\n"
            "答え方：すべての質問に A（食べていない） / B（1品） / C（2品以上）から選び、"
            "表示されたボタンをタップしてください。\n"
            "それでは、始めましょう！"
        )
        first_q = send_question(user_id, 1)
        return [TextSendMessage(text=intro), first_q]

    # 骨粗鬆症セルフチェック開始
    if text == "セルフチェック開始":
        user_states[user_id] = {"mode": "selfcheck", "step": 0}
        return TextSendMessage(text="セルフチェックを始めます。\nQ1: 牛乳、乳製品をあまりとらない（はい／いいえ）")

    # チェック進行中のユーザー
    if user_id in user_states:
        state = user_states[user_id]

        # 栄養チェックの処理
        if state["mode"] == "nutrition":
            q_num = state["current_q"]
            if text in ["A", "B", "C"]:
                state["answers"][q_num] = text
                q_num += 1
                if q_num > 10:
                    result = generate_result_text(state["answers"])
                    del user_states[user_id]
                    return TextSendMessage(text=result)
                else:
                    state["current_q"] = q_num
                    return send_question(user_id, q_num)
            else:
                del user_states[user_id]
                return TextSendMessage(text="診断を中断しました。\nもう一度「栄養チェック開始」と送信してください。")

        # 骨粗鬆症セルフチェックの処理
        elif state["mode"] == "selfcheck":
            step = state["step"]
            if text in ["はい", "いいえ"]:
                if step == 0:
                    state["step"] += 1
                    return TextSendMessage(text="Q2: 小魚、豆腐をあまりとらない（はい／いいえ）")
                elif step == 1:
                    del user_states[user_id]
                    return TextSendMessage(text="セルフチェックの結果：リスクが少し高めかもしれません。生活習慣に注意しましょう。")
            else:
                del user_states[user_id]
                return TextSendMessage(text="診断を中断しました。\nもう一度「セルフチェック開始」と送信してください。")

    # その他
    return TextSendMessage(text="診断を始めるには「セルフチェック開始」または「栄養チェック開始」と送信してください。")

def send_question(user_id, q_num):
    q = questions[q_num]
    text = q["text"]
    choices = q["choices"]
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label=f"{k}: {v}", text=k)) for k, v in choices.items()
    ])
    return TextSendMessage(text=text, quick_reply=quick_reply)
