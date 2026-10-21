import json
from medmentor.study import parse_quiz


def test_quiz_response_parser():
    payload = {"questions": [{
        "question": "Yurak urishini qaysi tuzilma boshqaradi?",
        "options": ["SA tugun", "AV qopqoq", "Aorta", "O'pka"],
        "answer": 0,
        "explanation": "SA tugun asosiy peysmeyker."
    }]}
    questions = parse_quiz(json.dumps(payload))
    assert questions[0]["answer"] == 0


def test_reject_invalid_answer():
    payload = {"questions": [{
        "question": "Yurak urishini qaysi tuzilma boshqaradi?",
        "options": ["A", "B", "C", "D"],
        "answer": 9,
    }]}
    try:
        parse_quiz(json.dumps(payload))
    except ValueError:
        pass
    else:
        assert False, "Invalid answer was accepted"
