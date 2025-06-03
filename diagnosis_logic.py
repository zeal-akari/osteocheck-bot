from comments import advice_comments, praise_comments
from questions import questions

# 通常スコアマッピング
score_map = {"A": 0, "B": 1, "C": 2}

# 加工食品（Q8）は逆スコア
junk_score_map = {"A": 2, "B": 1, "C": 0}

# 総合評価コメント（点数による）
summary_comments = {
    (18, 20): "🌟 今日はとても良いバランスがとれていたのではないでしょうか。",
    (16, 17): "👍 全体的にバランスの良い1日だったように思われます。",
    (13, 15): "😊 悪くないバランスだったかもしれません。",
    (0, 12):  "⚠️ やや偏りがあったかもしれません。まずは一つずつ、できそうなことから始めてみてはいかがでしょうか。"
}

def get_summary(score):
    for (low, high), comment in summary_comments.items():
        if low <= score <= high:
            return comment
    return ""

def evaluate(user_answers):
    total_score = 0
    c_count = 0
    advice_tags = []
    praise_tags = []

    for q_num, answer in user_answers.items():
        tags = questions[q_num]["tags"]

        # 加工食品は逆スコア
        if q_num == 8:
            score = junk_score_map[answer]
        else:
            score = score_map.get(answer, 0)
        
        total_score += score

        # コメント分類
        if answer in ["A", "B"]:
            advice_tags.extend(tags)
        elif answer == "C" and q_num != 8:
            praise_tags.extend(tags)
            c_count += 1

    return total_score, c_count, advice_tags, praise_tags

def generate_result_text(user_answers):
    score, c_count, advice_tags, praise_tags = evaluate(user_answers)
    stars = "★" * (score // 4) + "☆" * (5 - score // 4)
    result = f"🦴 骨の健康スコア：{stars}（{score}/20）\n\n"
    result += get_summary(score) + "\n\n"

    # アドバイス（最大4件）
    shown = 0
    for tag in advice_tags:
        if tag in advice_comments:
            result += advice_comments[tag] + "\n\n"
            shown += 1
        if shown >= 4:
            break

    # 褒めコメント（条件：スコア16以上 & C回答5件以上）
    if score >= 16 and c_count >= 5:
        shown = 0
        for tag in praise_tags:
            if tag in praise_comments:
                result += praise_comments[tag] + "\n\n"
                shown += 1
            if shown >= 2:
                break

    return result.strip()
