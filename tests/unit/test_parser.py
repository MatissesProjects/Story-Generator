import pytest
import parser

def test_detect_intent():
    assert parser.detect_intent("") == "EMPTY"
    assert parser.detect_intent("spark") == "SPARK"
    assert parser.detect_intent("continue") == "CONTINUE"
    assert parser.detect_intent("...") == "CONTINUE"
    assert parser.detect_intent('"Hello"') == "DIALOGUE"
    assert parser.detect_intent("I walk north") == "ACTION"

def test_is_valid_name():
    assert parser.is_valid_name("Elara") is True
    assert parser.is_valid_name("Dark-Knight") is True
    assert parser.is_valid_name("") is False
    assert parser.is_valid_name("This is a very long name that should be invalid") is False
    assert parser.is_valid_name("Invalid Name?") is False

def test_parse_dialogue_brackets_mandatory():
    text = "[Elara]: Hello.\nMalakar: Hi."
    parsed = parser.parse_dialogue(text)
    
    # Brackets are mandatory for Character tags in the current implementation
    assert len(parsed) == 1
    assert parsed[0][0] == "Elara"
    
    text_plain = "Just a story."
    parsed_plain = parser.parse_dialogue(text_plain)
    assert parsed_plain[0][0] == "Narrator"

def test_parse_dialogue_ignored_tags():
    text = "[System]: Update. [Narrator]: Real story."
    parsed = parser.parse_dialogue(text)
    assert len(parsed) == 1
    assert parsed[0][0] == "Narrator"

def test_stream_parser_basic():
    sp = parser.StreamParser()
    blocks = sp.feed("[Elara]: First part of ")
    assert len(blocks) == 0 # Buffer not complete
    
    blocks = sp.feed("the message.\n")
    assert len(blocks) == 1
    assert blocks[0] == ("Elara", "First part of the message.")

def test_stream_parser_mixed():
    sp = parser.StreamParser()
    text = "Intro text. [Malakar]: I am here.\n"
    blocks = sp.feed(text)
    assert len(blocks) == 2
    assert blocks[0] == ("Narrator", "Intro text.")
    assert blocks[1] == ("Malakar", "I am here.")

def test_stream_parser_flush():
    sp = parser.StreamParser()
    sp.feed("[Narrator]: Final words")
    blocks = sp.flush()
    assert len(blocks) == 1
    assert blocks[0] == ("Narrator", "Final words")

def test_parse_dialogue_pure_system_tag():
    assert parser.parse_dialogue("[System]") == []
    assert parser.parse_dialogue("***") == []

def test_stream_parser_system_tags_ignored():
    sp = parser.StreamParser()
    blocks = sp.feed("[Script]: Ignore me.\n[Narrator]: See me.\n")
    assert len(blocks) == 1
    assert blocks[0][0] == "Narrator"
