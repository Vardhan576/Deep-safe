import re
import math
import base64
import binascii
import urllib.parse
import json
import codecs


# ─── AI DETECTION ────────────────────────────────────────────────────────────

def analyze_ai_probability(text: str):
    """
    Returns AI probability (0–100) and reasons.
    """
    if not text or len(text.strip()) < 20:
        return 0.0, ["Text is too short to analyze."]

    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    reasons = []
    score = 0

    # 1. Sentence length uniformity
    if sentences:
        avg_len = len(words) / len(sentences)
        lengths = [len(s.split()) for s in sentences]
        variance = sum((x - avg_len) ** 2 for x in lengths) / len(sentences)
        std_dev = math.sqrt(variance)

        if std_dev < 4.0:
            score += 40
            reasons.append("Very uniform sentence lengths — typical of AI text generators.")
        elif std_dev < 7.0:
            score += 22
            reasons.append("Moderately uniform sentence structure — may suggest AI authorship.")

    # 2. Vocabulary diversity
    lower_words = [w.lower().strip(".,!?;:\"'") for w in words]
    freq = {}
    for w in lower_words:
        freq[w] = freq.get(w, 0) + 1
    unique_ratio = len(freq) / max(len(words), 1)

    if unique_ratio < 0.40:
        score += 30
        reasons.append("Low vocabulary diversity — repetitive word use consistent with AI output.")
    elif unique_ratio < 0.60:
        score += 15
        reasons.append("Moderate vocabulary diversity — slightly repetitive wording detected.")

    # 3. Sentence length range
    if sentences:
        avg_len = len(words) / len(sentences)
        if 10 < avg_len < 25:
            score += 15
            reasons.append("Average sentence length falls in the 10–25 word range preferred by AI models.")

    # 4. Formal connector phrases common in AI
    ai_phrases = [
        "it is important to note", "it is worth noting", "in conclusion",
        "furthermore", "additionally", "moreover", "in summary", "as a result",
        "this suggests", "it can be seen", "it is clear that", "in order to",
        "plays a crucial role", "it is essential", "significantly",
        "on the other hand", "to summarize"
    ]
    text_lower = text.lower()
    matched = [p for p in ai_phrases if p in text_lower]
    if len(matched) >= 3:
        score += 25
        reasons.append(f"Multiple AI-style connector phrases found: {', '.join(matched[:5])}.")
    elif len(matched) >= 1:
        score += 10
        reasons.append(f"AI-style transition phrase(s) detected: {', '.join(matched)}.")

    # 5. Lack of contractions / colloquial language
    contractions = r"\b(isn't|aren't|wasn't|weren't|don't|doesn't|didn't|can't|couldn't|won't|wouldn't|it's|that's|I'm|I've|I'll|we're|they're)\b"
    if not re.search(contractions, text, re.IGNORECASE):
        score += 10
        reasons.append("No contractions found — AI-generated text is often overly formal.")

    # Variation based on hash (deterministic)
    variation = (hash(text) % 14) - 7
    final_score = max(0, min(100, score + variation))

    # Short text penalty
    if len(words) < 50:
        final_score *= (len(words) / 50.0)

    if not reasons:
        reasons.append("No strong AI indicators found in the text.")

    return round(final_score, 1), reasons


# ─── HIDDEN THREAT / ENCODING SCANNER ────────────────────────────────────────

def _try_base64(text: str):
    candidates = re.findall(r'[A-Za-z0-9+/]{16,}={0,2}', text)
    for c in candidates:
        try:
            decoded = base64.b64decode(c + '==').decode('utf-8', errors='strict')
            if decoded.isprintable() and len(decoded) > 4:
                return c, decoded
        except Exception:
            pass
    return None, None


def _try_hex(text: str):
    candidates = re.findall(r'\b[0-9a-fA-F]{8,}\b', text)
    for c in candidates:
        if len(c) % 2 == 0:
            try:
                decoded = bytes.fromhex(c).decode('utf-8', errors='strict')
                if decoded.isprintable() and len(decoded) > 3:
                    return c, decoded
            except Exception:
                pass
    return None, None


def _try_binary(text: str):
    candidates = re.findall(r'(?:[01]{8}\s?){4,}', text)
    for c in candidates:
        bits = c.replace(' ', '')
        if len(bits) % 8 == 0:
            try:
                chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
                decoded = ''.join(chars)
                if decoded.isprintable():
                    return c.strip(), decoded
            except Exception:
                pass
    return None, None


