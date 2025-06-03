from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction
)
from questions import questions
from selfcheck_questions import selfcheck_questions
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
        first_q = send_nutrition_question(user_id, 1)
        return [TextSendMessage(text=intro), first_q]

    # 骨粗鬆症セルフチェック開始
    if text == "セルフチェック開始":
        user_states[user_id] = {"mode": "selfcheck", "current_q": 1, "score": 0}
        return send_selfcheck_question(user_id, 1)

    # 進行中ユーザーの回答処理
    if user_id in user_states:
        state = user_states[user_id]

        # 栄養チェック処理
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
                    return send_nutrition_question(user_id, q_num)
            else:
                del user_states[user_id]
                return TextSendMessage(text="診断を中断しました。\nもう一度「栄養チェック開始」と送信してください。")

        # 骨粗鬆症セルフチェック処理
        elif state["mode"] == "selfcheck":
            q_num = state["current_q"]
            if text in ["はい", "いいえ"]:
                if text == "はい":
                    state["score"] += selfcheck_questions[q_num]["score"]
                q_num += 1
                if q_num > len(selfcheck_questions):
                    score = state["score"]
                    if score <= 2:
                        result = "今は心配ないと考えられます。生活習慣を維持しましょう。"
                    elif score <= 5:
                        result = "骨が弱くなる可能性があります。気をつけましょう。"
                    elif score <= 9:
                        result = "骨が弱くなっている危険性があります。注意しましょう。"
                    else:
                        result = "骨が弱くなっていると考えられます。一度医師の診察を受けてください。"
                    del user_states[user_id]
                    return TextSendMessage(text=f"✅ 診断結果：{score}点\n{result}")
                else:
                    state["current_q"] = q_num
                    return send_selfcheck_question(user_id, q_num)
            else:
                del user_states[user_id]
                return TextSendMessage(text="診断を中断しました。\nもう一度「セルフチェック開始」と送信してください。")

    # 未対応メッセージ
    return TextSendMessage(text="診断を始めるには「セルフチェック開始」または「栄養チェック開始」と送信してください。")

def send_nutrition_question(user_id, q_num):
    q = questions[q_num]
    text = q["text"]
    choices = q["choices"]
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label=f"{k}: {v}", text=k)) for k, v in choices.items()
    ])
    return TextSendMessage(text=f"Q{q_num}: {text}", quick_reply=quick_reply)

def send_selfcheck_question(user_id, q_num):
    q_text = selfcheck_questions[q_num]["text"]
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="はい", text="はい")),
        QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ")),
    ])
    return TextSendMessage(text=f"Q{q_num}: {q_text}", quick_reply=quick_reply)
