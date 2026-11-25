
"""QuizMaster entry point: window, sidebar navigation and quiz-session wiring."""
import sqlite3
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from logic import QuizSession
from pages import (HomePage, ChoosePage, InstructionsPage, QuizPage, ResultsPage, ReviewPage,
                   BankPage, BoardPage, SettingsPage)
from theme import *


class App(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("QuizMaster - Academic Edition")
        self.geometry("1020x700"); self.minsize(940, 640); self.configure(bg=BG)
        setup_styles(self)
        self.setup = {"category": "Python", "difficulty": "Easy", "count": 5, "practice": False}
        self.session = self.last_result = None
        self.current, self._banner_job = None, None

        side = tk.Frame(self, bg=NAVY, width=214); side.pack(side="left", fill="y"); side.pack_propagate(False)
        tk.Label(side, text="QuizMaster", bg=NAVY, fg=GOLD, font=(FONT, 20, "bold")).pack(pady=(26, 0))
        tk.Label(side, text="ACADEMIC EDITION", bg=NAVY, fg=WHITE, font=SMALL).pack()
        tk.Frame(side, bg=GOLD, height=2).pack(fill="x", padx=18, pady=16)
        for text, name in (("Home", "home"), ("Start Quiz", "quiz_setup"), ("Practice", "practice_setup"),
                           ("Question Bank", "bank"), ("Leaderboard", "board"), ("Settings", "settings")):
            ttk.Button(side, text=text, style="TButton", command=lambda n=name: self.navigate(n)).pack(fill="x", padx=14, pady=3)

        right = ttk.Frame(self); right.pack(side="left", fill="both", expand=True)
        self.banner = tk.Label(right, text="", font=BODY, anchor="w", padx=16, pady=7, bg=BG)
        self.banner.pack(side="bottom", fill="x")
        self.content = ttk.Frame(right); self.content.pack(fill="both", expand=True)
        self.pages = {n: cls(self) for n, cls in (
            ("home", HomePage), ("choose", ChoosePage), ("instructions", InstructionsPage), ("quiz", QuizPage),
            ("results", ResultsPage), ("review", ReviewPage), ("bank", BankPage), ("board", BoardPage),
            ("settings", SettingsPage))}
        self.show("home")

    # ---- navigation ----
    def show(self, name, **kw):
        if self.current: self.pages[self.current].on_hide(); self.pages[self.current].pack_forget()
        self.current = name
        self.pages[name].pack(fill="both", expand=True)
        self.pages[name].on_show(**kw)

    def navigate(self, name):
        """Sidebar navigation; asks before abandoning a quiz in progress."""
        if self.current == "quiz" and self.session and not self.session.finished:
            if not messagebox.askyesno("Leave quiz?", "Your current quiz progress will be lost. Leave anyway?", icon="warning"):
                return
        if name in ("quiz_setup", "practice_setup"): return self.begin_setup(name == "practice_setup")
        self.show(name)

    def begin_setup(self, practice):
        self.setup["practice"] = practice
        self.show("choose")

    # ---- quiz lifecycle ----
    def start_session(self, name, timed):
        s = self.setup
        qs = self.db.get_questions(s["category"], s["difficulty"], s["count"])
        if not qs:
            return self.flash("No questions available for this selection.", "err")
        spq = int(self.db.get_setting("seconds_per_question") or 30)
        self._last_start = (name, timed)
        self.session = QuizSession(qs, s["category"], s["difficulty"], name, s["practice"], timed, spq)
        self.show("quiz")

    def retry(self):
        self.start_session(*self._last_start)

    def finish_quiz(self):
        self.last_result = self.session.finish()
        try:
            self.db.add_result(self.last_result)
            self.flash("Quiz submitted and your result was saved.", "ok")
        except sqlite3.Error as e:
            self.flash(f"Quiz finished, but the result could not be saved: {e}", "err")
        self.play_sound("ok")
        self.show("results")

    # ---- helpers ----
    def flash(self, msg, kind="info"):
        bg, fg = BANNERS[kind]
        self.banner.config(text=msg, bg=bg, fg=fg)
        if self._banner_job: self.after_cancel(self._banner_job)
        self._banner_job = self.after(5000, lambda: self.banner.config(text="", bg=BG))

    def play_sound(self, kind):
        if self.db.get_setting("sound") != "1": return
        try:
            import winsound
            winsound.Beep({"ok": 880, "err": 330}.get(kind, 600), 110)
        except ImportError:
            self.bell()


def main():
    try:
        db = Database()          # creates and seeds quiz.db automatically when missing
    except (sqlite3.Error, OSError) as e:
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Database error", f"Could not open the quiz database:\n{e}")
        sys.exit(1)
    App(db).mainloop()


if __name__ == "__main__":
    main()
