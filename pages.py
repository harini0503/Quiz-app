"""All UI pages. Pages only talk to the App (navigation/session) and Database."""
import tkinter as tk
from tkinter import ttk, messagebox

from database import CATEGORIES, DIFFICULTIES
from logic import performance_message
from theme import *


class Page(ttk.Frame):
    def __init__(self, app):
        super().__init__(app.content, padding=28)
        self.app, self.db = app, app.db

    def header(self, text, sub=None):
        ttk.Label(self, text=text, style="H1.TLabel").pack(anchor="w")
        tk.Frame(self, bg=GOLD, height=3, width=70).pack(anchor="w", pady=(4, 10))
        if sub:
            ttk.Label(self, text=sub, wraplength=700, justify="left").pack(anchor="w", pady=(0, 12))

    def card(self, **pack):
        f = ttk.Frame(self, style="Card.TFrame", padding=20)
        f.pack(**({"fill": "x"} | pack))
        return f

    def on_show(self, **kw): pass
    def on_hide(self): pass


def labeled_combo(parent, row, label, var, values, cmd=None, width=24, lstyle="Card.TLabel"):
    ttk.Label(parent, text=label, style=lstyle).grid(row=row, column=0, sticky="w", pady=8, padx=(0, 16))
    cb = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", width=width, font=BODY)
    cb.grid(row=row, column=1, sticky="w")
    if cmd: cb.bind("<<ComboboxSelected>>", lambda e: cmd())
    return cb


