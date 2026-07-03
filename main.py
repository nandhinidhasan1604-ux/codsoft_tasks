import tkinter as tk
from tkinter import messagebox
import random
import time

# =====================
# GAME LOGIC
# =====================

def check_winner(board):
    wins = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    for combo in wins:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
            return board[combo[0]], combo
    return None, None

def is_draw(board):
    return ' ' not in board

def minimax(board, is_maximizing, alpha, beta, depth, max_depth):
    winner, _ = check_winner(board)
    if winner == 'O': return 10 - depth
    if winner == 'X': return depth - 10
    if is_draw(board): return 0
    if depth == max_depth: return 0

    if is_maximizing:
        best = -1000
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                best = max(best, minimax(board, False, alpha, beta, depth+1, max_depth))
                board[i] = ' '
                alpha = max(alpha, best)
                if beta <= alpha: break
        return best
    else:
        best = 1000
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                best = min(best, minimax(board, True, alpha, beta, depth+1, max_depth))
                board[i] = ' '
                beta = min(beta, best)
                if beta <= alpha: break
        return best

def get_best_move(board, difficulty):
    empty = [i for i in range(9) if board[i] == ' ']
    if difficulty == 'Easy':
        return random.choice(empty)
    max_depth = 2 if difficulty == 'Medium' else 9
    best_score, best_move = -1000, -1
    for i in empty:
        board[i] = 'O'
        score = minimax(board, False, -1000, 1000, 0, max_depth)
        board[i] = ' '
        if score > best_score:
            best_score = score
            best_move = i
    return best_move

# =====================
# GUI
# =====================

class TicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic-Tac-Toe AI")
        self.window.resizable(False, False)
        self.window.configure(bg="#0f0c29")

        # colors
        self.BG        = "#0f0c29"
        self.CARD      = "#1a1740"
        self.BORDER    = "#3d3680"
        self.X_COLOR   = "#a78bfa"
        self.O_COLOR   = "#f9a8d4"
        self.TEXT      = "#ffffff"
        self.SUBTEXT   = "#9990cc"
        self.BTN_ACT   = "#6d5dfc"
        self.BTN_IDLE  = "#2a2560"
        self.CELL_BG   = "#1e1b4b"
        self.CELL_HOV  = "#2d2a6e"
        self.WIN_COLOR = "#a78bfa"
        self.GRAD1     = "#667eea"
        self.GRAD2     = "#764ba2"

        self.board = [' '] * 9
        self.buttons = []
        self.scores = {'You': 0, 'Draw': 0, 'AI': 0}
        self.difficulty = tk.StringVar(value='Hard')
        self.game_active = True
        self.animating = False

        self.build_ui()
        self.animate_title()
        self.window.mainloop()

    def build_ui(self):
        # ── Main Frame ──
        main = tk.Frame(self.window, bg=self.BG, padx=24, pady=20)
        main.pack()

        # ── Title ──
        title_frame = tk.Frame(main, bg=self.BG)
        title_frame.pack(pady=(0, 4))

        self.title_lbl = tk.Label(
            title_frame,
            text="✦ Tic-Tac-Toe AI ✦",
            font=("Helvetica", 22, "bold"),
            bg=self.BG,
            fg=self.X_COLOR
        )
        self.title_lbl.pack()

        tk.Label(
            main,
            text="Minimax  ·  Alpha-Beta Pruning",
            font=("Helvetica", 9),
            bg=self.BG,
            fg=self.SUBTEXT
        ).pack(pady=(0, 14))

        # ── Difficulty ──
        diff_frame = tk.Frame(main, bg=self.CARD, padx=10, pady=8)
        diff_frame.pack(fill="x", pady=(0, 14))

        tk.Label(
            diff_frame,
            text="DIFFICULTY",
            font=("Helvetica", 8, "bold"),
            bg=self.CARD,
            fg=self.SUBTEXT
        ).pack(side="left", padx=(6, 10))

        self.diff_btns = {}
        for level in ['Easy', 'Medium', 'Hard']:
            btn = tk.Button(
                diff_frame,
                text=level,
                font=("Helvetica", 10, "bold"),
                bg=self.BTN_IDLE,
                fg=self.SUBTEXT,
                activebackground=self.BTN_ACT,
                activeforeground=self.TEXT,
                relief="flat",
                padx=14,
                pady=4,
                cursor="hand2",
                bd=0,
                command=lambda l=level: self.set_difficulty(l)
            )
            btn.pack(side="left", padx=4)
            self.diff_btns[level] = btn
        self.highlight_diff('Hard')

        # ── Scoreboard ──
        score_frame = tk.Frame(main, bg=self.BG)
        score_frame.pack(fill="x", pady=(0, 14))

        self.score_labels = {}
        for i, (name, color) in enumerate([('You', self.X_COLOR), ('Draw', self.SUBTEXT), ('AI', self.O_COLOR)]):
            card = tk.Frame(score_frame, bg=self.CARD, padx=20, pady=10)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            score_frame.columnconfigure(i, weight=1)

            tk.Label(
                card,
                text=name,
                font=("Helvetica", 9),
                bg=self.CARD,
                fg=self.SUBTEXT
            ).pack()

            lbl = tk.Label(
                card,
                text="0",
                font=("Helvetica", 24, "bold"),
                bg=self.CARD,
                fg=color
            )
            lbl.pack()
            self.score_labels[name] = lbl

        # ── Status ──
        self.status_lbl = tk.Label(
            main,
            text="🎮  Your turn!  Place  ✕",
            font=("Helvetica", 12),
            bg=self.BG,
            fg=self.X_COLOR
        )
        self.status_lbl.pack(pady=(0, 12))

        # ── Board ──
        board_frame = tk.Frame(main, bg=self.BORDER, padx=3, pady=3)
        board_frame.pack(pady=(0, 14))

        inner = tk.Frame(board_frame, bg=self.BG)
        inner.pack()

        for i in range(9):
            btn = tk.Button(
                inner,
                text=' ',
                font=("Helvetica", 32, "bold"),
                width=4,
                height=2,
                bg=self.CELL_BG,
                fg=self.TEXT,
                activebackground=self.CELL_HOV,
                relief="flat",
                cursor="hand2",
                bd=0,
                command=lambda i=i: self.human_move(i)
            )
            btn.grid(row=i//3, column=i%3, padx=4, pady=4)

            # hover effect
            btn.bind("<Enter>", lambda e, b=btn: self.on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_hover(b, False))
            self.buttons.append(btn)

        # ── Restart Button ──
        self.restart_btn = tk.Button(
            main,
            text="↺   Restart Game",
            font=("Helvetica", 12, "bold"),
            bg=self.BTN_ACT,
            fg=self.TEXT,
            activebackground=self.GRAD2,
            activeforeground=self.TEXT,
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2",
            bd=0,
            command=self.restart
        )
        self.restart_btn.pack(fill="x", pady=(0, 14))

        # ── Badges ──
        badge_frame = tk.Frame(main, bg=self.BG)
        badge_frame.pack()

        for text in ['🤖 Minimax AI', '✂ Alpha-Beta Pruning', '🏆 Unbeatable on Hard']:
            tk.Label(
                badge_frame,
                text=text,
                font=("Helvetica", 8),
                bg=self.CARD,
                fg=self.SUBTEXT,
                padx=10,
                pady=4
            ).pack(side="left", padx=4)

    # ── Hover Effect ──
    def on_hover(self, btn, entering):
        if btn['text'] == ' ' and self.game_active:
            btn.config(bg=self.CELL_HOV if entering else self.CELL_BG)

    # ── Difficulty ──
    def set_difficulty(self, level):
        self.difficulty.set(level)
        self.highlight_diff(level)
        self.restart()

    def highlight_diff(self, level):
        for name, btn in self.diff_btns.items():
            if name == level:
                btn.config(bg=self.BTN_ACT, fg=self.TEXT)
            else:
                btn.config(bg=self.BTN_IDLE, fg=self.SUBTEXT)

    # ── Title Animation ──
    def animate_title(self):
        colors = [self.X_COLOR, "#c4b5fd", "#ddd6fe", self.O_COLOR, "#f9a8d4"]
        def cycle(i=0):
            self.title_lbl.config(fg=colors[i % len(colors)])
            self.window.after(800, lambda: cycle(i+1))
        cycle()

    # ── Human Move ──
    def human_move(self, i):
        if not self.game_active or self.board[i] != ' ' or self.animating:
            return

        self.board[i] = 'X'
        self.buttons[i].config(text='✕', fg=self.X_COLOR)
        self.animate_cell(i, self.X_COLOR)

        if self.check_game_over():
            return

        self.game_active = False
        self.status_lbl.config(text="🤖  AI is thinking...", fg=self.SUBTEXT)
        self.window.after(500, self.ai_move)

    # ── AI Move ──
    def ai_move(self):
        move = get_best_move(self.board, self.difficulty.get())
        self.board[move] = 'O'
        self.buttons[move].config(text='○', fg=self.O_COLOR)
        self.animate_cell(move, self.O_COLOR)

        if self.check_game_over():
            return

        self.game_active = True
        self.status_lbl.config(text="🎮  Your turn!  Place  ✕", fg=self.X_COLOR)

    # ── Cell Animation ──
    def animate_cell(self, i, color):
        btn = self.buttons[i]
        sizes = [28, 36, 32, 34]
        def step(s=0):
            if s < len(sizes):
                btn.config(font=("Helvetica", sizes[s], "bold"))
                self.window.after(60, lambda: step(s+1))
        step()

    # ── Highlight Win ──
    def highlight_win(self, combo):
        for i in combo:
            btn = self.buttons[i]
            def flash(b=btn, n=0):
                if n < 6:
                    color = self.WIN_COLOR if n % 2 == 0 else self.CELL_BG
                    b.config(bg=color)
                    self.window.after(180, lambda: flash(b, n+1))
                else:
                    b.config(bg=self.WIN_COLOR)
            flash()

    # ── Check Game Over ──
    def check_game_over(self):
        winner, combo = check_winner(self.board)
        if winner:
            self.game_active = False
            self.highlight_win(combo)
            if winner == 'X':
                self.scores['You'] += 1
                self.score_labels['You'].config(text=str(self.scores['You']))
                self.status_lbl.config(text="🎉  You win! Amazing!", fg=self.X_COLOR)
                self.window.after(1000, lambda: messagebox.showinfo("🎉 You Win!", "Congratulations!\nYou beat the AI!"))
            else:
                self.scores['AI'] += 1
                self.score_labels['AI'].config(text=str(self.scores['AI']))
                self.status_lbl.config(text="🤖  AI wins! Try again!", fg=self.O_COLOR)
                self.window.after(1000, lambda: messagebox.showinfo("🤖 AI Wins!", "The AI wins this round!\nBetter luck next time!"))
            self.disable_board()
            return True

        if is_draw(self.board):
            self.game_active = False
            self.scores['Draw'] += 1
            self.score_labels['Draw'].config(text=str(self.scores['Draw']))
            self.status_lbl.config(text="🤝  It's a Draw!", fg=self.SUBTEXT)
            self.window.after(1000, lambda: messagebox.showinfo("🤝 Draw!", "Perfect play!\nIt's a draw!"))
            self.disable_board()
            return True

        return False

    # ── Disable Board ──
    def disable_board(self):
        for btn in self.buttons:
            btn.config(state="disabled", cursor="arrow")

    # ── Restart ──
    def restart(self):
        self.board = [' '] * 9
        self.game_active = True
        self.status_lbl.config(
            text="🎮  Your turn!  Place  ✕",
            fg=self.X_COLOR
        )
        for btn in self.buttons:
            btn.config(
                text=' ',
                state="normal",
                cursor="hand2",
                bg=self.CELL_BG,
                fg=self.TEXT,
                font=("Helvetica", 32, "bold")
            )

# ── Start ──
TicTacToe()