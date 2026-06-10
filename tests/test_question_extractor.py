"""Tests for question extraction and normalization."""

from src.question_extractor import QuestionExtractor


def test_detects_question_mark():
    extractor = QuestionExtractor()
    assert extractor.is_question("Is the VPN down?")


def test_detects_question_word_at_start():
    extractor = QuestionExtractor()
    assert extractor.is_question("How do I reset my password")
    assert extractor.is_question("Can someone help with the deploy")


def test_detects_help_seeking_phrases():
    extractor = QuestionExtractor()
    assert extractor.is_question("Anyone know the wifi password")
    assert extractor.is_question("I was wondering if we support SSO")
    assert extractor.is_question("Not sure how to configure the linter")


def test_rejects_declarative_sentences():
    extractor = QuestionExtractor()
    # These contain auxiliary verbs mid-sentence and used to be false positives
    assert not extractor.is_question("The deploy is finished")
    assert not extractor.is_question("Our team has shipped the feature")
    assert not extractor.is_question("I did the migration yesterday")


def test_rejects_short_fragments_without_question_mark():
    extractor = QuestionExtractor()
    assert not extractor.is_question("How interesting")
    assert extractor.is_question("Why?")  # explicit '?' still counts


def test_extract_questions_from_mixed_text():
    extractor = QuestionExtractor()
    text = "The build passed. How do I get access to staging? Thanks all."
    questions = extractor.extract_questions(text)
    assert questions == ["How do I get access to staging?"]


def test_normalize_strips_fillers_and_case():
    extractor = QuestionExtractor()
    normalized = extractor.normalize_question("Hi team, How do I reset my password???")
    assert normalized == "how do i reset my password???"


def test_parse_slack_content_with_separator_and_dates():
    extractor = QuestionExtractor()
    content = (
        "2024-01-05\n"
        "How do I reset my password?\n"
        "-----------------------------------------------------------\n"
        "2024-01-08\n"
        "What is the deploy schedule?\n"
    )
    questions = extractor.parse_slack_content(content)
    assert len(questions) == 2
    assert questions[0]['date'] == '2024-01-05'
    assert questions[1]['date'] == '2024-01-08'
    assert questions[0]['text'] == 'How do I reset my password?'


def test_parse_slack_content_empty():
    extractor = QuestionExtractor()
    assert extractor.parse_slack_content("") == []
