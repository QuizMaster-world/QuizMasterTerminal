# QuizMasterTerminal

QuizMasterTerminal is a text-based terminal version of [QuizMasterMini](https://github.com/hermonochy/QuizMasterMini). No external requirements are needed. QuizMasterTerminal allows users to create and play quizzes directly from the terminal. It is ideal for environments where graphical interfaces are not available or desired.

## How to Use

### Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/hermonochy/QuizMasterTerminal
   ```
   
 2. Enter the directory containing the game executable:
    ```sh
    cd QuizMasterTerminal
    ```

3. Run either Quiz Creator or Quiz Game (see below).

## Quiz Game

1. In a command line window, enter `./quiz.py` for Linux, `python quiz.py` for Windows.
2. Follow the prompts in the terminal to select a quiz file (JSON format).
3. Answer the questions by typing the number corresponding to your choice.
4. At the end, your score will be displayed.

## Quiz Creator

1. In a command line window, enter `./quizcreator.py` for Linux, `python quizcreator.py` for Windows.
2. Follow the prompts to create, edit, or delete quiz questions.
3. Save your quiz to a JSON file for use in the Quiz Game.

## Features

- **Play a Quiz:** Select and play quizzes from JSON files.
- **Make a Quiz:** Create, edit, and save quizzes in JSON format.
- **Text-Based Interaction:** All interactions are handled through the terminal for simplicity and compatibility with low-storage devices.

Enjoy creating and playing quizzes with QuizMasterTerminal!