def _try_url_encoding(text: str):
    if '%' in text:
        try:
            decoded = urllib.parse.unquote(text)
            if decoded != text and decoded.isprintable():
                return text, decoded
        except Exception:
            pass
    return None, None


def _try_rot13(text: str):
    # Only flag ROT13 if it produces something meaningful (a flag-like pattern)
    try:
        decoded = codecs.decode(text, 'rot_13')
        flag_pattern = re.search(r'[A-Z]{3,}\{.+?\}', decoded)
        if flag_pattern:
            return text, decoded
    except Exception:
        pass
    return None, None


FLAG_PATTERN = re.compile(r'[A-Z]{2,10}\{[A-Za-z0-9_\-!@#$%^&*()+=<>?./\\,;:\'\" ]+?\}')


def scan_hidden_threats(text: str):
    """
    Scans for Base64, Hex, Binary, URL-encoded, ROT13, and flag patterns.
    Returns: (hidden_found, encoding_type, encoded_str, decoded_str, flag_found, flag)
    """
    # Direct flag check first
    direct_flag = FLAG_PATTERN.search(text)
    if direct_flag:
        return True, "plaintext_flag", direct_flag.group(), direct_flag.group(), True, direct_flag.group()

    # Base64
    enc, dec = _try_base64(text)
    if dec:
        flag = FLAG_PATTERN.search(dec)
        return True, "Base64", enc, dec, bool(flag), flag.group() if flag else ""

    # Hex
    enc, dec = _try_hex(text)
    if dec:
        flag = FLAG_PATTERN.search(dec)
        return True, "Hexadecimal", enc, dec, bool(flag), flag.group() if flag else ""

    # Binary
    enc, dec = _try_binary(text)
    if dec:
        flag = FLAG_PATTERN.search(dec)
        return True, "Binary", enc, dec, bool(flag), flag.group() if flag else ""

    # URL encoding
    enc, dec = _try_url_encoding(text)
    if dec:
        flag = FLAG_PATTERN.search(dec)
        return True, "URL Encoding", enc, dec, bool(flag), flag.group() if flag else ""

    # ROT13
    enc, dec = _try_rot13(text)
    if dec:
        flag = FLAG_PATTERN.search(dec)
        return True, "ROT13", enc, dec, bool(flag), flag.group() if flag else ""

    return False, "", "", "", False, ""


# ─── TRUST SCORE ─────────────────────────────────────────────────────────────

def calculate_trust_score(ai_probability: float, hidden_data: bool, flag_found: bool) -> (int, str):
    score = 100
    score -= int(ai_probability * 0.6)   # Max -60 for full AI probability
    if hidden_data:
        score -= 20
    if flag_found:
        score -= 15
    score = max(0, score)

    if score >= 70:
        risk = "Low"
    elif score >= 40:
        risk = "Medium"
    else:
        risk = "High"

    return score, risk


# ─── MASTER ANALYZER ─────────────────────────────────────────────────────────

def full_analysis(text: str) -> dict:
    ai_prob, ai_reasons = analyze_ai_probability(text)
    hidden, enc_type, enc_str, dec_str, flag_found, flag = scan_hidden_threats(text)
    trust, risk = calculate_trust_score(ai_prob, hidden, flag_found)

    # Final summary
    parts = []
    if ai_prob >= 70:
        parts.append(f"Content is very likely AI-generated ({ai_prob}%).")
    elif ai_prob >= 30:
        parts.append(f"Content shows moderate AI-generation signals ({ai_prob}%).")
    else:
        parts.append(f"Content appears mostly human-written ({ai_prob}% AI probability).")

    if hidden:
        parts.append(f"Hidden {enc_type}-encoded data was detected and decoded.")
        if flag_found:
            parts.append(f"A CTF flag was found: {flag}.")
    else:
        parts.append("No hidden encoded data found.")

    parts.append(f"Overall trust score: {trust}/100 — Risk: {risk}.")

    return {
        "ai_probability": ai_prob,
        "ai_reasons": ai_reasons,
        "hidden_data_found": hidden,
        "encoding_type": enc_type,
        "decoded_output": dec_str,
        "flag_found": flag_found,
        "flag": flag,
        "risk_level": risk,
        "trust_score": trust,
        "final_summary": " ".join(parts)
    }
