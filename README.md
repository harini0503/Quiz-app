# QuizMaster - Academic Edition

A desktop quiz app built with Python, Tkinter and SQLite (standard library only, no pip installs).

## Structure
```
quiz_app/
  main.py       App window, sidebar navigation, quiz lifecycle
  pages.py      All UI pages (Home, Choose, Instructions, Quiz, Results, Review, Bank, Leaderboard, Settings)
  logic.py      QuizSession (scoring, timer) and performance messages
  database.py   Schema, seed data (30 questions) and all SQL
  theme.py      Navy / white / gold colours, fonts, ttk styles
  quiz.db       Created automatically on first run
```

## Requirements
Python 3.9 or newer with Tkinter.
- Windows / macOS (python.org installer): Tkinter is included.
- Ubuntu / Debian: `sudo apt install python3-tk`

## Run
```
cd quiz_app
python main.py        # or: python3 main.py
```
`quiz.db` is created and populated on first launch. Delete it to reset everything.

## Using the app
- **Start Quiz / Practice**: choose category, difficulty ("All" mixes levels) and question count, then set timed/untimed and a name (or Guest).
- **Keyboard**: keys 1-4 pick an answer, Left/Right move between questions, Enter goes to the next question, Tab/Space/Enter operate buttons.
- **Practice mode** shows correctness and the explanation straight after each answer.
- **Question Bank**: add, edit (or double-click) and delete questions; input is validated.
- **Leaderboard**: filter by category/difficulty, sort, and clear with confirmation.
- **Settings**: sound, timed default, seconds per question, and reset to defaults.
