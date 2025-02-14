#!/usr/bin/env python3
import random
import json
import subprocess
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class QuizQuestion:
    question: str
    correctAnswer: str
    wrongAnswers: List[str]
    timeout: int = field(default=10)

    def __repr__(self):
        return self.question

def load_quiz(filename: str) -> Tuple[List[QuizQuestion], str]:
    with open(filename, 'r') as file:
        quizDicts = json.load(file)
        questionList = []
        for q in quizDicts["listOfQuestions"]:
            qq = QuizQuestion(**q)
            questionList.append(qq)
        titleofquiz = quizDicts["title"]
    return questionList, titleofquiz

def main():
    print("Welcome to QuizMasterMini")
    while True:
        print("1. Play a Quiz")
        print("2. Make a Quiz")
        print("3. Quit")
        choice = input("Enter choice: ").lower()

        if choice == "3" or choice == "Quit" or choice == "q" or choice == "3. Quit":
            break
        elif choice == "2" or choice == "Make" or choice == "Make a Quiz" or choice == "2. Make a Quiz":
            subprocess.Popen(["python3", "quizcreator.py"])
        elif choice == "1"or choice == "Play" or choice == "Play a Quiz" or choice == "1. Play a Quiz":            
            filename = input("Please select a quiz file (path to .json): ")
            if not filename:
                continue

            questions, title = load_quiz(filename)
            question_index = 0
            score = 0

            while question_index < len(questions):
                current_question = questions[question_index]
                correct_answer = current_question.correctAnswer
                wrong_answers = current_question.wrongAnswers
                answers = random.sample([correct_answer] + wrong_answers, len(wrong_answers) + 1)

                print(f"Question: {current_question.question}")
                for i, answer in enumerate(answers):
                    print(f"{i+1}. {answer}")
                user_answer = input("Select the correct answer: ")

                if user_answer.isdigit() and 1 <= int(user_answer) <= len(answers):
                    if answers[int(user_answer) - 1] == correct_answer:
                        score += 1
                else:
                    print("Invalid choice. Please select a valid answer.")

                question_index += 1

                if question_index >= len(questions):
                    print(f"Quiz completed! Your score: {score}/{len(questions)}")

    print("Goodbye!")

if __name__ == "__main__":
    main()
