"""Shared colours, fonts and ttk styles so every page looks consistent."""
from tkinter import ttk

NAVY, NAVY_L, GOLD, WHITE, BG = "#14274E", "#22407A", "#C9A227", "#FFFFFF", "#F4F6FA"
TEXT, OK, WARN, ERR = "#1B2438", "#2E7D32", "#B26A00", "#B00020"
FONT = "Segoe UI"
H1, H2, BODY, SMALL = (FONT, 22, "bold"), (FONT, 15, "bold"), (FONT, 11), (FONT, 9)
BANNERS = {"ok": ("#E6F4EA", OK), "warn": ("#FFF4E0", WARN), "err": ("#FDE7EA", ERR), "info": ("#E8EEF9", NAVY)}


def setup_styles(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background=WHITE, relief="solid", borderwidth=1, bordercolor="#D5DBE8")
    s.configure("TLabel", background=BG, foreground=TEXT, font=BODY)
    s.configure("Card.TLabel", background=WHITE, foreground=TEXT, font=BODY)
    s.configure("H1.TLabel", font=H1, foreground=NAVY)
    s.configure("H2.TLabel", font=H2, foreground=NAVY)
    s.configure("Q.TLabel", background=WHITE, foreground=NAVY, font=(FONT, 14, "bold"))
    s.configure("Big.TLabel", background=WHITE, foreground=NAVY, font=(FONT, 34, "bold"))
    s.configure("TButton", font=BODY, padding=(14, 8), background=NAVY, foreground=WHITE, borderwidth=0, focuscolor=GOLD)
    s.map("TButton", background=[("active", NAVY_L), ("disabled", "#9AA5B8")], foreground=[("disabled", "#E4E8F0")])
    s.configure("Gold.TButton", background=GOLD, foreground=NAVY, font=(FONT, 11, "bold"))
    s.map("Gold.TButton", background=[("active", "#DDB63A"), ("disabled", "#E2D49A")])
    s.configure("Danger.TButton", background=ERR)
    s.map("Danger.TButton", background=[("active", "#D32F4A")])
    s.configure("Opt.TRadiobutton", background=WHITE, foreground=TEXT, font=(FONT, 12), padding=8)
    s.map("Opt.TRadiobutton", background=[("active", "#EEF2FA")])
    s.configure("TRadiobutton", background=BG, font=BODY)
    s.configure("TCheckbutton", background=BG, font=BODY)
    s.configure("Card.TCheckbutton", background=WHITE, font=BODY)
    s.configure("Horizontal.TProgressbar", troughcolor="#DCE2EE", background=GOLD, thickness=14)
    s.configure("Treeview", rowheight=28, font=BODY, background=WHITE, fieldbackground=WHITE)
    s.configure("Treeview.Heading", font=(FONT, 10, "bold"), background=NAVY, foreground=WHITE)
    s.map("Treeview", background=[("selected", NAVY_L)], foreground=[("selected", WHITE)])
