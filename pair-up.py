"""
Memory Match - a small desktop memory game (Tkinter, standard library only).

Run:  python3 pair-up.py
"""

import random
import tkinter as tk

SYMBOLS = ["A", "B", "C", "D", "E", "F"]   # 6 pairs -> 12 cards
COLS, ROWS = 4, 3
FLIP_BACK_MS = 800                          # mismatch delay

BG = "#1e2130"
CARD_BACK = "#394867"
CARD_FACE = "#f1f3f8"
CARD_MATCHED = "#4caf7d"
TEXT_LIGHT = "#f1f3f8"
TEXT_DARK = "#1e2130"


class MemoryGame:
    def __init__(self, root):
        self.root = root
        root.title("Memory Match")
        root.configure(bg=BG)
        root.resizable(False, False)

        # --- header ---
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=20, pady=(18, 8))

        self.attempts_label = tk.Label(
            header, text="Attempts: 0", font=("Helvetica", 15, "bold"),
            bg=BG, fg=TEXT_LIGHT,
        )
        self.attempts_label.pack(side="left")

        tk.Button(
            header, text="Restart", command=self.reset,
            font=("Helvetica", 13), highlightthickness=0,
        ).pack(side="right")

        # --- board ---
        board = tk.Frame(root, bg=BG)
        board.pack(padx=20)

        self.cards = []          # label widgets, index 0..11
        for i in range(COLS * ROWS):
            lbl = tk.Label(
                board, text="?", width=4, height=2,
                font=("Helvetica", 28, "bold"),
                bg=CARD_BACK, fg=TEXT_LIGHT,
                relief="raised", bd=2, cursor="hand2",
            )
            lbl.grid(row=i // COLS, column=i % COLS, padx=6, pady=6)
            # default arg binds the index at definition time, not call time
            lbl.bind("<Button-1>", lambda _e, idx=i: self.on_click(idx))
            self.cards.append(lbl)

        # --- status ---
        self.status = tk.Label(
            root, text="Find all six pairs.", font=("Helvetica", 14),
            bg=BG, fg=TEXT_LIGHT,
        )
        self.status.pack(pady=(10, 20))

        self.pending_after = None
        self.reset()

    # ------------------------------------------------------------------ state
    def reset(self):
        """Reset and reshuffle. Safe to call mid-turn."""
        # cancel any scheduled flip-back so it can't fire on the new board
        if self.pending_after is not None:
            self.root.after_cancel(self.pending_after)
            self.pending_after = None

        self.values = SYMBOLS * 2
        random.shuffle(self.values)

        self.first = None
        self.second = None
        self.locked = False          # True while a mismatched pair is showing
        self.matched = set()
        self.attempts = 0

        for lbl in self.cards:
            lbl.config(text="?", bg=CARD_BACK, fg=TEXT_LIGHT, relief="raised")

        self.attempts_label.config(text="Attempts: 0")
        self.status.config(text="Find all six pairs.")

    # ------------------------------------------------------------------ input
    def on_click(self, idx):
        # Guards against rapid clicking:
        if self.locked:                 # a mismatch is still on screen
            return
        if idx in self.matched:         # already solved
            return
        if idx == self.first:           # same card clicked twice
            return

        self.show(idx)

        if self.first is None:
            self.first = idx
            return

        # second card of the turn
        self.second = idx
        self.attempts += 1
        self.attempts_label.config(text=f"Attempts: {self.attempts}")

        if self.values[self.first] == self.values[self.second]:
            self.mark_matched(self.first, self.second)
            self.first = self.second = None
            if len(self.matched) == len(self.values):
                self.status.config(
                    text=f"Congratulations! All pairs matched in {self.attempts} attempts."
                )
        else:
            self.locked = True
            self.pending_after = self.root.after(FLIP_BACK_MS, self.hide_pair)

    # ------------------------------------------------------------------ view
    def show(self, idx):
        self.cards[idx].config(
            text=self.values[idx], bg=CARD_FACE, fg=TEXT_DARK, relief="sunken"
        )

    def mark_matched(self, a, b):
        self.matched.update((a, b))
        for i in (a, b):
            self.cards[i].config(bg=CARD_MATCHED, fg=TEXT_LIGHT, relief="flat")

    def hide_pair(self):
        for i in (self.first, self.second):
            if i is not None:
                self.cards[i].config(
                    text="?", bg=CARD_BACK, fg=TEXT_LIGHT, relief="raised"
                )
        self.first = self.second = None
        self.locked = False
        self.pending_after = None


if __name__ == "__main__":
    root = tk.Tk()
    MemoryGame(root)
    root.mainloop()