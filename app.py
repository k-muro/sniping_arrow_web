from flask import Flask, render_template, request, jsonify
from board_logic.board import SnipingArrowBoard  # ロジック部分
import traceback
app = Flask(__name__)
from flask import jsonify

@app.errorhandler(Exception)
def handle_exception(e):
    # スタックトレースを取得
    tb = traceback.format_exc()
    app.logger.error(f"Error occurred: {str(e)}\nTraceback:\n{tb}")
    
    # クライアントにエラーメッセージをJSONで返す
    return jsonify({
        "error": "Server encountered an error",
        "details": str(e),
        "traceback": tb
    }), 500

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # フォームから盤面データを受け取る
        data = request.json.get("board_data")
        rows = len(data)
        cols = len(data[0])
        board = SnipingArrowBoard(rows, cols)
        for r, row in enumerate(data):
            for c, cell in enumerate(row):
                if cell == "■":
                    board.set_black_cell(r, c)
                elif isinstance(cell, int):
                    board.set_number(r, c, cell)
        # 結果を返す（ダミーで動作確認用）
        result = board.display_board()
        return jsonify({"message": "Received board data", "result": result})

    return render_template("index.html")

@app.route('/api/export_url', methods=['POST'])
def export_url():
    data = request.json
    board = data.get('board')
    #print(board)
    sab=get_board(board)
    sab.display_board()
    url=sab.get_url()
    return jsonify({'url':url})


def get_board(board):
    rows=len(board)
    cols=len(board[1])
    sab= SnipingArrowBoard(rows, cols)

    # 方向記号から内部表現への変換マップ
    direction_map = {
        "→": "right",
        "←": "left",
        "↑": "up",
        "↓": "down"
    }

    for r in range(rows):
        for c in range(cols):
                value = str(board[r][c])
                # 空のセルはスキップ
                if not value or value == " ":
                    continue
                
                # 値の種類に応じて適切なメソッドを呼び出す
                if value.isdigit():
                    # 数字の場合
                    sab.set_number(r, c, int(value))
                elif value == "■":
                    # 黒マスの場合
                    sab.set_black_cell(r, c)
                elif value in direction_map:
                    # 矢印の場合
                    sab.set_arrow_head(r, c, direction_map[value])
    return sab

@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
    data = request.json
    board = data.get('board')
    #print(board)
    sab=get_board(board)
    #sab.display_board()
    is_hukusuukai,ans_list1,ans_list2=sab.solve_board()
    ans_board1=[{"startRow":i[0],"startCol":i[1],"direction":i[2],"length":i[3],"path":list(sab.get_arrow_path(i)),"tip":list(sab.get_arrow_tip(i))} for i in ans_list1]
    #print(ans_board1)
    ans_board2=[{"startRow":i[0],"startCol":i[1],"direction":i[2],"length":i[3],"path":list(sab.get_arrow_path(i)),"tip":list(sab.get_arrow_tip(i))} for i in ans_list2]
    #print(jsonify({'is_hukusuukai':is_hukusuukai,'ans_board1': ans_board1, 'ans_board2': ans_board2}))
    return jsonify({'is_hukusuukai':is_hukusuukai,'ans_board1': ans_board1, 'ans_board2': ans_board2})


if __name__ == "__main__":
    app.run(debug=True)
