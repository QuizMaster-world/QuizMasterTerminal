#!/usr/bin/env python3
import os
import json
import sys
import time

from typing import List
from dataclasses import dataclass, asdict, field

from fuzzywuzzy import fuzz
from glob import glob
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, Input, ListView, ListItem, Label
)
from textual.containers import Vertical
from textual.screen import Screen

from modules.persistence import *

class MakeQuizScreen(Screen):
    def __init__(self):
        super().__init__()
        self.questions: List[QuizQuestion] = []
        self.quiz_title = ""
        self.quiz_filename = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Quiz Creator", id="heading")
        yield Button("Load Quiz", id="load")
        yield Button("Add Question", id="addq")
        yield Button("Edit Question", id="editq")
        yield Button("Save Quiz", id="save")
        yield ListView(id="qlist")
        yield Button("Back", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
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
        yield Static("Enter search term for quiz to load:")
        yield Input(placeholder="Search...", id="search")
        yield ListView(id="quizlist")
        yield Button("Back", id="back")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        search_term = event.value.strip()
        quizfiles = glob('./Quizzes/**/*.json', recursive=True)
        results = []
        for file in quizfiles:
            if search_str_in_file(file, search_term):
                results.append(file)
        quizlist = self.query_one("#quizlist", ListView)
        quizlist.clear()
        if not results:
            quizlist.append(ListItem(Label("No quizzes found."), id="none"))
        else:
            for idx, file in enumerate(results):
                _, title = load_quiz(file)
                item = ListItem(Label(f"{title}"), id=f"quiz_{idx}")
                item.data = {"file": file}
                quizlist.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if not hasattr(event.item, "data") or not isinstance(event.item.data, dict):
            return
        file = event.item.data.get("file")
        if file:
            questions, title = load_quiz(file)
            self._owner.set_questions_and_title(questions, title)
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
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

class SaveQuizScreen(Screen):
    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Save Quiz")
        yield Input(placeholder="Quiz title...", id="title")
        yield Input(placeholder="Filename (e.g., Quizzes/myquiz.json)", id="filename")
        yield Button("Save", id="save")
        yield Button("Back", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            title = self.query_one("#title", Input).value.strip()
            filename = self.query_one("#filename", Input).value.strip()
            if title and filename:
                save_quiz(filename, title, self._owner.questions)
                self._owner.quiz_title = title
                self._owner.quiz_filename = filename
                self.app.pop_screen()
        elif event.button.id == "back":
            self.app.pop_screen()
