import hashlib
from collections import Counter
import re

def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def normalize_for_palindrome(value: str) -> str:
    clean_str = re.sub(r"[^a-zA-Z0-9]", "", value)
    return clean_str.lower()

def is_palindrome(value: str) -> bool:
    normalized = normalize_for_palindrome(value)
    return normalized == normalized[::-1]

def character_frequency_map(value: str) -> dict:
    return dict(Counter(value))

def unique_characters(value: str) -> int:
    return len(set(value))

def word_count(value: str) -> int:
    clean_words = []
    for w in value.split():
        if w:
            clean_words.append(w)
    return len(clean_words)