# ------------------------------------------------------------------ Home
class HomePage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Welcome to QuizMaster",
                    "Test your knowledge across Python, General Knowledge, Science, Mathematics and History. "
                    "Take a scored quiz, practise with instant feedback, and climb the leaderboard.")
        self.stats = ttk.Label(self, style="Card.TLabel", padding=16, wraplength=640)
        self.stats.pack(fill="x", pady=(0, 18))
        row = ttk.Frame(self); row.pack(anchor="w")
        items = [("Start Quiz", lambda: app.begin_setup(False), "Gold.TButton"),
                 ("Practice", lambda: app.begin_setup(True), "TButton"),
                 ("Categories", lambda: app.show("bank"), "TButton"),
                 ("Leaderboard", lambda: app.show("board"), "TButton"),
                 ("Settings", lambda: app.show("settings"), "TButton")]
        for i, (t, c, st) in enumerate(items):
            ttk.Button(row, text=t, command=c, style=st, width=16).grid(row=i // 3, column=i % 3, padx=6, pady=6)

    def on_show(self, **kw):
        last, streak = self.db.recent_stats()
        if last:
            self.stats.config(text=f"Latest score: {last['score']}/{last['total']} ({last['percent']:.0f}%) in "
                                   f"{last['category']} - {last['difficulty']}\nPass streak (60%+): {streak} quiz(zes)")
        else:
            self.stats.config(text="No quizzes taken yet. Start your first quiz to see your progress here.")


# ------------------------------------------------------------------ Choose
class ChoosePage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Choose Your Quiz")
        self.mode_lbl = ttk.Label(self, style="H2.TLabel"); self.mode_lbl.pack(anchor="w", pady=(0, 8))
        c = self.card()
        self.cat, self.diff = tk.StringVar(value=CATEGORIES[0]), tk.StringVar(value="Easy")
        labeled_combo(c, 0, "Category", self.cat, CATEGORIES, self.refresh)
        labeled_combo(c, 1, "Difficulty", self.diff, DIFFICULTIES + ["All"], self.refresh)
        ttk.Label(c, text="Number of questions", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=8)
        self.spin = ttk.Spinbox(c, from_=1, to=1, width=8, font=BODY); self.spin.grid(row=2, column=1, sticky="w")
        self.avail = ttk.Label(c, style="Card.TLabel", foreground=NAVY); self.avail.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        row = ttk.Frame(self); row.pack(anchor="w", pady=16)
        ttk.Button(row, text="Continue", style="Gold.TButton", command=self.proceed).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Home", command=lambda: app.show("home")).pack(side="left")

    def on_show(self, **kw):
        s = self.app.setup
        self.cat.set(s["category"]); self.diff.set(s["difficulty"])
        self.mode_lbl.config(text="Practice Mode" if s["practice"] else "Scored Quiz")
        self.refresh(); self.spin.set(min(s["count"], max(1, self.n)))

    def refresh(self):
        self.n = self.db.count(self.cat.get(), self.diff.get())
        self.avail.config(text=f"{self.n} question(s) available for this selection.")
        self.spin.config(to=max(1, self.n))
        if self.spin.get().isdigit() and int(self.spin.get()) > max(1, self.n): self.spin.set(max(1, self.n))

    def proceed(self):
        if self.n == 0:
            return self.app.flash("No questions match this selection. Choose another or add some in Categories.", "warn")
        try:
            count = int(self.spin.get())
        except ValueError:
            return self.app.flash("Enter a whole number of questions.", "err")
        if not 1 <= count <= self.n:
            return self.app.flash(f"Choose between 1 and {self.n} questions.", "warn")
        self.app.setup.update(category=self.cat.get(), difficulty=self.diff.get(), count=count)
        self.app.show("instructions")


# ------------------------------------------------------------------ Instructions
class InstructionsPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Quiz Instructions")
        c = self.card()
        rules = ("1.  Each question has four options; exactly one is correct.\n"
                 "2.  Use Previous / Next to move around and change answers before submitting.\n"
                 "3.  Keyboard: keys 1-4 select an answer, Left/Right arrows navigate, Enter goes next.\n"
                 "4.  In Practice mode you get instant feedback after each answer.\n"
                 "5.  In timed mode the quiz submits automatically when time runs out.")
        ttk.Label(c, text=rules, style="Card.TLabel", justify="left").pack(anchor="w")
        d = self.card(pady=12)
        self.timed = tk.BooleanVar()
        ttk.Checkbutton(d, text="Timed mode", variable=self.timed, style="Card.TCheckbutton", command=self.info).pack(anchor="w")
        self.limit_lbl = ttk.Label(d, style="Card.TLabel"); self.limit_lbl.pack(anchor="w", pady=4)
        r = ttk.Frame(d, style="Card.TFrame"); r.pack(anchor="w", pady=6)
        ttk.Label(r, text="Display name", style="Card.TLabel").pack(side="left", padx=(0, 10))
        self.name = ttk.Entry(r, width=26, font=BODY); self.name.pack(side="left")
        row = ttk.Frame(self); row.pack(anchor="w", pady=8)
        ttk.Button(row, text="Begin Quiz", style="Gold.TButton", command=lambda: self.begin(False)).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Play as Guest", command=lambda: self.begin(True)).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Back", command=lambda: app.show("choose")).pack(side="left")
        self.name.bind("<Return>", lambda e: self.begin(False))

    def info(self):
        spq = int(self.db.get_setting("seconds_per_question") or 30)
        n = self.app.setup["count"]
        self.limit_lbl.config(text=f"Time limit: {spq * n} seconds ({spq}s per question)." if self.timed.get() else "Untimed: take as long as you need.")

    def on_show(self, **kw):
        self.timed.set(self.db.get_setting("timed_default") == "1")
        self.name.delete(0, "end"); self.name.insert(0, self.db.get_setting("player_name"))
        self.info(); self.name.focus_set()

    def begin(self, guest):
        name = "Guest" if guest else self.name.get().strip()
        if not name:
            return self.app.flash("Enter a display name or choose Play as Guest.", "warn")
        if len(name) > 24:
            return self.app.flash("Display name must be 24 characters or fewer.", "err")
        self.db.set_setting("player_name", name)
        self.app.start_session(name, self.timed.get())


