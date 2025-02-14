#!/usr/bin/env python3
import random
import json
import os
import sys
import time
from glob import glob
from fuzzywuzzy import fuzz
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

def sprint(str):
   for c in str + '\n':
     sys.stdout.write(c)
     sys.stdout.flush()
     time.sleep(3./90)

def search_str_in_file(file_path, word):
    with open(file_path, 'r', errors="ignore") as file:
        content = file.read().lower()
        words = content.split()

        if word.lower() in content:
            return file_path
        
        for w in words:
            if fuzz.ratio(w, word.lower()) > 80:
                return file_path

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
    sprint("\nWelcome to QuizMaster Terminal")
    while True:
        sprint("\n1. Play a Quiz")
        sprint("2. Make a Quiz")
        sprint("3. Quit")
        choice = input("Enter choice: ").lower()

        if choice == "3" or choice == "quit" or choice == "q" or choice == "3. quit":
            break
        elif choice == "2" or choice == "make" or choice == "make a quiz" or choice == "2. make a quiz":
            os.system("python3 quizcreator.py")
        elif choice == "1" or choice == "play" or choice == "play a quiz" or choice == "1. play a quiz":
            searchTerm = input("Enter search term for quizzes: ").lower()
            quizfiles = glob('./quizzes/**/*.json', recursive=True)
            quizfileSearchResults = []
            for file in quizfiles:
                if search_str_in_file(file, searchTerm):
                    quizfileSearchResults.append(file)

            if not quizfileSearchResults:
                sprint("No quizzes found.")
                continue

            sprint("Search Results:")
            for idx, file in enumerate(quizfileSearchResults):
                _, title = load_quiz(file)
                sprint(f"{idx + 1}. {title}")

            quiz_choice = int(input("Enter the number of the quiz you want to play: ")) - 1
            if quiz_choice < 0 or quiz_choice >= len(quizfileSearchResults):
                sprint("Invalid choice.")
                continue

            filename = quizfileSearchResults[quiz_choice]
            questions, title = load_quiz(filename)
            question_index = 0
            score = 0

            while question_index < len(questions):
                current_question = questions[question_index]
                correct_answer = current_question.correctAnswer
                wrong_answers = current_question.wrongAnswers
                answers = random.sample([correct_answer] + wrong_answers, len(wrong_answers) + 1)

                sprint(f"\nQuestion: {current_question.question}")
                for i, answer in enumerate(answers):
                    sprint(f"{i+1}. {answer}")
                user_answer = input("Select the correct answer: ")

                if user_answer.isdigit() and 1 <= int(user_answer) <= len(answers):
                    if answers[int(user_answer) - 1] == correct_answer:
                        score += 1
                else:
                    sprint("Invalid choice. Please select a valid answer.")

                question_index += 1

                if question_index >= len(questions):
                    sprint(f"Quiz completed! Your score: {score}/{len(questions)}")

    sprint("Goodbye!")

if __name__ == "__main__":
    main()
