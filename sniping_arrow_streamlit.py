import streamlit as st

# 盤面の状態を保持する初期化
if "board" not in st.session_state:
    # 初期盤面（5x5の空白）
    rows, cols = 5, 5
    st.session_state.board = [["" for _ in range(cols)] for _ in range(rows)]
    st.session_state.selected = (0, 0)  # 選択中のマス

# 現在選択中のマスの座標を取得
selected_row, selected_col = st.session_state.selected

# 盤面サイズの設定
st.sidebar.title("Settings")
rows = st.sidebar.number_input("Rows", min_value=1, max_value=10, value=5, step=1)
cols = st.sidebar.number_input("Cols", min_value=1, max_value=10, value=5, step=1)

# サイズ変更時の処理
if len(st.session_state.board) != rows or len(st.session_state.board[0]) != cols:
    st.session_state.board = [["" for _ in range(cols)] for _ in range(rows)]

# キーボード操作を有効化するJSコード
st.markdown(
    """
    <script>
    const sendKey = (key) => {
        const streamlitEvent = new CustomEvent("streamlit-event", {
            detail: { key: key },
        });
        window.dispatchEvent(streamlitEvent);
    };
    document.addEventListener("keydown", (event) => {
        sendKey(event.key);
    });
    </script>
    """,
    unsafe_allow_html=True,
)

# キーボード操作の処理
keyboard_input = st.experimental_get_query_params().get("key", [""])[0]

# キーボード操作を処理
if keyboard_input in ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]:
    # 矢印キーによる選択マスの移動
    if keyboard_input == "ArrowUp" and selected_row > 0:
        selected_row -= 1
    elif keyboard_input == "ArrowDown" and selected_row < rows - 1:
        selected_row += 1
    elif keyboard_input == "ArrowLeft" and selected_col > 0:
        selected_col -= 1
    elif keyboard_input == "ArrowRight" and selected_col < cols - 1:
        selected_col += 1
    st.session_state.selected = (selected_row, selected_col)

elif keyboard_input.isdigit():
    # 数字キーで入力
    st.session_state.board[selected_row][selected_col] = keyboard_input
elif keyboard_input == "x":
    # 黒マスを設定
    st.session_state.board[selected_row][selected_col] = "■"
elif keyboard_input in ["w", "a", "s", "d"]:
    # 矢印の設定
    arrow_map = {"w": "↑", "a": "←", "s": "↓", "d": "→"}
    st.session_state.board[selected_row][selected_col] = arrow_map[keyboard_input]
elif keyboard_input == " ":
    # スペースキーでクリア
    st.session_state.board[selected_row][selected_col] = ""

# 盤面描画
st.write("### Board")
for r in range(rows):
    cols = st.columns(len(st.session_state.board[r]))
    for c, col in enumerate(cols):
        with col:
            color = "lightblue" if (r, c) == st.session_state.selected else "white"
            st.button(
                st.session_state.board[r][c] or " ",
                key=f"cell-{r}-{c}",
                on_click=lambda row=r, col=c: st.session_state.update(
                    {"selected": (row, col)}
                ),
                args=(r, c),
            )