# ------------------------------------------------------------------ Quiz
class QuizPage(Page):
    KEYS = ["<Key-1>", "<Key-2>", "<Key-3>", "<Key-4>", "<Left>", "<Right>", "<Return>"]

    def __init__(self, app):
        super().__init__(app)
        self._timer = None
        top = ttk.Frame(self); top.pack(fill="x")
        self.lbl_q = ttk.Label(top, style="H2.TLabel"); self.lbl_q.pack(side="left")
        self.lbl_timer = ttk.Label(top, font=(FONT, 13, "bold"), foreground=NAVY); self.lbl_timer.pack(side="right")
        self.lbl_score = ttk.Label(top); self.lbl_score.pack(side="right", padx=24)
        self.bar = ttk.Progressbar(self, maximum=100); self.bar.pack(fill="x", pady=10)
        c = self.card(fill="both", expand=True)
        self.question = ttk.Label(c, style="Q.TLabel", wraplength=640, justify="left"); self.question.pack(anchor="w", pady=(0, 12))
        self.choice = tk.IntVar(value=-1)
        self.opts = [ttk.Radiobutton(c, style="Opt.TRadiobutton", variable=self.choice, value=i, command=self.on_choose) for i in range(4)]
        for o in self.opts: o.pack(anchor="w", fill="x")
        self.feedback = ttk.Label(c, style="Card.TLabel", wraplength=640, justify="left"); self.feedback.pack(anchor="w", pady=(12, 0))
        nav = ttk.Frame(self); nav.pack(fill="x", pady=(12, 0))
        self.b_prev = ttk.Button(nav, text="Previous", command=lambda: self.move(-1)); self.b_prev.pack(side="left")
        self.b_next = ttk.Button(nav, text="Next", command=lambda: self.move(1)); self.b_next.pack(side="left", padx=8)
        ttk.Button(nav, text="Submit", style="Gold.TButton", command=self.finish).pack(side="right")

    def on_show(self, **kw):
        self.app.session.index = 0
        self.render()
        for i in range(4):
            self.app.bind(self.KEYS[i], lambda e, i=i: self.key_choose(i))
        self.app.bind("<Left>", lambda e: self.move(-1)); self.app.bind("<Right>", lambda e: self.move(1))
        self.app.bind("<Return>", lambda e: self.move(1))
        self.tick()

    def on_hide(self):
        if self._timer: self.after_cancel(self._timer); self._timer = None
        for k in self.KEYS: self.app.unbind(k)

    def render(self):
        s = self.app.session; q = s.current()
        self.lbl_q.config(text=f"Question {s.index + 1} of {s.total}")
        self.question.config(text=q["text"])
        for i, o in enumerate(self.opts): o.config(text=f"{'ABCD'[i]}.   {q['options'][i]}")
        a = s.answers[s.index]
        self.choice.set(-1 if a is None else a)
        self.feedback.config(text="")
        if s.practice and a is not None: self.show_feedback()
        self.b_prev.state(["!disabled" if s.index > 0 else "disabled"])
        self.b_next.state(["!disabled" if s.index < s.total - 1 else "disabled"])
        self.update_progress()

    def update_progress(self):
        s = self.app.session
        self.bar["value"] = 100 * s.answered() / s.total
        self.lbl_score.config(text=f"Answered {s.answered()}/{s.total}  |  Score {s.score()}")

    def key_choose(self, i):
        self.choice.set(i); self.on_choose()

    def on_choose(self):
        s = self.app.session
        s.answer(self.choice.get()); self.update_progress()
        if s.practice:
            self.show_feedback()
            self.app.play_sound("ok" if s.is_correct(s.index) else "err")

    def show_feedback(self):
        s = self.app.session; q = s.current()
        if s.is_correct(s.index):
            self.feedback.config(text=f"Correct! {q['explanation']}", foreground=OK)
        else:
            self.feedback.config(text=f"Incorrect. Correct answer: {q['options'][q['correct']]}. {q['explanation']}", foreground=ERR)

    def move(self, d):
        s = self.app.session
        if 0 <= s.index + d < s.total:
            s.index += d; self.render()

    def tick(self):
        s = self.app.session
        if s is None or s.finished: return
        rem = s.remaining()
        if rem is None:
            self.lbl_timer.config(text="Untimed")
        else:
            self.lbl_timer.config(text=f"Time {rem // 60:02d}:{rem % 60:02d}", foreground=ERR if rem <= 15 else NAVY)
            if rem <= 0:
                self.app.flash("Time is up - your answers were submitted automatically.", "warn")
                return self.app.finish_quiz()
        self._timer = self.after(500, self.tick)

    def finish(self):
        s = self.app.session
        left = s.unanswered()
        msg = (f"{left} question(s) are unanswered and will be marked incorrect.\n\nSubmit anyway?" if left
               else "Submit your final answers?")
        if messagebox.askyesno("Confirm submission", msg, icon="warning" if left else "question"):
            self.app.finish_quiz()


