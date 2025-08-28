import json

from dataclasses import dataclass, field, asdict
from typing import List, Tuple
from fuzzywuzzy import fuzz

@dataclass
class QuizQuestion:
    question: str
    correctAnswer: str
    wrongAnswers: List[str]
    timeout: int = field(default=10)

    def as_dict(self):
        return asdict(self)

def search_str_in_file(file_path, word):
    with open(file_path, 'r', errors="ignore") as file:
        content = file.read().lower()
        words = content.split()
        if word.lower() in content:
            return file_path
        for w in words:
            if fuzz.ratio(w, word.lower()) > 80:
                return file_path

def load_quiz(filename: str):
    with open(filename, 'r') as file:
        quizDicts = json.load(file)
        questions = [QuizQuestion(**q) for q in quizDicts["listOfQuestions"]]
        title = quizDicts["title"]
    return questions, title

def save_quiz(filename: str, title: str, questions: List[QuizQuestion]):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        savedData = {"title": title, "listOfQuestions": [q.as_dict() for q in questions]}
        json.dump(savedData, file, indent=2)
