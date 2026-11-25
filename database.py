"""SQLite data layer: schema creation, seeding and every query the app needs."""
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.db")
CATEGORIES = ["Python", "General Knowledge", "Science", "Mathematics", "History"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
DEFAULTS = {"sound": "1", "timed_default": "0", "seconds_per_question": "30", "player_name": "Guest"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, difficulty TEXT NOT NULL,
    text TEXT NOT NULL, opt1 TEXT NOT NULL, opt2 TEXT NOT NULL, opt3 TEXT NOT NULL, opt4 TEXT NOT NULL,
    correct INTEGER NOT NULL CHECK(correct BETWEEN 0 AND 3), explanation TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS results(
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT, difficulty TEXT,
    score INTEGER, total INTEGER, percent REAL, seconds INTEGER, mode TEXT, taken_at TEXT);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
"""

# (category, difficulty, question, options, index of correct option, explanation)
SEED = [
 ("Python","Easy","Which keyword defines a function in Python?",["func","def","function","lambda"],1,"Functions are defined with the def keyword."),
 ("Python","Easy","Which of these data types is immutable?",["list","dict","tuple","set"],2,"Tuples cannot be modified after creation."),
 ("Python","Medium","What does [1, 2, 3][-1] return?",["1","2","3","IndexError"],2,"Negative indexes count from the end; -1 is the last item."),
 ("Python","Medium","Which decorator makes a method behave like a read-only attribute?",["@staticmethod","@classmethod","@property","@abstractmethod"],2,"@property exposes a method as an attribute."),
 ("Python","Hard","What does the GIL do in CPython?",["Allows true parallel threads","Lets only one thread execute bytecode at a time","Handles garbage collection","Compiles code to machine code"],1,"The Global Interpreter Lock serialises bytecode execution."),
 ("Python","Hard","After `a, *b = [1, 2, 3]`, what is b?",["[2, 3]","2","(2, 3)","SyntaxError"],0,"The starred target collects the remaining items into a list."),
 ("General Knowledge","Easy","What is the capital of France?",["Berlin","Madrid","Paris","Rome"],2,"Paris is the capital of France."),
 ("General Knowledge","Easy","How many continents are there?",["5","6","7","8"],2,"The common convention counts seven continents."),
 ("General Knowledge","Medium","Which is the largest ocean?",["Atlantic","Indian","Arctic","Pacific"],3,"The Pacific covers about a third of Earth's surface."),
 ("General Knowledge","Medium","Which language has the most native speakers?",["English","Mandarin Chinese","Spanish","Hindi"],1,"Mandarin Chinese has the most native speakers."),
 ("General Knowledge","Hard","Which city hosted the first modern Olympic Games in 1896?",["Paris","London","Athens","Rome"],2,"The 1896 Games were held in Athens."),
 ("General Knowledge","Hard","What is the smallest country in the world by area?",["Monaco","Vatican City","San Marino","Malta"],1,"Vatican City covers roughly 0.44 square kilometres."),
 ("Science","Easy","Which gas do plants absorb for photosynthesis?",["Oxygen","Carbon dioxide","Nitrogen","Hydrogen"],1,"Plants take in CO2 and release oxygen."),
 ("Science","Easy","H2O is the chemical formula for what?",["Hydrogen","Salt","Water","Peroxide"],2,"Two hydrogen atoms and one oxygen atom form water."),
 ("Science","Medium","Which organelle is known as the powerhouse of the cell?",["Nucleus","Mitochondrion","Ribosome","Golgi body"],1,"Mitochondria produce most of the cell's ATP."),
 ("Science","Medium","Which particle carries a negative electric charge?",["Proton","Neutron","Electron","Photon"],2,"Electrons are negatively charged."),
 ("Science","Hard","What is the approximate speed of light in a vacuum?",["3 x 10^6 m/s","3 x 10^8 m/s","3 x 10^10 m/s","3 x 10^5 m/s"],1,"Light travels at about 299,792 km/s."),
 ("Science","Hard","Which gas is the most abundant in Earth's atmosphere?",["Oxygen","Nitrogen","Carbon dioxide","Argon"],1,"Nitrogen makes up about 78% of the atmosphere."),
 ("Mathematics","Easy","What is 12 x 8?",["86","96","108","98"],1,"12 x 8 = 96."),
 ("Mathematics","Easy","What do the angles of a triangle add up to?",["90 degrees","180 degrees","270 degrees","360 degrees"],1,"Interior angles of a triangle sum to 180 degrees."),
 ("Mathematics","Medium","Solve for x: 2x + 6 = 20",["5","6","7","8"],2,"Subtract 6 to get 2x = 14, so x = 7."),
 ("Mathematics","Medium","What is the square root of 169?",["11","12","13","14"],2,"13 x 13 = 169."),
 ("Mathematics","Hard","What is the derivative of x^3?",["x^2","3x^2","3x","x^3 / 3"],1,"The power rule gives 3x^2."),
 ("Mathematics","Hard","What is the value of 5! (5 factorial)?",["60","100","120","150"],2,"5 x 4 x 3 x 2 x 1 = 120."),
 ("History","Easy","Who was the first President of the United States?",["Abraham Lincoln","George Washington","Thomas Jefferson","John Adams"],1,"George Washington served from 1789 to 1797."),
 ("History","Easy","In which year did World War II end?",["1918","1939","1945","1950"],2,"The war ended in 1945."),
 ("History","Medium","Which civilization built Machu Picchu?",["Aztec","Maya","Inca","Olmec"],2,"Machu Picchu was an Inca citadel."),
 ("History","Medium","Who was the first emperor of unified China?",["Kublai Khan","Qin Shi Huang","Sun Yat-sen","Liu Bang"],1,"Qin Shi Huang unified China in 221 BCE."),
 ("History","Hard","The Peace of Westphalia (1648) ended which conflict?",["Hundred Years' War","Thirty Years' War","War of the Roses","Seven Years' War"],1,"It ended the Thirty Years' War in Europe."),
 ("History","Hard","In which year did the French Revolution begin?",["1776","1789","1799","1815"],1,"The Revolution began in 1789."),
]


def _where(category, difficulty):
    """Build a WHERE clause; 'All' (or empty) means no filter on that field."""
    clauses, params = [], []
    if category and category != "All":
        clauses.append("category=?"); params.append(category)
    if difficulty and difficulty != "All":
        clauses.append("difficulty=?"); params.append(difficulty)
    return (" WHERE " + " AND ".join(clauses) if clauses else ""), params


def _to_question(row):
    q = dict(row)
    q["options"] = [row["opt1"], row["opt2"], row["opt3"], row["opt4"]]
    return q


class Database:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self._seed()

    def _seed(self):
        """Populate questions and default settings only when they are missing."""
        if self.conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
            self.conn.executemany(
                "INSERT INTO questions(category,difficulty,text,opt1,opt2,opt3,opt4,correct,explanation)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                [(c, d, t, *o, a, e) for c, d, t, o, a, e in SEED])
        for k, v in DEFAULTS.items():
            self.conn.execute("INSERT OR IGNORE INTO settings VALUES(?,?)", (k, v))
        self.conn.commit()

    # ---- questions ----
    def count(self, category, difficulty):
        w, p = _where(category, difficulty)
        return self.conn.execute("SELECT COUNT(*) FROM questions" + w, p).fetchone()[0]

    def get_questions(self, category, difficulty, limit=None, shuffle=True):
        w, p = _where(category, difficulty)
        sql = "SELECT * FROM questions" + w + (" ORDER BY RANDOM()" if shuffle else " ORDER BY category, id")
        if limit:
            sql += " LIMIT ?"; p.append(limit)
        return [_to_question(r) for r in self.conn.execute(sql, p)]

    def save_question(self, q, qid=None):
        vals = (q["category"], q["difficulty"], q["text"], *q["options"], q["correct"], q["explanation"])
        if qid is None:
            self.conn.execute("INSERT INTO questions(category,difficulty,text,opt1,opt2,opt3,opt4,correct,explanation)"
                              " VALUES(?,?,?,?,?,?,?,?,?)", vals)
        else:
            self.conn.execute("UPDATE questions SET category=?,difficulty=?,text=?,opt1=?,opt2=?,opt3=?,opt4=?,"
                              "correct=?,explanation=? WHERE id=?", vals + (qid,))
        self.conn.commit()

    def delete_question(self, qid):
        self.conn.execute("DELETE FROM questions WHERE id=?", (qid,)); self.conn.commit()

    # ---- results ----
    def add_result(self, r):
        self.conn.execute("INSERT INTO results(name,category,difficulty,score,total,percent,seconds,mode,taken_at)"
                          " VALUES(?,?,?,?,?,?,?,?,?)",
                          (r["name"], r["category"], r["difficulty"], r["score"], r["total"], r["percent"],
                           r["seconds"], r["mode"], datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.conn.commit()

    def leaderboard(self, category="All", difficulty="All", order="Highest score", limit=100):
        w, p = _where(category, difficulty)
        orders = {"Highest score": "percent DESC, seconds ASC", "Most recent": "id DESC", "Fastest": "seconds ASC"}
        sql = "SELECT * FROM results" + w + " ORDER BY " + orders.get(order, orders["Highest score"]) + " LIMIT ?"
        return list(self.conn.execute(sql, p + [limit]))

    def clear_results(self):
        self.conn.execute("DELETE FROM results"); self.conn.commit()

    def recent_stats(self):
        """Return (latest result row or None, current streak of consecutive passes >= 60%)."""
        rows = list(self.conn.execute("SELECT * FROM results ORDER BY id DESC LIMIT 50"))
        streak = 0
        for r in rows:
            if r["percent"] >= 60: streak += 1
            else: break
        return (rows[0] if rows else None), streak

    # ---- settings ----
    def get_setting(self, key):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else DEFAULTS.get(key, "")

    def set_setting(self, key, value):
        self.conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, str(value))); self.conn.commit()

    def reset_settings(self):
        for k, v in DEFAULTS.items(): self.set_setting(k, v)
