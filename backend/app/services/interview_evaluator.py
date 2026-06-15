import re

GENERIC_WORDS = {"good", "ok", "yes", "no", "em", "toi", "t?i", "lam", "l?m", "project", "code", "api"}
PROJECT_TERMS = ("project", "d\u1ef1 \u00e1n", "x\u00e2y", "built", "implemented", "developed", "tri\u1ec3n khai", "m\u00f4 t\u1ea3")
TRADEOFF_TERMS = ("tradeoff", "trade-off", "\u0111\u00e1nh \u0111\u1ed5i", "khi n\u00e0o", "v\u00ec sao", "t\u00f9y", "ph\u01b0\u01a1ng \u00e1n")
CONCEPT_TERMS = ("l\u00e0", "ho\u1ea1t \u0111\u1ed9ng", "c\u00e1ch", "nguy\u00ean l\u00fd", "flow", "quy tr\u00ecnh")


def evaluate_interview_answer(question: str, expected_keywords: list[str], user_answer: str) -> dict[str, object]:
    answer_text = (user_answer or "").strip()
    normalized_answer = _normalize(answer_text)
    matched_keywords = [keyword for keyword in expected_keywords if _contains_keyword(normalized_answer, keyword)]
    missing_keywords = [keyword for keyword in expected_keywords if keyword not in matched_keywords]

    if not expected_keywords:
        keyword_score = 50.0
    else:
        keyword_score = (len(matched_keywords) / len(expected_keywords)) * 72.0
    length_bonus = _length_bonus(answer_text)
    evidence_bonus = _evidence_bonus(normalized_answer)
    score = round(min(100.0, keyword_score + length_bonus + evidence_bonus), 1)
    category = _classify_feedback(answer_text, normalized_answer, matched_keywords, missing_keywords)
    hint = _better_answer_hint(category, missing_keywords)

    return {
        "score": score,
        "feedback": _build_feedback(score, matched_keywords, missing_keywords, category, hint),
        "feedback_category": category,
        "better_answer_hint": hint,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }


def build_session_summary(scores: list[float]) -> str:
    if not scores:
        return "Ch\u01b0a c\u00f3 c\u00e2u tr\u1ea3 l\u1eddi n\u00e0o \u0111\u1ec3 t\u1ed5ng k\u1ebft. H\u00e3y tr\u1ea3 l\u1eddi \u00edt nh\u1ea5t m\u1ed9t c\u00e2u tr\u01b0\u1edbc khi k\u1ebft th\u00fac phi\u00ean."
    average = round(sum(scores) / len(scores), 1)
    if average >= 80:
        level = "t\u1ed1t"
        suggestion = "Ti\u1ebfp t\u1ee5c luy\u1ec7n c\u00e2u tr\u1ea3 l\u1eddi c\u00f3 v\u00ed d\u1ee5 project, tradeoff v\u00e0 k\u1ebft qu\u1ea3 th\u1ef1c t\u1ebf."
    elif average >= 60:
        level = "kh\u00e1"
        suggestion = "N\u00ean b\u1ed5 sung keyword k\u1ef9 thu\u1eadt quan tr\u1ecdng v\u00e0 v\u00ed d\u1ee5 project c\u1ee5 th\u1ec3 h\u01a1n."
    elif average >= 40:
        level = "trung b\u00ecnh"
        suggestion = "C\u1ea7n \u00f4n l\u1ea1i concept n\u1ec1n t\u1ea3ng v\u00e0 chu\u1ea9n b\u1ecb c\u00e2u tr\u1ea3 l\u1eddi theo skill gap tr\u01b0\u1edbc khi ph\u1ecfng v\u1ea5n th\u1eadt."
    else:
        level = "c\u1ea7n luy\u1ec7n th\u00eam"
        suggestion = "N\u00ean h\u1ecdc l\u1ea1i concept c\u1ed1t l\u00f5i, l\u00e0m mini project v\u00e0 luy\u1ec7n tr\u1ea3 l\u1eddi ng\u1eafn g\u1ecdn t\u1eebng c\u00e2u."
    return f"\u0110i\u1ec3m trung b\u00ecnh {average}/100, m\u1ee9c \u0111\u1ed9 s\u1eb5n s\u00e0ng {level}. {suggestion}"


def _normalize(text: str) -> str:
    return text.lower().replace("node js", "node.js").replace("next js", "next.js")


def _contains_keyword(normalized_text: str, keyword: str) -> bool:
    normalized_keyword = _normalize(keyword)
    pattern = rf"(?<![a-z0-9+#.]){re.escape(normalized_keyword)}(?![a-z0-9+#.])"
    return re.search(pattern, normalized_text) is not None


def _length_bonus(answer: str) -> float:
    word_count = len(re.findall(r"\w+", answer))
    if word_count >= 80:
        return 18.0
    if word_count >= 40:
        return 12.0
    if word_count >= 20:
        return 7.0
    if word_count >= 8:
        return 3.0
    return 0.0


