#!/usr/bin/env python3
import json
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

def main():
    print("Quiz Creator")
    while True:
        print("1. Open Quiz")
        print("2. Save Quiz")
        print("3. Add Question")
        print("4. Edit Question")
        print("5. Delete Question")
        print("6. Quit")
        choice = input("Enter choice: ")

        if choice == "6":
            break
        elif choice == "1":
            filename = input("Enter the quiz file to open (path to .json): ")
            with open(filename, 'r') as file:
                quizDicts = json.load(file)
                questionList.clear()
                for q in quizDicts["listOfQuestions"]:
                    qq = QuizQuestion(**q)
                    questionList.append(qq)
                print("Quiz loaded successfully.")
        elif choice == "2":
            filename = input("Enter the filename to save the quiz (path to .json): ")
            with open(filename, 'w') as file:
                quiz_name = input("Enter the title of the quiz: ")
                savedData = {"title": quiz_name, "listOfQuestions": questionList}
                json.dump(savedData, file, default=vars)
                print("Quiz saved successfully.")
        elif choice == "3":
            question = input("Enter the question: ")
            correct_answer = input("Enter the correct answer: ")
            wrong_answers = input("Enter the wrong answers (comma-separated): ").split(',')
            new_question = QuizQuestion(question, correct_answer, wrong_answers)
            questionList.append(new_question)
            print("Question added successfully.")
        elif choice == "4":
            index = int(input("Enter the index of the question to edit: "))
            if 0 <= index < len(questionList):
                question = input("Enter the new question: ")
                correct_answer = input("Enter the new correct answer: ")
                wrong_answers = input("Enter the new wrong answers (comma-separated): ").split(',')
                questionList[index] = QuizQuestion(question, correct_answer, wrong_answers)
                print("Question edited successfully.")
            else:
                print("Invalid index.")
        elif choice == "5":
            index = int(input("Enter the index of the question to delete: "))
            if 0 <= index < len(questionList):
                questionList.pop(index)
                print("Question deleted successfully.")
            else:
                print("Invalid index.")

    print("Goodbye!")

if __name__ == "__main__":
    main()
