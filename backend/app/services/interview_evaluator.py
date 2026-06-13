import re


def evaluate_interview_answer(question: str, expected_keywords: list[str], user_answer: str) -> dict[str, object]:
    answer_text = (user_answer or "").strip()
    normalized_answer = _normalize(answer_text)
    matched_keywords = [keyword for keyword in expected_keywords if _contains_keyword(normalized_answer, keyword)]
    missing_keywords = [keyword for keyword in expected_keywords if keyword not in matched_keywords]

    if not expected_keywords:
        keyword_score = 50.0
    else:
        keyword_score = (len(matched_keywords) / len(expected_keywords)) * 80.0
    length_bonus = _length_bonus(answer_text)
    score = round(min(100.0, keyword_score + length_bonus), 1)

    return {
        "score": score,
        "feedback": _build_feedback(score, matched_keywords, missing_keywords),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }


def build_session_summary(scores: list[float]) -> str:
    if not scores:
        return "Chưa có câu trả lời nào để tổng kết. Hãy trả lời ít nhất một câu trước khi finish session."
    average = round(sum(scores) / len(scores), 1)
    if average >= 80:
        level = "tốt"
        suggestion = "Tiếp tục luyện cách trả lời có cấu trúc STAR/project impact để tăng độ thuyết phục."
    elif average >= 60:
        level = "khá"
        suggestion = "Nên bổ sung keyword kỹ thuật quan trọng và ví dụ project cụ thể hơn trong câu trả lời."
    elif average >= 40:
        level = "trung bình"
        suggestion = "Cần ôn lại nền tảng và chuẩn bị câu trả lời theo từng skill gap trước khi phỏng vấn thật."
    else:
        level = "còn yếu"
        suggestion = "Nên học lại các khái niệm cốt lõi, làm mini project và luyện trả lời ngắn gọn từng câu."
    return f"Điểm trung bình {average}/100, mức độ sẵn sàng {level}. {suggestion}"


def _normalize(text: str) -> str:
    return text.lower().replace("node js", "node.js").replace("next js", "next.js")


def _contains_keyword(normalized_text: str, keyword: str) -> bool:
    normalized_keyword = _normalize(keyword)
    pattern = rf"(?<![a-z0-9+#.]){re.escape(normalized_keyword)}(?![a-z0-9+#.])"
    return re.search(pattern, normalized_text) is not None


def _length_bonus(answer: str) -> float:
    word_count = len(re.findall(r"\w+", answer))
    if word_count >= 80:
        return 20.0
    if word_count >= 40:
        return 14.0
    if word_count >= 20:
        return 8.0
    if word_count >= 8:
        return 4.0
    return 0.0


def _build_feedback(score: float, matched_keywords: list[str], missing_keywords: list[str]) -> str:
    strengths = ", ".join(matched_keywords[:5]) if matched_keywords else "chưa nêu rõ keyword kỹ thuật chính"
    missing = ", ".join(missing_keywords[:5]) if missing_keywords else "không thiếu keyword lớn trong question bank MVP"
    if score >= 80:
        advice = "Câu trả lời tốt; hãy thêm ví dụ project thật và impact để thuyết phục hơn."
    elif score >= 60:
        advice = "Câu trả lời ổn nhưng nên giải thích có cấu trúc hơn: khái niệm, cách làm, ví dụ, trade-off."
    else:
        advice = "Cần bổ sung keyword cốt lõi và đưa ví dụ cụ thể thay vì trả lời quá chung."
    return f"Điểm mạnh: {strengths}. Thiếu: {missing}. Gợi ý: {advice}"