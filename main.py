import numpy as np
import random
import time
import math
import copy
import time as tt
import sys
from numba import jit

sys.setrecursionlimit(30000)

standard_board = [[1, 8, 3, 7, 7, 3, 8, 1], [8, 3, 2, 5, 5, 2, 3, 8], [3, 2, 6, 6, 6, 6, 2, 3],
                  [7, 5, 6, 4, 4, 6, 5, 7], [7, 5, 6, 4, 4, 6, 5, 7], [3, 2, 6, 6, 6, 6, 2, 3],
                  [8, 3, 2, 5, 5, 2, 3, 8], [1, 8, 3, 7, 7, 3, 8, 1]]
COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(0)
direction = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]


def eval_board(tuple):
    return standard_board[tuple[0]][tuple[1]]


@jit
def out_of_bound(x, y, size):
    if x < 0 or y < 0 or x >= size or y >= size:
        return True
    return False


def possible_positions(board, tile, size):
    positions = []
    for i in range(0, size):
        for j in range(0, size):
            if board[i][j] != 0:
                continue
            if updateBoard(board, tile, i, j, checkonly=True) > 0:
                positions.append((i, j))
    return positions


def updateBoard(board, tile, i, j, checkonly=False):
    reversed_stone = 0

    board[i][j] = tile
    if tile == 1:
        change = -1
    else:
        change = 1

    need_turn = []
    for xdirection, ydirection in direction:
        x, y = i, j
        x += xdirection
        y += ydirection
        if onBoard(x, y) and board[x][y] == change:
            x += xdirection
            y += ydirection
            if not onBoard(x, y):
                continue
            # 涓€鐩磋蛋鍒板嚭鐣屾垨涓嶆槸瀵规柟妫嬪瓙鐨勪綅缃�
            while board[x][y] == change:
                x += xdirection
                y += ydirection
                if not onBoard(x, y):
                    break
            # 鍑虹晫浜嗭紝鍒欐病鏈夋瀛愯缈昏浆
            if not onBoard(x, y):
                continue
            # 鏄嚜宸辩殑妫嬪瓙锛屼腑闂寸殑鎵€鏈夋瀛愰兘瑕佺炕杞�
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    # 鍥炲埌浜嗚捣鐐瑰垯缁撴潫
                    if x == i and y == j:
                        break
                    # 闇€瑕佺炕杞殑妫嬪瓙
                    need_turn.append([x, y])
    # 灏嗗墠闈复鏃舵斁涓婄殑妫嬪瓙鍘绘帀锛屽嵆杩樺師妫嬬洏
    board[i][j] = 0  # restore the empty space
    # 娌℃湁瑕佽缈昏浆鐨勬瀛愶紝鍒欒蛋娉曢潪娉曘€傜炕杞鐨勮鍒欍€�
    for x, y in need_turn:
        if not checkonly:
            board[i][j] = tile
            board[x][y] = tile  # 缈昏浆妫嬪瓙
        reversed_stone += 1
    return reversed_stone


@jit
def judge(tuple):
    if tuple[0] == 0 and tuple[1] == 0:
        return True
    if tuple[0] == 0 and tuple[1] == 7:
        return True
    if tuple[0] == 7 and tuple[1] == 0:
        return True
    if tuple[0] == 7 and tuple[1] == 7:
        return True
    return False


# don't change the class name
@jit
def onBoard(x, y):
    return 0 <= x < 8 and 0 <= y < 8


def check_win(chessboard, size, color):
    cnt = 0
    for i in range(0, size):
        for j in range(0, size):
            if chessboard[i][j] == color:
                cnt += 1
    return cnt


# def random_race(chessboard, size, color):
#     a = possible_positions(chessboard, color, size)
#     b = possible_positions(chessboard, -color, size)
#     if len(a) == 0 and len(b) == 0:
#         tmp = check_win(chessboard, size, color)
#         if tmp >= 32:
#             return color
#         else:
#             return -color
#     elif len(a) == 0:
#         tp = b[len(b) - 1]
#         updateBoard(chessboard, -color, tp[0], tp[1])
#         random_race(chessboard, size, color)
#     else:
#         tp = a[len(a) - 1]
#         updateBoard(chessboard, color, tp[0], tp[1])
#         random_race(chessboard, size, -color)
#     return color
def random_race(chessboard, size, color):
    a = possible_positions(chessboard, color, size)
    if len(a) == 0:
        b = possible_positions(chessboard, -color, size)
        if len(b) == 0:
            return check_win(chessboard, size, color) <= 32
        else:
            ans = (0, 0)
            min = -1
            for tp in b:
                if eval_board(tp) > min:
                    min = eval_board(tp)
                    ans = tp
            updateBoard(chessboard, -color, ans[0], ans[1])
            random_race(chessboard, size, color)
    else:
        ans = (0, 0)
        min = -1
        for tp in a:
            if eval_board(tp) > min:
                min = eval_board(tp)
                ans = tp
        updateBoard(chessboard, color, ans[0], ans[1])
        random_race(chessboard, size, -color)
    return True


class mcts_node:
    def __init__(self, chessboard, try_times, success, color):
        self.chessboard = chessboard
        self.t = try_times
        self.s = success
        self.child = []
        self.size = len(chessboard)
        self.color = color
        self.parent = None

    def back_reward(self, color):
        self.t += 1
        if self.color == color:
            self.s += 1
        if self.parent is not None:
            self.parent.back_reward(color)

    def expand(self):
        l = possible_positions(self.chessboard, self.color, self.size)
        if len(l) != 0:
            for p in l:
                board = copy.deepcopy(self.chessboard)
                updateBoard(board, self.color, p[0], p[1])
                tmp = mcts_node(board, 0, 0, -self.color)
                self.child.append(tmp)
                tmp.parent = self
            return True
        # else:
        #     self.color = -self.color
        #     self.expand()
        return False

    def cal_value(self, times):
        t = self.t
        if self.t == 0:
            t = 0.00000000001
        return self.s / t + 2 * math.sqrt(2 * math.log(times) / t)


