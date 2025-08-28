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

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, Input, ListView, ListItem, Label
)
from textual.containers import Vertical
from textual.screen import Screen

from modules.persistence import QuizQuestion, search_str_in_file, load_quiz

class QuizSearchScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Enter search term for quizzes:")
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
            self.app.push_screen(PlayQuizScreen(file))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
            
class PlayQuizScreen(Screen):
    def __init__(self, quizfile):
        super().__init__()
        self.quizfile = quizfile
        self.questions = []
        self.title = ""
        self.current = 0
        self.score = 0
        self.answer_buttons = []

    def compose(self) -> ComposeResult:
        self.questions, self.title = load_quiz(self.quizfile)
        self.current = 0
        self.score = 0
        yield Header()
        yield Static(f"Quiz: {self.title}", id="quiztitle")
        self.qbox = Static("", id="question")
        yield self.qbox
        self.abox = Vertical(id="answers")
        yield self.abox
        yield Button("Back", id="back")
        yield Footer()

    def on_mount(self):
        self.update_question()

    def update_question(self):
        if self.current >= len(self.questions):
            self.qbox.update(f"Quiz completed! Your score: {self.score}/{len(self.questions)}")
            self.abox.remove_children()
            return
        q = self.questions[self.current]
        self.qbox.update(f"Question {self.current+1}: {q.question}")
        answers = random.sample([q.correctAnswer] + q.wrongAnswers, len(q.wrongAnswers)+1)
        self.abox.remove_children()
        self.answer_buttons = []
        for idx, ans in enumerate(answers):
            btn = Button(ans, id=f"answer_{self.current}_{idx}")
            btn.data = {"correct": ans == q.correctAnswer}
            self.abox.mount(btn)
            self.answer_buttons.append(btn)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id and event.button.id.startswith("answer_"):
            correct = event.button.data.get("correct", False)
            if correct:
                self.score += 1
            self.current += 1
            self.update_question()

