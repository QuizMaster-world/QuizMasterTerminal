#!/usr/bin/env python3
import json
import sys
import time
from glob import glob
from fuzzywuzzy import fuzz
from dataclasses import dataclass, field
from typing import List

@dataclass
class QuizQuestion:
    question: str
    correctAnswer: str
    wrongAnswers: List[str]
    timeout: int = field(default=10)

    def __repr__(self):
        return self.question

questionList = []

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

def load_quiz(filename: str) -> List[QuizQuestion]:
    with open(filename, 'r') as file:
        quizDicts = json.load(file)
        questionList = []
        for q in quizDicts["listOfQuestions"]:
            qq = QuizQuestion(**q)
            questionList.append(qq)
    return questionList

def view_all_questions():
    if not questionList:
        sprint("\nNo questions available.")
        return
    for idx, question in enumerate(questionList):
        sprint(f"\n{idx}. {question.question}")

def main():
    sprint("\nQuiz Creator")
    while True:
        sprint("\n1. Open Quiz")
        sprint("2. Save Quiz")
        sprint("3. Add Question")
        sprint("4. Edit Question")
        sprint("5. Delete Question")
        sprint("6. View All Questions")
        sprint("7. Quit")
        choice = input("Enter choice: ").lower()

        if choice in ["7","quit","q","7. quit"]:
            break
        elif choice in ["1","open","open quiz","o","1. open quiz"]:
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
                with open(file, 'r') as f:
                    quizDicts = json.load(f)
                    title = quizDicts["title"]
                sprint(f"{idx + 1}. {title}")

            quiz_choice = int(input("Enter the number of the quiz you want to open: ")) - 1
            if quiz_choice < 0 or quiz_choice >= len(quizfileSearchResults):
                sprint("Invalid choice.")
                continue

            filename = quizfileSearchResults[quiz_choice]
            with open(filename, 'r') as file:
                quizDicts = json.load(file)
                questionList.clear()
                for q in quizDicts["listOfQuestions"]:
                    qq = QuizQuestion(**q)
                    questionList.append(qq)
                sprint("Quiz loaded successfully.")
                view_all_questions()
        elif choice in ["2","save","save quiz","s","2. save quiz"]:
            filename = ("quizzes/" + input("Enter the filename to save the quiz (path to .json): "))
            with open(filename, 'w') as file:
                quiz_name = input("Enter the title of the quiz: ")
                savedData = {"title": quiz_name, "listOfQuestions": questionList}
                json.dump(savedData, file, default=vars)
                sprint("Quiz saved successfully.")
        elif choice in ["3","add","add question","a","3. add question"]:
            question = input("Enter the question: ")
            correct_answer = input("Enter the correct answer: ")
            wrong_answers = input("Enter the wrong answers (comma-separated): ").split(',')
            new_question = QuizQuestion(question, correct_answer, wrong_answers)
            questionList.append(new_question)
            sprint("Question added successfully.")
        elif choice in ["4","edit","edit question","e","4. edit question"]:
            index = int(input("Enter the index of the question to edit: "))
            if 0 <= index < len(questionList):
                question = input("Enter the new question: ")
                correct_answer = input("Enter the new correct answer: ")
                wrong_answers = input("Enter the new wrong answers (comma-separated): ").split(',')
                questionList[index] = QuizQuestion(question, correct_answer, wrong_answers)
                sprint("Question edited successfully.")
            else:
                sprint("Invalid index.")
        elif choice == "5" or choice == "delete" or choice == "delete question" or choice == "d":
            index = int(input("Enter the index of the question to delete: "))
            if 0 <= index < len(questionList):
                questionList.pop(index)
                sprint("Question deleted successfully.")
            else:
                sprint("Invalid index.")
        elif choice == "6" or choice == "view" or choice == "view all questions" or choice == "v":
            view_all_questions()

    sprint("Goodbye!")

if __name__ == "__main__":
    main()
