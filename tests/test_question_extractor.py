"""Tests for question extraction and normalization."""

from slack_question_analyzer.question_extractor import QuestionExtractor


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


def test_document_header_not_glued_onto_question():
    """A header line above the date must not leak into the first question."""
    extractor = QuestionExtractor()
    content = (
        "MFT Content from the Slack threads\n"
        "June 9, 2026\n"
        "\n"
        "Hi Team, Can I check if the Metering Agent comes pre-installed?\n"
    )
    questions = extractor.parse_slack_content(content)
    assert len(questions) == 1
    assert questions[0]['text'] == 'Can I check if the Metering Agent comes pre-installed?'
    assert 'MFT Content' not in questions[0]['text']
    assert questions[0]['date'] == 'June 9, 2026'


def test_leading_greetings_stripped():
    extractor = QuestionExtractor()
    assert extractor.strip_greeting('Hi Team, how do I reset?') == 'how do I reset?'
    assert extractor.strip_greeting('Hello everyone! Hey folks, is VPN down?') == 'is VPN down?'
    assert extractor.strip_greeting('Good morning - can someone help?') == 'can someone help?'
    # No greeting: untouched; greeting-only: kept rather than emptied
    assert extractor.strip_greeting('How do I reset?') == 'How do I reset?'
    assert extractor.strip_greeting('Hi team!') == 'Hi team!'


def test_multiline_message_keeps_sentences_apart():
    """Lines are sentence boundaries even without punctuation."""
    extractor = QuestionExtractor()
    questions = extractor.questions_from_messages([{
        'text': 'Some context line without punctuation\nHow do I configure alerts?',
        'date': '2024-01-05',
    }])
    assert len(questions) == 1
    assert questions[0]['text'] == 'How do I configure alerts?'


def test_abbreviations_do_not_split_sentences():
    """Fixture-2 regression: the splitter tore 'maintenance window, e.g.
    1am to 4am?' into fragments at the 'e.g.' period."""
    from slack_question_analyzer.question_extractor import QuestionExtractor
    extractor = QuestionExtractor()
    questions = extractor.extract_questions(
        'Is there a way to set a transfer to only run during a maintenance '
        'window, e.g. 1am to 4am?')
    assert questions == ['Is there a way to set a transfer to only run '
                         'during a maintenance window, e.g. 1am to 4am?']

    questions = extractor.extract_questions(
        'Can we whitelist protocols, i.e. SFTP and FTPS only?')
    assert len(questions) == 1 and 'i.e. SFTP' in questions[0]