def same(ch1, ch2, size):
    for i in range(0, size):
        for j in range(0, size):
            if ch1[i][j] != ch2[i][j]:
                return False
    return True


class AI(object):
    # chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        # You are white or black
        self.color = color
        # the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need to add your decision to your candidate_list. The system will get the end of your candidate_list as
        # your decision.
        self.candidate_list = []
        self.last = None

    # The input is the current chessboard. Chessboard is a numpy array.

    def go(self, chessboard):
        # self.find_position(chessboard)
        global root
        global total_cnt
        total_cnt = 1
        if self.last is None:
            root = mcts_node(chessboard, 0, 0, self.color)
            root.expand()
        else:
            flag = False
            root = self.last
            for node in root.child:
                if same(node.chessboard, chessboard, self.chessboard_size):
                    root = node
                    total_cnt = root.t
                    print(total_cnt)
                    flag = True
            if not flag:
                self.last = None
                root = mcts_node(chessboard, 0, 0, self.color)
                root.expand()
        self.candidate_list = possible_positions(chessboard, self.color, self.chessboard_size)
        start = time.time()
        while time.time() - start < 4.5:
            total_cnt += 1
            find_path(root, total_cnt)
        max = 0
        # for c in root.child:
        #     print()
        #     for i in range(0, self.chessboard_size):
        #         print(c.chessboard[i])
        for node in root.child:
            if node.s / node.t > max:
                max = node.s / node.t
                choose = node
                if not judge(decide(chessboard, choose.chessboard, self.chessboard_size)):
                    self.candidate_list.append(decide(chessboard, choose.chessboard, self.chessboard_size))
                    self.last = node
                    print(node.t)
        # for i in range(0, self.chessboard_size):
        #     for j in range(0, self.chessboard_size):
        #         if chessboard[i][j] == 0 and choose.chessboard[i][j] != 0:
        #             self.candidate_list.append((i, j))
        #             break

        if len(self.candidate_list) != 0 and judge(self.candidate_list[len(self.candidate_list) - 1]):
            for tp in self.candidate_list:
                if not judge(tp):
                    self.candidate_list.append(tp)
                    break

    def find_position(self, chessboard):
        self.candidate_list.clear()
        idx = np.where(chessboard == COLOR_NONE)
        idx = list(zip(idx[0], idx[1]))
        for x, y in idx:
            choose = False
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x_new = x + dx
                    y_new = y + dy
                    if out_of_bound(x_new, y_new, self.chessboard_size) or (dx == 0 and dy == 0):
                        continue
                    enemy = -self.color
                    valid = False
                    while not out_of_bound(x_new, y_new, self.chessboard_size) and chessboard[x_new][y_new] == enemy:
                        x_new += dx
                        y_new += dy
                        valid = True
                        if out_of_bound(x_new, y_new, self.chessboard_size):
                            break
                    if out_of_bound(x_new, y_new, self.chessboard_size) or chessboard[x_new][y_new] != self.color:
                        valid = False
                    if valid:
                        choose = True
                if choose:
                    self.candidate_list.append((x, y))
        if len(self.candidate_list) == 0:
            return


def is_leaf(node):
    return len(node.child) == 0


def decide(ch1, ch2, size):
    for i in range(0, size):
        for j in range(0, size):
            if ch1[i][j] == 0 and ch2[i][j] != 0:
                return i, j


def find_path(root, time):
    choose = root
    while not is_leaf(choose):
        max = 0
        for node in choose.child:
            if node.cal_value(time) > max:
                max = node.cal_value(time)
                choose = node
    if is_leaf(choose) and choose.t == 0:
        chess = copy.deepcopy(root.chessboard)
        judge = random_race(chess, choose.size, choose.color)
        if judge:
            choose.back_reward(choose.color)
        else:
            choose.back_reward(-choose.color)
    elif is_leaf(choose):
        if choose.expand():
            find_path(choose, time)


if __name__ == "__main__":

    a = AI(8, -1, 5)
    chessboard = []
    for i in range(0, 8):
        chessboard.append([])
        for j in range(0, 8):
            chessboard[i].append(0)
    #
    chessboard[3][3] = -1
    chessboard[3][4] = 1
    chessboard[4][3] = 1
    chessboard[4][4] = 1
    chessboard[4][5] = 1
    # for i in range(0, 8):
    #     chessboard[i][i] = 1
    # chessboard[3][4] = -1
    # ce = [[0] * 8 for i in range(8)]
    # ce[0] = [0, -1, 0, 1, 0, 1, 0, 0]
    # ce[1] = [1, -1, 1, 1, 1, 1, -1, 1]
    # ce[2] = [1, 1, -1, 1, -1, 1, 1, 0]
    # ce[3] = [1, -1, 1, -1, -1, 1, 1, -1]
    # ce[4] = [1, 1, 1, -1, -1, 1, 1, -1]
    # ce[5] = [1, 1, 1, 1, 1, -1, 1, -1]
    # ce[6] = [1, 0, 1, -1, -1, 1, -1, -1]
    # ce[7] = [0, 1, 1, 1, 1, 1, 1, -1]
    a.go(chessboard)
    print(a.candidate_list[len(a.candidate_list) - 1])