# ------------------------------------------------------------------ Results
class ResultsPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Quiz Results")
        c = self.card()
        self.big = ttk.Label(c, style="Big.TLabel"); self.big.pack(anchor="w")
        self.detail = ttk.Label(c, style="Card.TLabel", justify="left"); self.detail.pack(anchor="w", pady=8)
        self.msg = ttk.Label(c, style="Card.TLabel", foreground=NAVY, font=(FONT, 12, "bold"), wraplength=640); self.msg.pack(anchor="w")
        row = ttk.Frame(self); row.pack(anchor="w", pady=16)
        ttk.Button(row, text="Review Answers", style="Gold.TButton", command=lambda: app.show("review")).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Try Again", command=app.retry).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Home", command=lambda: app.show("home")).pack(side="left")

    def on_show(self, **kw):
        r = self.app.last_result
        self.big.config(text=f"{r['score']} / {r['total']}   ({r['percent']:.0f}%)")
        self.detail.config(text=f"Correct: {r['correct']}    Incorrect: {r['incorrect']}    Unanswered: {r['unanswered']}\n"
                                f"Time taken: {r['seconds'] // 60}m {r['seconds'] % 60:02d}s    Mode: {r['mode']}    "
                                f"{r['category']} - {r['difficulty']}")
        self.msg.config(text=performance_message(r["percent"]))


# ------------------------------------------------------------------ Review
class ReviewPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Answer Review")
        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True)
        self.text = tk.Text(wrap, wrap="word", font=BODY, bg=WHITE, relief="flat", padx=14, pady=10, state="disabled")
        sb = ttk.Scrollbar(wrap, command=self.text.yview); self.text.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self.text.pack(fill="both", expand=True)
        self.text.tag_config("q", font=(FONT, 12, "bold"), foreground=NAVY, spacing1=14)
        self.text.tag_config("ok", foreground=OK); self.text.tag_config("bad", foreground=ERR)
        self.text.tag_config("exp", foreground="#55607A", font=(FONT, 10, "italic"))
        row = ttk.Frame(self); row.pack(anchor="w", pady=(10, 0))
        ttk.Button(row, text="Back to Results", command=lambda: app.show("results")).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Home", command=lambda: app.show("home")).pack(side="left")

    def on_show(self, **kw):
        s = self.app.session
        t = self.text; t.config(state="normal"); t.delete("1.0", "end")
        for i, q in enumerate(s.questions):
            a = s.answers[i]
            t.insert("end", f"Q{i + 1}. {q['text']}\n", "q")
            if a is None:
                t.insert("end", "   Your answer: (not answered)  [INCORRECT]\n", "bad")
            elif a == q["correct"]:
                t.insert("end", f"   Your answer: {q['options'][a]}  [CORRECT]\n", "ok")
            else:
                t.insert("end", f"   Your answer: {q['options'][a]}  [INCORRECT]\n", "bad")
            if a != q["correct"]:
                t.insert("end", f"   Correct answer: {q['options'][q['correct']]}\n", "ok")
            t.insert("end", f"   {q['explanation']}\n", "exp")
        t.config(state="disabled"); t.yview_moveto(0)


