import pytest
import utils

def test_safe_parse_json_none():
    assert utils.safe_parse_json(None, default={"a": 1}) == {"a": 1}
    assert utils.safe_parse_json("", default={"a": 1}) == {"a": 1}

def test_safe_parse_json_valid():
    assert utils.safe_parse_json('{"key": "value"}') == {"key": "value"}

def test_safe_parse_json_markdown():
    text = "Here is some JSON:\n```json\n{\"key\": \"value\"}\n```"
    assert utils.safe_parse_json(text) == {"key": "value"}

def test_safe_parse_json_embedded():
    text = "Random garbage before {\"key\": \"value\"} random garbage after"
    assert utils.safe_parse_json(text) == {"key": "value"}

def test_safe_parse_json_malformed():
    assert utils.safe_parse_json("Not JSON at all", default={"error": True}) == {"error": True}

def test_safe_parse_json_malformed_markdown():
    # Looks like a block but invalid JSON
    text = "```json\n{\"key\": missing_quotes}\n```"
    assert utils.safe_parse_json(text, default={"err": 1}) == {"err": 1}

def test_safe_parse_json_malformed_embedded():
    # Looks like an object but invalid JSON
    text = "Embedded {invalid: json}"
    assert utils.safe_parse_json(text, default={"err": 2}) == {"err": 2}

def test_extract_character_mentions():
    text = "Elara and Malakar went to the tavern."
    names = ["Elara", "Malakar", "Kaelen"]
    found = utils.extract_character_mentions(text, names)
    assert set(found) == {"Elara", "Malakar"}
    assert "Kaelen" not in found

def test_extract_character_mentions_ignore_case():
    text = "ELARA and malakar"
    names = ["Elara", "Malakar"]
    found = utils.extract_character_mentions(text, names)
    assert set(found) == {"Elara", "Malakar"}