def _evidence_bonus(normalized_answer: str) -> float:
    bonus = 0.0
    if any(term in normalized_answer for term in PROJECT_TERMS):
        bonus += 5.0
    if any(term in normalized_answer for term in TRADEOFF_TERMS):
        bonus += 3.0
    return bonus


def _classify_feedback(answer_text: str, normalized_answer: str, matched_keywords: list[str], missing_keywords: list[str]) -> str:
    word_count = len(re.findall(r"\w+", answer_text))
    if word_count < 12:
        return "tr\u1ea3 l\u1eddi qu\u00e1 ng\u1eafn"
    if len(matched_keywords) <= 1 and missing_keywords:
        return "thi\u1ebfu concept"
    if not any(term in normalized_answer for term in PROJECT_TERMS):
        return "thi\u1ebfu v\u00ed d\u1ee5 project"
    if not any(term in normalized_answer for term in TRADEOFF_TERMS) and len(matched_keywords) < max(3, len(missing_keywords)):
        return "thi\u1ebfu tradeoff"
    if _is_generic_answer(normalized_answer):
        return "tr\u1ea3 l\u1eddi qu\u00e1 chung"
    return "c\u00f3 d\u1ea5u hi\u1ec7u hi\u1ec3u \u0111\u00fang"


def _is_generic_answer(normalized_answer: str) -> bool:
    words = re.findall(r"[a-zA-Z\u00c0-\u1ef9]+", normalized_answer)
    if len(words) < 25:
        return False
    generic_count = sum(1 for word in words if word in GENERIC_WORDS)
    return generic_count >= max(4, len(words) // 5)


def _better_answer_hint(category: str, missing_keywords: list[str]) -> str:
    missing = ", ".join(missing_keywords[:3])
    if category == "tr\u1ea3 l\u1eddi qu\u00e1 ng\u1eafn":
        return "H\u00e3y m\u1edf r\u1ed9ng c\u00e2u tr\u1ea3 l\u1eddi theo 3 ph\u1ea7n: kh\u00e1i ni\u1ec7m, c\u00e1ch l\u00e0m, v\u00ed d\u1ee5 project."
    if category == "thi\u1ebfu concept":
        return f"B\u1ed5 sung concept c\u1ed1t l\u00f5i v\u00e0 keyword quan tr\u1ecdng: {missing}." if missing else "B\u1ed5 sung concept c\u1ed1t l\u00f5i tr\u01b0\u1edbc khi n\u00f3i v\u1ec1 project."
    if category == "thi\u1ebfu v\u00ed d\u1ee5 project":
        return "Th\u00eam m\u1ed9t v\u00ed d\u1ee5 project th\u1eadt: b\u1ea1n x\u00e2y g\u00ec, d\u00f9ng tech n\u00e0o, g\u1eb7p l\u1ed7i g\u00ec v\u00e0 x\u1eed l\u00fd ra sao."
    if category == "thi\u1ebfu tradeoff":
        return "N\u00ean n\u00f3i th\u00eam tradeoff: khi n\u00e0o ch\u1ecdn c\u00e1ch n\u00e0y, khi n\u00e0o kh\u00f4ng n\u00ean d\u00f9ng."
    if category == "tr\u1ea3 l\u1eddi qu\u00e1 chung":
        return "L\u00e0m c\u00e2u tr\u1ea3 l\u1eddi c\u1ee5 th\u1ec3 h\u01a1n b\u1eb1ng t\u00ean tech stack, responsibility v\u00e0 output th\u1eadt."
    return "C\u00e2u tr\u1ea3 l\u1eddi \u0111\u00e3 c\u00f3 n\u1ec1n t\u1ea3ng; h\u00e3y th\u00eam project evidence v\u00e0 tradeoff \u0111\u1ec3 thuy\u1ebft ph\u1ee5c h\u01a1n."


def _build_feedback(score: float, matched_keywords: list[str], missing_keywords: list[str], category: str, hint: str) -> str:
    strengths = ", ".join(matched_keywords[:5]) if matched_keywords else "ch\u01b0a n\u00eau r\u00f5 keyword k\u1ef9 thu\u1eadt ch\u00ednh"
    missing = ", ".join(missing_keywords[:5]) if missing_keywords else "kh\u00f4ng thi\u1ebfu keyword l\u1edbn trong question bank MVP"
    if score >= 80:
        good = "C\u00e2u tr\u1ea3 l\u1eddi kh\u00e1 thuy\u1ebft ph\u1ee5c."
    elif score >= 60:
        good = "C\u00e2u tr\u1ea3 l\u1eddi c\u00f3 n\u1ec1n t\u1ea3ng nh\u01b0ng c\u1ea7n r\u00f5 h\u01a1n."
    else:
        good = "C\u00e2u tr\u1ea3 l\u1eddi c\u1ea7n b\u1ed5 sung concept v\u00e0 evidence."
    return f"Ph\u00e2n lo\u1ea1i feedback: {category}. \u0110i\u1ec3m t\u1ed1t: {good} Keyword \u0111\u00e3 n\u00eau: {strengths}. \u0110i\u1ec3m c\u00f2n thi\u1ebfu: {missing}. G\u1ee3i \u00fd b\u1ed5 sung: {hint}"