# ------------------------------------------------------------------ Question bank
class QuestionDialog(tk.Toplevel):
    """Modal add/edit form with validation."""
    def __init__(self, page, question=None):
        super().__init__(page); self.page, self.q = page, question
        self.title("Edit Question" if question else "Add Question")
        self.configure(bg=BG, padx=20, pady=16); self.transient(page); self.resizable(False, False)
        f = ttk.Frame(self); f.pack()
        self.cat = tk.StringVar(value=question["category"] if question else CATEGORIES[0])
        self.diff = tk.StringVar(value=question["difficulty"] if question else "Easy")
        labeled_combo(f, 0, "Category", self.cat, CATEGORIES, lstyle="TLabel")
        labeled_combo(f, 1, "Difficulty", self.diff, DIFFICULTIES, lstyle="TLabel")
        ttk.Label(f, text="Question").grid(row=2, column=0, sticky="nw", pady=6)
        self.text = tk.Text(f, width=52, height=3, font=BODY, wrap="word"); self.text.grid(row=2, column=1, pady=6)
        self.correct = tk.IntVar(value=question["correct"] if question else -1)
        self.opts = []
        for i in range(4):
            ttk.Label(f, text=f"Option {'ABCD'[i]}").grid(row=3 + i, column=0, sticky="w", pady=3)
            r = ttk.Frame(f); r.grid(row=3 + i, column=1, sticky="w")
            e = ttk.Entry(r, width=46, font=BODY); e.pack(side="left"); self.opts.append(e)
            ttk.Radiobutton(r, variable=self.correct, value=i).pack(side="left", padx=6)
        ttk.Label(f, text="(select the radio button beside the correct option)", font=SMALL).grid(row=7, column=1, sticky="w")
        ttk.Label(f, text="Explanation").grid(row=8, column=0, sticky="nw", pady=6)
        self.expl = tk.Text(f, width=52, height=2, font=BODY, wrap="word"); self.expl.grid(row=8, column=1, pady=6)
        if question:
            self.text.insert("1.0", question["text"]); self.expl.insert("1.0", question["explanation"])
            for e, v in zip(self.opts, question["options"]): e.insert(0, v)
        self.err = tk.Label(self, fg=ERR, bg=BG, font=BODY, wraplength=480); self.err.pack(pady=4)
        r = ttk.Frame(self); r.pack()
        ttk.Button(r, text="Save", style="Gold.TButton", command=self.save).pack(side="left", padx=6)
        ttk.Button(r, text="Cancel", command=self.destroy).pack(side="left")
        self.grab_set(); self.text.focus_set()

    def save(self):
        text, expl = self.text.get("1.0", "end").strip(), self.expl.get("1.0", "end").strip()
        opts = [e.get().strip() for e in self.opts]
        problem = None
        if len(text) < 10: problem = "Question text must be at least 10 characters."
        elif not all(opts): problem = "All four answer options are required."
        elif len({o.lower() for o in opts}) < 4: problem = "Answer options must all be different."
        elif self.correct.get() not in range(4): problem = "Select which option is correct."
        elif not expl: problem = "Please add a brief explanation."
        if problem: return self.err.config(text=problem)
        data = {"category": self.cat.get(), "difficulty": self.diff.get(), "text": text, "options": opts,
                "correct": self.correct.get(), "explanation": expl}
        self.page.db.save_question(data, self.q["id"] if self.q else None)
        self.page.app.flash("Question saved successfully.", "ok")
        self.destroy(); self.page.reload()


class BankPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Categories & Question Bank")
        f = ttk.Frame(self); f.pack(fill="x", pady=(0, 8))
        self.cat, self.diff = tk.StringVar(value="All"), tk.StringVar(value="All")
        ttk.Label(f, text="Category").pack(side="left")
        ttk.Combobox(f, textvariable=self.cat, values=["All"] + CATEGORIES, state="readonly", width=18).pack(side="left", padx=(6, 16))
        ttk.Label(f, text="Difficulty").pack(side="left")
        ttk.Combobox(f, textvariable=self.diff, values=["All"] + DIFFICULTIES, state="readonly", width=10).pack(side="left", padx=6)
        for w in f.winfo_children():
            if isinstance(w, ttk.Combobox): w.bind("<<ComboboxSelected>>", lambda e: self.reload())
        self.count = ttk.Label(f); self.count.pack(side="right")
        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(wrap, columns=("cat", "diff", "text"), show="headings", selectmode="browse")
        for c, t, w in (("cat", "Category", 130), ("diff", "Difficulty", 80), ("text", "Question", 420)):
            self.tree.heading(c, text=t); self.tree.column(c, width=w, anchor="w")
        sb = ttk.Scrollbar(wrap, command=self.tree.yview); self.tree.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.edit())
        row = ttk.Frame(self); row.pack(anchor="w", pady=(10, 0))
        ttk.Button(row, text="Add", style="Gold.TButton", command=lambda: QuestionDialog(self)).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Edit", command=self.edit).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Delete", style="Danger.TButton", command=self.delete).pack(side="left")
        self.rows = {}

    def on_show(self, **kw): self.reload()

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        qs = self.db.get_questions(self.cat.get(), self.diff.get(), shuffle=False)
        self.rows = {str(q["id"]): q for q in qs}
        for q in qs:
            self.tree.insert("", "end", iid=str(q["id"]), values=(q["category"], q["difficulty"], q["text"]))
        self.count.config(text=f"{len(qs)} question(s)")

    def selected(self):
        sel = self.tree.selection()
        if not sel: self.app.flash("Select a question first.", "warn"); return None
        return self.rows[sel[0]]

    def edit(self):
        q = self.selected()
        if q: QuestionDialog(self, q)

    def delete(self):
        q = self.selected()
        if q and messagebox.askyesno("Delete question", "Permanently delete this question?", icon="warning"):
            self.db.delete_question(q["id"]); self.reload(); self.app.flash("Question deleted.", "ok")


