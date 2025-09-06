#!/usr/bin/env python3
import os
from typing import List
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, Input, ListView, ListItem, Label, DirectoryTree
)
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

from modules.persistence import QuizQuestion, save_quiz, load_quiz

QUIZ_DIR = "./Quizzes" 

class MakeQuizScreen(Screen):
    def __init__(self):
        super().__init__()
        self.questions: List[QuizQuestion] = []
        self.quiz_title = ""
        self.quiz_filename = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static("Quiz Creator", id="heading")
            yield Input(value=self.quiz_title, placeholder="Quiz Title...", id="quiz_title")
        yield ListView(id="qlist")
        with Horizontal():
            yield Button("Add Question", id="addq")
            yield Button("Edit Question", id="editq")
            yield Button("Delete Question", id="delq")
        with Horizontal():
            yield Button("Load Quiz", id="load")
            yield Button("Save Quiz", id="save")
        with Horizontal():
            yield Button("Back", id="back")
        yield Footer()

    def on_mount(self):
        self.refresh_list()

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "quiz_title":
            self.quiz_title = event.value.strip()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "load":
            self.app.push_screen(LoadQuizScreen(self))
        elif event.button.id == "addq":
            self.app.push_screen(AddQuestionScreen(self))
        elif event.button.id == "editq":
            qlist = self.query_one("#qlist", ListView)
            idx = qlist.index
            if idx is not None and 0 <= idx < len(self.questions):
                question = self.questions[idx]
                self.app.push_screen(EditQuestionScreen(self, idx, question))
        elif event.button.id == "delq":
            qlist = self.query_one("#qlist", ListView)
            idx = qlist.index
            if idx is not None and 0 <= idx < len(self.questions):
                del self.questions[idx]
                self.refresh_list()
        elif event.button.id == "save":
            self.app.push_screen(SaveQuizScreen(self))

    def add_question(self, question: QuizQuestion):
        self.questions.append(question)
        self.refresh_list()
        
    def edit_question(self, idx, question: QuizQuestion):
        self.questions[idx] = question
        self.refresh_list()

    def set_questions_and_title(self, questions, title):
        self.questions = questions
        self.quiz_title = title
        self.refresh_list()
        self.query_one("#quiz_title", Input).value = title

    def refresh_list(self):
        qlist = self.query_one("#qlist", ListView)
        qlist.clear()
        for idx, q in enumerate(self.questions):
            qlist.append(ListItem(Label(f"{idx+1}. {q.question}")))

class LoadQuizScreen(Screen):
    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Select a quiz to load (tree or path):")
        with Horizontal():
            yield DirectoryTree(QUIZ_DIR, id="dir_tree")
            with Vertical():
                yield Input(placeholder="Or enter quiz path...", id="path_input")
                yield ListView(id="quizlist")
        yield Button("Back", id="back")
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        path = event.path
        if os.path.isfile(path) and str(path).endswith('.json'):
            try:
                questions, title = load_quiz(path)
                self._owner.set_questions_and_title(questions, title)
                self.app.pop_screen()
            except Exception as e:
                self.query_one("#quizlist", ListView).clear()
                self.query_one("#quizlist", ListView).append(ListItem(Label(f"Failed to load: {e}")))
                self.query_one("#path_input", Input).value = str(path)

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "path_input":
            path = event.value.strip()
            if os.path.isfile(path):
                try:
                    questions, title = load_quiz(path)
                    self._owner.set_questions_and_title(questions, title)
                    self.app.pop_screen()
                except Exception as e:
                    self.query_one("#quizlist", ListView).clear()
                    self.query_one("#quizlist", ListView).append(ListItem(Label(f"Failed to load: {e}")))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.app.pop_screen()

class SaveQuizScreen(Screen):
    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Save Quiz")
        with Horizontal():
            yield DirectoryTree(QUIZ_DIR, id="dir_tree")
            with Vertical():
                yield Input(value=self._owner.quiz_title, placeholder="Quiz title...", id="title")
                yield Input(placeholder="Filename (e.g., Quizzes/myquiz.json)", id="filename")
        yield Button("Save", id="save")
        yield Button("Back", id="back")
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        path = event.path
        if os.path.isdir(path):
            self.query_one("#filename", Input).value = os.path.join(path, "myquiz.json")
        elif str(path).endswith('.json'):
            self.query_one("#filename", Input).value = str(path)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save":
            title = self.query_one("#title", Input).value.strip()
            filename = self.query_one("#filename", Input).value.strip()
            if title and filename:
                try:
                    save_quiz(filename, title, self._owner.questions)
                    self._owner.quiz_title = title
                    self._owner.quiz_filename = filename
                    self.app.pop_screen()
                except Exception as e:
                    pass
        elif event.button.id == "back":
            self.app.pop_screen()

class AddQuestionScreen(Screen):
    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Add a New Question")
        yield Input(placeholder="Question...", id="question")
        yield Input(placeholder="Correct answer...", id="correct")
        yield Input(placeholder="Wrong answers (comma separated)...", id="wrong")
        yield Button("Add", id="add")
        yield Button("Back", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add":
            question = self.query_one("#question", Input).value.strip()
            correct = self.query_one("#correct", Input).value.strip()
            wrong = self.query_one("#wrong", Input).value.strip()
            if question and correct and wrong:
                wrong_answers = [a.strip() for a in wrong.split(",") if a.strip()]
                q = QuizQuestion(question, correct, wrong_answers)
                self._owner.add_question(q)
                self.app.pop_screen()
        elif event.button.id == "back":
            self.app.pop_screen()

class EditQuestionScreen(Screen):
    def __init__(self, owner, qidx, question: QuizQuestion):
        super().__init__()
        self._owner = owner
        self._qidx = qidx
        self._original = question

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Edit Question")
        yield Input(value=self._original.question, placeholder="Question...", id="question")
        yield Input(value=self._original.correctAnswer, placeholder="Correct answer...", id="correct")
        yield Input(value=", ".join(self._original.wrongAnswers), placeholder="Wrong answers (comma separated)...", id="wrong")
        yield Button("Save", id="save")
        yield Button("Back", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save":
            question = self.query_one("#question", Input).value.strip()
            correct = self.query_one("#correct", Input).value.strip()
            wrong = self.query_one("#wrong", Input).value.strip()
            if question and correct and wrong:
                wrong_answers = [a.strip() for a in wrong.split(",") if a.strip()]
                q = QuizQuestion(question, correct, wrong_answers)
                self._owner.edit_question(self._qidx, q)
                self.app.pop_screen()
        elif event.button.id == "back":
            self.app.pop_screen()

class QuizCreatorApp(App):
    CSS = """
    #heading { text-align: center; padding: 1 0;}
    ListView { height: 9;}
    DirectoryTree { min-width: 40; max-width: 48; height: 16; }
    Input { margin: 0 1;}
    """
    TITLE = "QuizMaster Terminal - Quiz Creator"

    def on_mount(self):
        self.push_screen(MakeQuizScreen())

if __name__ == '__main__':
    QuizCreatorApp().run()