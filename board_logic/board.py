from z3 import *

class SnipingArrowBoard:
    def __init__(self, rows, cols):
        """
        盤面の初期化
        :param rows: 行数
        :param cols: 列数
        """
        self.rows = rows
        self.cols = cols
        self.board = [[" " for _ in range(cols)] for _ in range(rows)]  # 空白マスで初期化
        self.numbers = {}  # 数字マスの座標と値を保持する辞書 {(row, col): value}
        self.black_cells = set()  # 黒マスの座標を保持するセット
        self.arrow_heads = {}  # 矢尻の座標と方向 {(row, col): direction}

    def set_number(self, row, col, value):
        """
        数字マスを設定する
        :param row: マスの行インデックス
        :param col: マスの列インデックス
        :param value: 数字
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError("指定された座標が盤面外です")
        self.board[row][col] = value
        self.numbers[(row, col)] = value

    def set_black_cell(self, row, col):
        """
        黒マスを設定する
        :param row: マスの行インデックス
        :param col: マスの列インデックス
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError("指定された座標が盤面外です")
        if (row, col) in self.numbers:
            raise ValueError("数字マスには黒マスを設定できません")
        self.board[row][col] = "■"  # 黒マスを■で表現
        self.black_cells.add((row, col))

    def set_arrow_head(self, row, col, direction):
        """
        矢尻を設定する
        :param row: マスの行インデックス
        :param col: マスの列インデックス
        :param direction: 矢尻の方向 ('up', 'down', 'left', 'right')
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError("指定された座標が盤面外です")
        if self.board[row][col] != " ":
            raise ValueError("指定されたマスにはすでに何かが配置されています")
        if direction not in {"up", "down", "left", "right"}:
            raise ValueError("無効な方向です。'up', 'down', 'left', 'right'を使用してください")
        
        direction_map = {"up": "↑", "down": "↓", "left": "←", "right": "→"}
        self.board[row][col] = direction_map[direction]  # 矢尻の向きを表示
        self.arrow_heads[(row, col)] = direction

    def display_board(self):
        """
        盤面を表示する
        """
        for row in self.board:
            print(". ".join(str(cell) for cell in row))
    def get_url(self):
        board_tmp = [[" " for _ in range(self.cols)] for _ in range(self.rows)]
        tmp_dict={"■":"z","↑":"u","→":"r","↓":"d","←":"l"," ":""}
        for row in range(self.rows):
            for col in range(self.cols):

                if self.board[row][col] in tmp_dict.keys():
                    board_tmp[row][col]=tmp_dict[self.board[row][col]]
                else:
                    board_tmp[row][col]=str(self.board[row][col])+""
        url_L= self.create_position_sequence(board_tmp)
        url_W=f"{self.cols}x{self.rows}"
        url_G="sniping-arrow"
        
        return f"https://pedros.works/paper-puzzle-player?W={url_W}&L={url_L}&G={url_G}"
    def create_position_sequence(self,matrix):
        """
        Creates a sequence of number-alphabet pairs from the matrix

        Args:
            matrix (list): 2D matrix containing the characters

        Returns:
            str: Formatted sequence of number-alphabet pairs
        """
        # First reorder the matrix as before
        rows = len(matrix)
        cols = len(matrix[0])
        elements = []
        for row in range(rows):
            for col in range(cols):
                index = col * rows + (rows - 1 - row)
                elements.append((index, matrix[row][col]))

        # Sort by index to get the correct order
        elements.sort(key=lambda x: x[0])
        ordered_list = [elem[1] for elem in elements]
        # Find positions of target characters
        positions = []
        for id,i in enumerate(ordered_list):
            try:
                a=int(i)
                i="("+i+")"
            except:pass
            if i!="":

                positions.append((i,id))

        ordered_chars = sorted(positions, key=lambda x: x[1])
        sequence = []

        # First character gets its absolute position
        if ordered_chars:
            first_char = ordered_chars[0]
            sequence.append(f"{first_char[0]}{first_char[1]}")

            # For subsequent characters, calculate the difference
            for i in range(1, len(ordered_chars)):
                current_char = ordered_chars[i][0]
                prev_pos = ordered_chars[i-1][1]
                current_pos = ordered_chars[i][1]
                diff = current_pos - prev_pos
                sequence.append(f"{current_char}{diff}")

        return "".join(sequence)
    def enumerate_possible_arrows(self):
        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        arrows = []

        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == "■":  # 黒マスはスキップ
                    continue
                if self.board[row][col] in {"↑","↓","→","←"}:  # 黒マスはスキップ
                    continue

                for direction, (dr, dc) in directions.items():
                    length = 2
                    path = []
                    valid = True
                    had_arrow_head=False

                    while valid:
                        next_row = row + dr * (length-1)
                        next_col = col + dc * (length-1)

                        # 範囲外チェック
                        if not (0 <= next_row < self.rows and 0 <= next_col < self.cols):
                            break

                        next_cell = self.board[next_row][next_col]

                        # 終端条件：黒マス、数字マス、矢尻を経由してはならない
                        if next_cell == "■" or isinstance(next_cell, int) :
                            break

                        path.append((next_row, next_col))

                        # 矢尻がある場合、その方向でなければ無効
                        if (next_row, next_col) in self.arrow_heads:
                            had_arrow_head=True
                            if self.arrow_heads[(next_row, next_col)] != direction:
                                break

                        # 始点が数字マスの場合、長さが固定
                        if (row, col) in self.numbers:
                            if length == self.numbers[(row, col)]:
                                arrows.append((row, col, direction, length))
                            elif length > self.numbers[(row, col)]:
                                break
                        else:
                            if length >= 2:  # 長さが2以上なら記録
                                arrows.append((row, col, direction, length))

                        length += 1
                        if had_arrow_head:
                            break

        return arrows
    def get_arrow_path(self, arrow):
        """
        矢印が通過するすべてのマスを列挙する
        :param arrow: (始点の行, 始点の列, 方向, 長さ)
        :return: 矢印が通過するすべてのマスのリスト
        """
        start_row, start_col, direction, length = arrow
        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        dr, dc = directions[direction]
        path = [(start_row + dr * i, start_col + dc * i) for i in range(length)]
        return set(path)

    def get_arrow_surroundings(self, arrow):
        """
        矢印の周囲のマスを列挙する
        :param arrow: (始点の行, 始点の列, 方向, 長さ)
        :return: 周囲のマスのリスト
        """
        path = self.get_arrow_path(arrow)
        surrounding = set()  # 重複を防ぐためセットを使用
        for row, col in path:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                adjacent = (row + dr, col + dc)
                if 0 <= adjacent[0] < self.rows and 0 <= adjacent[1] < self.cols:
                    surrounding.add(adjacent)

        # 矢印自体のマスを除外
        for cell in path:
            if cell in surrounding:
                surrounding.remove(cell)

        return set(surrounding)

    def get_arrow_extension(self, arrow):
        """
        矢印の先に黒ますか外周に至るまでのマスを列挙する
        :param arrow: (始点の行, 始点の列, 方向, 長さ)
        :return: 矢印の先にあるマスのリスト
        """
        start_row, start_col, direction, length = arrow
        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        dr, dc = directions[direction]
        end_row = start_row + dr * length
        end_col = start_col + dc * length

        extension = []
        while 0 <= end_row < self.rows and 0 <= end_col < self.cols:
            if self.board[end_row][end_col] == "■":  # 黒マスに到達
                #extension.append((end_row, end_col))
                break
            extension.append((end_row, end_col))
            end_row += dr
            end_col += dc

        return set(extension)
    
    def get_arrow_tip(self, arrow):
        """
        矢尻（arrowの終端の次のマス）を取得する
        :param arrow: (始点の行, 始点の列, 方向, 長さ)
        :return: 矢尻の座標 (row, col) または None（矢尻が盤面外の場合）
        """
        start_row, start_col, direction, length = arrow
        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        dr, dc = directions[direction]
        tip_row = start_row + dr * (length-1)
        tip_col = start_col + dc * (length-1)

        # 範囲外のチェック
        if 0 <= tip_row < self.rows and 0 <= tip_col < self.cols:
            return tip_row, tip_col
        return None  # 盤面外に矢尻がある場合
    def get_possible_arrows_dict(self):

        possible_arrows=self.enumerate_possible_arrows()
        possible_arrows_dict={arrow:{} for arrow in possible_arrows}
        
        id_dict={}
        for id,arrow in enumerate(possible_arrows):
            id_dict[id]=arrow
            possible_arrows_dict[arrow]["id"]=id
            possible_arrows_dict[arrow]["path_length"]=arrow[3]
            possible_arrows_dict[arrow]["arrow_path"]=self.get_arrow_path(arrow)
            possible_arrows_dict[arrow]["arrow_surroundings"]=self.get_arrow_surroundings(arrow)
            possible_arrows_dict[arrow]["arrow_extension"]=self.get_arrow_extension(arrow)
            possible_arrows_dict[arrow]["arrow_tip"]=self.get_arrow_tip(arrow)
        return id_dict,possible_arrows,possible_arrows_dict
    def get_ng_id_dict(self):
        id_dict,possible_arrows,possible_arrows_dict=self.get_possible_arrows_dict()
        ng_id_dict={}
        keys = list(possible_arrows_dict.keys())

        # 2重ループ
        for i, arrow1 in enumerate(keys):
            for arrow2 in keys[i + 1:]:  # key1より後のキーだけを対象にする
                arrow1_id=possible_arrows_dict[arrow1]["id"]
                arrow2_id=possible_arrows_dict[arrow2]["id"]
                # 矢印は重なってはいけない
                arrow1_path=possible_arrows_dict[arrow1]["arrow_path"]
                arrow2_path=possible_arrows_dict[arrow2]["arrow_path"]
                if len(arrow1_path&arrow2_path)!=0:
                    ng_id_dict.setdefault(arrow1_id,set()).add(arrow2_id)
                # 同じ長さの矢印があるマスをタテヨコに連続させてはいけません。
                path_length1=possible_arrows_dict[arrow1]["path_length"]
                path_length2=possible_arrows_dict[arrow2]["path_length"]
                if path_length1==path_length2:
                    arrow1_surroundings=possible_arrows_dict[arrow1]["arrow_surroundings"]
                    if len(arrow1_surroundings&arrow2_path)!=0:
                        ng_id_dict.setdefault(arrow1_id,set()).add(arrow2_id)

                # 同じ矢が向いている方向(矢羽→矢尻の方向)に、黒マスか外周に至るまで、他の矢印の矢尻があってはいけません
                arrow1_extension=possible_arrows_dict[arrow1]["arrow_extension"]
                arrow2_extension=possible_arrows_dict[arrow2]["arrow_extension"]
                
                arrow1_tip=possible_arrows_dict[arrow1]["arrow_tip"]
                arrow2_tip=possible_arrows_dict[arrow2]["arrow_tip"]
                if arrow2_tip in arrow1_extension:
                    ng_id_dict.setdefault(arrow1_id,set()).add(arrow2_id)
                if arrow1_tip in arrow2_extension:
                    ng_id_dict.setdefault(arrow1_id,set()).add(arrow2_id)
                # 矢尻のあるマスがタテヨコに連続させてはいけません。
                diff_arrow_tip=(arrow1_tip[0]-arrow2_tip[0])**2+(arrow1_tip[1]-arrow2_tip[1])**2
                if diff_arrow_tip==1:
                    ng_id_dict.setdefault(arrow1_id,set()).add(arrow2_id)

                
            
        # 全てのマスは1回通過する
        cell_id_dict={}
        for i, arrow1 in enumerate(keys):
            arrow1_path=possible_arrows_dict[arrow1]["arrow_path"]
            arrow1_id=possible_arrows_dict[arrow1]["id"]
            for cell in arrow1_path:
                cell_id_dict.setdefault(cell,set()).add(arrow1_id)
        return id_dict,possible_arrows,possible_arrows_dict,ng_id_dict,cell_id_dict
    def solve_board(self):
            
        id_dict,possible_arrows,possible_arrows_dict,ng_id_dict,cell_id_dict=self.get_ng_id_dict()
        variable_dict={}
        for k,v in possible_arrows_dict.items():
            variable_dict[v['id']]=Bool(f"x{v['id']}")
        solver = Solver()
        for k,v in ng_id_dict.items():
            for k0 in list(v):
                solver.add(Or(Not(variable_dict[k]), Not(variable_dict[k0])))


        
        for k,v0 in cell_id_dict.items():

            # 制約: リスト内の1つだけがTrue
            solver.add(Sum([If(variable_dict[v], 1, 0) for v in v0]) == 1)
        #check= solver.check()
        #print(check)
        is_hukusuukai=False
        ans_list1=[]
        ans_list2=[]
        constraints = solver.assertions()       
        print(len(constraints))
        if solver.check()==sat:
            model = solver.model()
            for key,var in  variable_dict.items():
                if model[var]:
                    ans_list1.append(id_dict[key])
                    
            print(ans_list1)
            #solver1=copy.deepcopy(solver)
            solver.add(Or([var != model[var] for var in  variable_dict.values()]))
     
            constraints = solver.assertions()       
            print(len(constraints))
            # 二つ目の解を探す
            if solver.check() == sat:
                is_hukusuukai=True
                model = solver.model()
                for key,var in  variable_dict.items():
                    if model[var]:
                        ans_list2.append(id_dict[key])
                print(ans_list2)
        
        return is_hukusuukai,ans_list1,ans_list2