# ------------------------------------------------------------------ Leaderboard
class BoardPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Leaderboard")
        f = ttk.Frame(self); f.pack(fill="x", pady=(0, 8))
        self.cat, self.diff, self.sort = tk.StringVar(value="All"), tk.StringVar(value="All"), tk.StringVar(value="Highest score")
        for label, var, vals, w in (("Category", self.cat, ["All"] + CATEGORIES, 17), ("Difficulty", self.diff, ["All"] + DIFFICULTIES, 9),
                                    ("Sort by", self.sort, ["Highest score", "Most recent", "Fastest"], 13)):
            ttk.Label(f, text=label).pack(side="left", padx=(8, 4))
            cb = ttk.Combobox(f, textvariable=var, values=vals, state="readonly", width=w); cb.pack(side="left")
            cb.bind("<<ComboboxSelected>>", lambda e: self.reload())
        cols = (("rank", "#", 36), ("name", "Name", 100), ("cat", "Category", 120), ("diff", "Level", 70),
                ("score", "Score", 60), ("pct", "%", 50), ("time", "Time", 60), ("date", "Date", 120))
        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(wrap, columns=[c[0] for c in cols], show="headings")
        for c, t, w in cols: self.tree.heading(c, text=t); self.tree.column(c, width=w, anchor="w")
        sb = ttk.Scrollbar(wrap, command=self.tree.yview); self.tree.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self.tree.pack(fill="both", expand=True)
        self.empty = ttk.Label(self); self.empty.pack(anchor="w", pady=6)
        ttk.Button(self, text="Clear Results", style="Danger.TButton", command=self.clear).pack(anchor="w")

    def on_show(self, **kw): self.reload()

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.db.leaderboard(self.cat.get(), self.diff.get(), self.sort.get())
        for i, r in enumerate(rows, 1):
            self.tree.insert("", "end", values=(i, r["name"], r["category"], r["difficulty"], f"{r['score']}/{r['total']}",
                             f"{r['percent']:.0f}", f"{r['seconds'] // 60}:{r['seconds'] % 60:02d}", r["taken_at"]))
        self.empty.config(text="" if rows else "No results to show for this filter yet.")

    def clear(self):
        if messagebox.askyesno("Clear results", "Delete ALL saved quiz results? This cannot be undone.", icon="warning"):
            self.db.clear_results(); self.reload(); self.app.flash("All results cleared.", "ok")


# ------------------------------------------------------------------ Settings
class SettingsPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.header("Settings")
        c = self.card()
        self.sound, self.timed, self.secs = tk.BooleanVar(), tk.BooleanVar(), tk.StringVar()
        ttk.Checkbutton(c, text="Enable sound effects", variable=self.sound, style="Card.TCheckbutton").pack(anchor="w", pady=6)
        ttk.Checkbutton(c, text="Timed mode by default", variable=self.timed, style="Card.TCheckbutton").pack(anchor="w", pady=6)
        r = ttk.Frame(c, style="Card.TFrame"); r.pack(anchor="w", pady=6)
        ttk.Label(r, text="Seconds per question (5-300)", style="Card.TLabel").pack(side="left", padx=(0, 10))
        ttk.Spinbox(r, from_=5, to=300, increment=5, textvariable=self.secs, width=6, font=BODY).pack(side="left")
        row = ttk.Frame(self); row.pack(anchor="w", pady=16)
        ttk.Button(row, text="Save Settings", style="Gold.TButton", command=self.save).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Reset Preferences", style="Danger.TButton", command=self.reset).pack(side="left")

    def on_show(self, **kw):
        self.sound.set(self.db.get_setting("sound") == "1"); self.timed.set(self.db.get_setting("timed_default") == "1")
        self.secs.set(self.db.get_setting("seconds_per_question"))

    def save(self):
        try:
            secs = int(self.secs.get())
            if not 5 <= secs <= 300: raise ValueError
        except ValueError:
            return self.app.flash("Seconds per question must be a whole number from 5 to 300.", "err")
        self.db.set_setting("sound", int(self.sound.get())); self.db.set_setting("timed_default", int(self.timed.get()))
        self.db.set_setting("seconds_per_question", secs)
        self.app.flash("Settings saved.", "ok")

    def reset(self):
        if messagebox.askyesno("Reset preferences", "Restore all preferences to their defaults?"):
            self.db.reset_settings(); self.on_show(); self.app.flash("Preferences reset to defaults.", "ok")
