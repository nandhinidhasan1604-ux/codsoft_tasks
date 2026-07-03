import streamlit as st
import random

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Tic-Tac-Toe AI",
    page_icon="🎮",
    layout="centered"
)

# =====================
# CUSTOM CSS
# =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

* { font-family: 'Poppins', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

.main-title {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #f093fb, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0px;
    padding-top: 10px;
}

.sub-title {
    text-align: center;
    color: rgba(255,255,255,0.4);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    margin-bottom: 20px;
}

.score-container {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin: 16px 0;
}

.score-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 12px 24px;
    text-align: center;
    flex: 1;
}

.score-label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.score-you { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
.score-draw { font-size: 1.8rem; font-weight: 700; color: rgba(255,255,255,0.6); }
.score-ai { font-size: 1.8rem; font-weight: 700; color: #f9a8d4; }

.status-box {
    text-align: center;
    padding: 10px;
    border-radius: 10px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: #a78bfa;
    font-size: 1rem;
    font-weight: 600;
    margin: 12px 0;
}

div[data-testid="column"] button {
    width: 100% !important;
    height: 90px !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    transition: all 0.2s !important;
}

div[data-testid="column"] button:hover {
    background: rgba(255,255,255,0.14) !important;
    border-color: rgba(167,139,250,0.5) !important;
    transform: scale(1.03) !important;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 16px;
    flex-wrap: wrap;
}

.badge {
    font-size: 0.7rem;
    padding: 4px 12px;
    border-radius: 99px;
    border: 1px solid rgba(167,139,250,0.35);
    color: rgba(167,139,250,0.85);
    background: rgba(167,139,250,0.1);
}

div[data-testid="stRadio"] label {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =====================
# GAME LOGIC
# =====================

def check_winner(board):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
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
# SESSION STATE
# =====================
if 'board' not in st.session_state:
    st.session_state.board = [' '] * 9
if 'scores' not in st.session_state:
    st.session_state.scores = {'You': 0, 'Draw': 0, 'AI': 0}
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'status' not in st.session_state:
    st.session_state.status = "🎮 Your turn! Place ✕"
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = 'Hard'

# =====================
# UI
# =====================

st.markdown('<div class="main-title">✦ Tic-Tac-Toe AI ✦</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">MINIMAX · ALPHA-BETA PRUNING</div>', unsafe_allow_html=True)

# difficulty
difficulty = st.radio(
    "Difficulty",
    ['Easy', 'Medium', 'Hard'],
    horizontal=True,
    index=2
)
if difficulty != st.session_state.difficulty:
    st.session_state.difficulty = difficulty
    st.session_state.board = [' '] * 9
    st.session_state.game_over = False
    st.session_state.status = "🎮 Your turn! Place ✕"

# scoreboard
scores = st.session_state.scores
st.markdown(f"""
<div class="score-container">
    <div class="score-card">
        <div class="score-label">You</div>
        <div class="score-you">{scores['You']}</div>
    </div>
    <div class="score-card">
        <div class="score-label">Draw</div>
        <div class="score-draw">{scores['Draw']}</div>
    </div>
    <div class="score-card">
        <div class="score-label">AI</div>
        <div class="score-ai">{scores['AI']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# status
st.markdown(
    f'<div class="status-box">{st.session_state.status}</div>',
    unsafe_allow_html=True
)

# board
board = st.session_state.board
winner, win_combo = check_winner(board)

cols = st.columns(3)
for i in range(9):
    with cols[i % 3]:
        cell_text = board[i]
        if cell_text == 'X':
            display = '✕'
        elif cell_text == 'O':
            display = '○'
        else:
            display = ' '

        if st.button(
            display,
            key=f"cell_{i}",
            disabled=st.session_state.game_over or board[i] != ' '
        ):
            if not st.session_state.game_over and board[i] == ' ':
                # human move
                board[i] = 'X'
                winner, win_combo = check_winner(board)

                if winner == 'X':
                    st.session_state.scores['You'] += 1
                    st.session_state.status = "🎉 You win! Amazing!"
                    st.session_state.game_over = True
                elif is_draw(board):
                    st.session_state.scores['Draw'] += 1
                    st.session_state.status = "🤝 It's a Draw!"
                    st.session_state.game_over = True
                else:
                    # AI move
                    ai_move = get_best_move(board, st.session_state.difficulty)
                    board[ai_move] = 'O'
                    winner, _ = check_winner(board)

                    if winner == 'O':
                        st.session_state.scores['AI'] += 1
                        st.session_state.status = "🤖 AI wins! Try again!"
                        st.session_state.game_over = True
                    elif is_draw(board):
                        st.session_state.scores['Draw'] += 1
                        st.session_state.status = "🤝 It's a Draw!"
                        st.session_state.game_over = True
                    else:
                        st.session_state.status = "🎮 Your turn! Place ✕"

                st.session_state.board = board
                st.rerun()

# restart
st.markdown("<br>", unsafe_allow_html=True)
if st.button("↺  Restart Game", use_container_width=True):
    st.session_state.board = [' '] * 9
    st.session_state.game_over = False
    st.session_state.status = "🎮 Your turn! Place ✕"
    st.rerun()

# badges
st.markdown("""
<div class="badge-row">
    <span class="badge">🤖 Minimax AI</span>
    <span class="badge">✂ Alpha-Beta Pruning</span>
    <span class="badge">🏆 Unbeatable on Hard</span>
</div>
""", unsafe_allow_html=True)