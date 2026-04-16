import random
import string
import base64
import codecs
from utils.cyber_analyzer import full_analysis

def generate_random_flag():
    inner = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"FLAG{{{inner}}}"

def build_ctf_challenge(category, difficulty):
    category = category.lower() if category else "general"
    difficulty = difficulty.lower() if difficulty else "easy"
    
    flag = generate_random_flag()
    raw_content = f"The secret system administrator password is {flag}. Do not share this."
    
    encoded_challenge = ""
    method = ""
    hints = []
    solution = ""
    
    if difficulty == "easy":
        # 1 encoding
        choice = random.choice(["base64", "hex", "rot13"])
        if choice == "base64":
            encoded_challenge = base64.b64encode(raw_content.encode()).decode()
            method = "Base64 Encoding"
            hints = ["Look for characters ending in =", "It's a very common web encoding."]
            solution = "Decode the string using Base64 to reveal the plaintext flag."
        elif choice == "hex":
            encoded_challenge = raw_content.encode().hex()
            method = "Hexadecimal Encoding"
            hints = ["Notice the characters only range from 0-9 and a-f", "Try converting hex to ascii."]
            solution = "Convert the hex string bytes back to ASCII."
        elif choice == "rot13":
            encoded_challenge = codecs.encode(raw_content, "rot_13")
            method = "ROT13 Cipher"
            hints = ["The letters are shifted by 13", "S is F, F is S."]
            solution = "Apply a ROT13 shift to the letters to decrypt."
            
    elif difficulty == "medium":
        # Base64 then Hex
        b64 = base64.b64encode(raw_content.encode()).decode()
        encoded_challenge = b64.encode().hex()
        method = "Hex + Base64 Multi-Layer"
        hints = ["This looks like hex, but what does it decode to?", "You might have to decode it twice."]
        solution = "First decode the hexadecimal string to raw text. It will result in a Base64 string. Decode the Base64 string to get the flag."
        
    else: # hard
        # ROT13 then Base64 then Hex
        rot = codecs.encode(raw_content, "rot_13")
        b64 = base64.b64encode(rot.encode()).decode()
        encoded_challenge = b64.encode().hex()
        method = "Hex + Base64 + ROT13 Triple-Layer"
        hints = ["There are multiple layers of obfuscation here.", "Hex -> Base64 -> ???", "Caesar shift by 13."]
        solution = "Decode Hex -> Decode Base64 -> Apply ROT13."

    # Now simulate cyber_analyzer
    analysis = full_analysis(encoded_challenge)
    
    # Map to requested JSON
    encodings_detected = [analysis.get('encoding_type', '')] if analysis.get('encoding_type') else []
    
    result = {
        "title": f"{category.capitalize()} Intercept",
        "category": category.capitalize(),
        "difficulty": difficulty.capitalize(),
        "description": f"We intercepted a suspicious communication related to {category}. Can you extract the hidden flag?",
        "challenge": encoded_challenge,
        "flag": flag,
        "hints": hints,
        "solution": solution,
        "method": method,
        "cyber_analysis": {
            "ai_probability": f"{analysis.get('ai_probability', 0)}%",
            "encodings_detected": encodings_detected,
            "decoded_content": analysis.get('decoded_output', ''),
            "flag_found": str(analysis.get('flag_found', False)).lower(),
            "trust_score": str(analysis.get('trust_score', 100)),
            "risk_level": analysis.get('risk_level', 'Low')
        }
    }
    
    return result
