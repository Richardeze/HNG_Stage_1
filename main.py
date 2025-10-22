from flask import Flask, request, jsonify, abort
from datetime import datetime, timezone
import re
import sqlite3
from utils import (sha256_hash, is_palindrome, normalize_for_palindrome,
                   character_frequency_map, unique_characters, word_count)
import db

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
db.init_db()

def iso_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the HNG Stage 1 String Analyzer API!"
    }), 200

@app.route("/strings", methods=["POST"])
def create_string():
    data = request.get_json()
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    if "value" not in data:
        return jsonify({"error": "Missing 'value' field"}), 400

    value = data["value"]
    if not isinstance(value, str):
        return jsonify({"error": " 'value' must be a string"}), 422

    sha_hash = sha256_hash(value)
    existing = db.get_by_hash(sha_hash)
    if existing is not None:
        return jsonify({"error": "String already exists"}), 409

    length = len(value)
    palindrome = is_palindrome(value)
    unique_chars = unique_characters(value)
    wc = word_count(value)
    freq_map = character_frequency_map(value)
    created_at = iso_now()

    record = {
        "id": sha_hash,
        "value": value,
        "length": length,
        "is_palindrome": palindrome,
        "unique_characters": unique_chars,
        "word_count": wc,
        "sha256_hash": sha_hash,
        "character_frequency_map": freq_map,
        "created_at": created_at
    }
    db.insert_string(record)
    response_sendback = {
        "id":sha_hash,
        "value": value,
        "properties": {
            "length": length,
            "is_palindrome": palindrome,
            "unique_characters": unique_chars,
            "word_count": wc,
            "sha256_hash": sha_hash,
            "character_frequency_map": freq_map
        },
        "created_at": created_at
    }
    return jsonify(response_sendback), 201

@app.route("/strings/<string_value>", methods=["GET"])
def get_string(string_value):
    record = db.get_by_value(string_value)
    if record is None:
        return jsonify({"error": "String not found"}), 404
    response_sendback = {
        "id": record["id"],
        "value": record["value"],
        "properties": record["properties"],
        "created_at": record["created_at"]
    }
    return jsonify(response_sendback), 200

@app.route("/strings", methods=["GET"])
def list_strings():
    records = db.list_all()

    is_palindrome = request.args.get("is_palindrome")
    min_length = request.args.get("min_length", type=int)
    max_length = request.args.get("max_length", type=int)
    word_count = request.args.get("word_count", type=int)
    contains_character = request.args.get("contains_character")

    filtered = []

    for rec in records:
        props = rec["properties"]
        if is_palindrome is not None:
            bool_val = is_palindrome.lower() == "true"
            if props["is_palindrome"] != bool_val:
                continue

        if min_length is not None and props["length"] < min_length:
            continue

        if max_length is not None and props["length"] > max_length:
            continue

        if word_count is not None and props["word_count"] != word_count:
            continue

        if contains_character is not None and contains_character not in rec["value"]:
            continue

        filtered.append(rec)

    response_sendback = {
        "data": filtered,
        "count": len(filtered),
        "filters_applied": {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character
        }
    }

    return jsonify(response_sendback), 200

@app.route("/strings/filter-by-natural-language", methods=["GET"])
def filter_by_natural_language():
    query = request.args.get("query", "").lower().strip()
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    filters = {}

    if "palindrome" in query or "palindromic" in query:
        filters["is_palindrome"] = True

    if "single word" in query or "one word" in query:
        filters["word_count"] = 1
    elif "two words" in query:
        filters["word_count"] = 2

    match_longer = re.search(r"longer than (\d+)", query)
    match_shorter = re.search(r"shorter than (\d+)", query)
    if match_longer:
        filters["min_length"] = int(match_longer.group(1)) + 1
    if match_shorter:
        filters["max_length"] = int(match_shorter.group(1)) - 1

    match_contains = re.search(r"containing the letter (\w)", query)
    if match_contains:
        filters["contains_character"] = match_contains.group(1).lower()

    if not filters:
        return jsonify({
            "error": "Unable to parse natural language query",
            "query": query
        }), 400

    records = db.list_all()

    filtered = []
    for rec in records:
        props = rec["properties"]

        if "is_palindrome" in filters and props["is_palindrome"] != filters["is_palindrome"]:
            continue
        if "word_count" in filters and props["word_count"] != filters["word_count"]:
            continue
        if "min_length" in filters and props["length"] < filters["min_length"]:
            continue
        if "max_length" in filters and props["length"] > filters["max_length"]:
            continue
        if "contains_character" in filters and filters["contains_character"] not in rec["value"]:
            continue

        filtered.append(rec)

    response_sendback = {
        "data": filtered,
        "count": len(filtered),
        "interpreted_query": {
            "original": query,
            "parsed_filters": filters
        }
    }
    return jsonify(response_sendback), 200

@app.route("/strings/<string_value>", methods=["DELETE"])
def delete_string(string_value):
    deleted = db.delete_by_value(string_value)
    if not deleted:
        return jsonify({"error": "String not found"}), 404

    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)