"""Quiz rules and scoring. No Tkinter or SQL in here."""
import math
import time


def performance_message(pct):
    if pct >= 90: return "Outstanding! Exceptional mastery of the material."
    if pct >= 75: return "Excellent work. You have a strong grasp of this topic."
    if pct >= 60: return "Good effort. A little more practice will sharpen your results."
    if pct >= 40: return "Fair attempt. Try Practice mode to strengthen weak areas."
    return "Keep going! Review the answers and try again."


class QuizSession:
    def __init__(self, questions, category, difficulty, player="Guest", practice=False, timed=False, secs_per_q=30):
        self.questions, self.category, self.difficulty = questions, category, difficulty
        self.player, self.practice, self.timed = player, practice, timed
        self.total = len(questions)
        self.answers = [None] * self.total          # chosen option index per question
        self.index = 0
        self.limit = secs_per_q * self.total if timed else None
        self.start = time.monotonic()
        self.end = None                              # set when finished, freezes the clock

    @property
    def finished(self): return self.end is not None
    def current(self): return self.questions[self.index]
    def answer(self, choice): self.answers[self.index] = choice
    def is_correct(self, i): return self.answers[i] == self.questions[i]["correct"]
    def score(self): return sum(self.is_correct(i) for i in range(self.total))
    def answered(self): return sum(a is not None for a in self.answers)
    def unanswered(self): return self.total - self.answered()
    def elapsed(self): return int((self.end or time.monotonic()) - self.start)

    def remaining(self):
        """Seconds left (None when untimed)."""
        if self.limit is None: return None
        return max(0, math.ceil(self.limit - (time.monotonic() - self.start)))

    def finish(self):
        self.end = self.end or time.monotonic()
        score = self.score()
        secs = min(self.elapsed(), self.limit) if self.limit else self.elapsed()
        return {"name": self.player, "category": self.category, "difficulty": self.difficulty,
                "score": score, "total": self.total, "correct": score,
                "incorrect": self.total - score - self.unanswered(), "unanswered": self.unanswered(),
                "percent": round(100 * score / self.total, 1) if self.total else 0.0,
                "seconds": secs, "mode": "Practice" if self.practice else ("Timed" if self.timed else "Untimed")}
