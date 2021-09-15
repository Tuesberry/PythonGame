import random
import os
import time
import msvcrt

class Snake:
    def __init__(self, n):
        self.length = n
        self.head = []  #head, tail info save
        self.tail = []

class SnakeGame:
    direction = {"LEFT":-2, "DOWN":-1, "NON_DIR":0, "UP":1, "RIGHT": 2}
    sprite = {"EMPTY":0, "BODY":1, "HEAD":2, "FOOD":3}
    element = {"SPRITE":0, "DIRECTION":1}

    def __init__(self, w, h, length, delay):
        self.W = w
        self.H = h
        self.initLen = length
        self.snake = Snake(length)
        self.delay = delay
        self.board = [[[0]*2 for x in range(self.W)]for y in range(self.H)]
        self.snake.head = [self.H//2, self.snake.length-1]
        self.snake.tail = [self.H//2, 0]

        # Snake Location Initialization on board
        for i in range(0, self.snake.length):
            self.board[self.H//2][i][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["BODY"]
            self.board[self.H//2][i][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["RIGHT"]
        
        self.board[self.H//2][self.snake.length-1][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["HEAD"]
        self.board[self.H//2][self.snake.length-1][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["RIGHT"]

        # Food Location
        x = random.randint(0, self.W-1)
        y = random.randint(0, self.H-1)

        while self.board[y][x][SnakeGame.element["SPRITE"]] != SnakeGame.sprite["EMPTY"]:
            x = random.randint(0, self.W-1)
            y = random.randint(0, self.H-1)

        self.board[y][x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["FOOD"]

    def DrawScene(self):
        os.system('cls||clear')
        for x in range(0, self.W+2):
            print("=", end="")
        print("")

        for y in range(0, self.H):
            print("|", end="")
            for x in range(0, self.W):
                if self.board[y][x][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["BODY"]:
                    print("+", end="")
                elif self.board[y][x][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["HEAD"]:
                    print("@", end="")
                elif self.board[y][x][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["FOOD"]:
                    print("*", end="")
                else:
                    print(" ", end="")
            print("|")

        for x in range(0, self.W+2):
            print("=", end="")
        print("")

    @staticmethod
    def GetDirection():
        rtn = SnakeGame.direction["NON_DIR"]
        msvcrt.getch()  #Read a keypress and return the resulting character as a byte string.
        ch = msvcrt.getch().decode()
        if ch == chr(72):
            print("UP")
            rtn = SnakeGame.direction["UP"]
        elif ch == chr(75):
            print("LEFT")
            rtn = SnakeGame.direction["LEFT"]
        elif ch == chr(77):
            print("RIGHT")
            rtn = SnakeGame.direction["RIGHT"]
        elif ch == chr(80):
            print("DOWN")
            rtn = SnakeGame.direction["DOWN"]

        return rtn

    def PrintBoard(self):
        for y in range(0, self.H):
            for x in range(0, self.W):
                print(self.board[y][x][SnakeGame.element["DIRECTION"]], end='')
            print('')
            
    def GameLoop(self):
        self.DrawScene()
        current = SnakeGame.direction["NON_DIR"]
        while True:
            start = time.time()
            while(time.time() - start) <= self.delay/1000:
                if msvcrt.kbhit():
                    current = SnakeGame.GetDirection()
            
            #codes 실습1
            #위치 확인
            beforeDir_x = self.snake.head[1]
            beforeDir_y = self.snake.head[0]

            #이전 위치 방향
            before_dir = self.board[beforeDir_y][beforeDir_x][SnakeGame.element["DIRECTION"]]

            if -1*before_dir == current or current == SnakeGame.direction["NON_DIR"]:
                current = before_dir

            #이전 머리 위치 -> 몸통
            self.board[beforeDir_y][beforeDir_x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["BODY"]
            self.board[beforeDir_y][beforeDir_x][SnakeGame.element["DIRECTION"]] = current

            #새로운 머리 위치 결정
            if current == SnakeGame.direction["RIGHT"] :
                newDir_x = beforeDir_x + 1
                newDir_y = beforeDir_y
            elif current == SnakeGame.direction["LEFT"] :
                newDir_x = beforeDir_x - 1
                newDir_y = beforeDir_y
            elif current == SnakeGame.direction["UP"] :
                newDir_x = beforeDir_x
                newDir_y = beforeDir_y - 1
            elif current == SnakeGame.direction["DOWN"] :
                newDir_x = beforeDir_x
                newDir_y = beforeDir_y + 1
            
            
            #머리가 경계, 몸통과 충돌 -> 종료
            if newDir_y >= self.H or newDir_y < 0 or newDir_x >= self.W or newDir_x < 0:
                print("GAMEOVER")
                break
            elif self.board[newDir_y][newDir_x][SnakeGame.element["SPRITE"]] != SnakeGame.sprite["EMPTY"] and self.board[newDir_y][newDir_x][SnakeGame.element["SPRITE"]] != SnakeGame.sprite["FOOD"]:
                print("GAMEOVER")
                break

            #먹이 먹으면 상태 저장
            if self.board[newDir_y][newDir_x][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["FOOD"]:
                bIsFood = True
            else :
                bIsFood = False

            #머리 저장
            self.board[newDir_y][newDir_x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["HEAD"]
            self.board[newDir_y][newDir_x][SnakeGame.element["DIRECTION"]] = current
            self.snake.head = [newDir_y, newDir_x]

            #꼬리
            if bIsFood == False:
                tail_x = self.snake.tail[1]
                tail_y = self.snake.tail[0]
                tail_current_dir = self.board[tail_y][tail_x][SnakeGame.element["DIRECTION"]]
                self.board[tail_y][tail_x][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["NON_DIR"]
                self.board[tail_y][tail_x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["EMPTY"]

                #다음 꼬리 위치 지정
                if tail_current_dir == SnakeGame.direction["RIGHT"]:
                    nextTail_x = tail_x + 1
                    nextTail_y = tail_y
                elif tail_current_dir == SnakeGame.direction["LEFT"]:
                    nextTail_x = tail_x - 1
                    nextTail_y = tail_y
                elif tail_current_dir == SnakeGame.direction["UP"]:
                    nextTail_x = tail_x 
                    nextTail_y = tail_y - 1
                else :
                    nextTail_x = tail_x 
                    nextTail_y = tail_y + 1

                self.snake.tail = [nextTail_y, nextTail_x]

            else:
                #길이 추가
                self.snake.length += 1

                #먹이 생성
                x = random.randint(0, self.W-1)
                y = random.randint(0, self.H-1)

                while self.board[y][x][SnakeGame.element["SPRITE"]] != SnakeGame.sprite["EMPTY"]:
                    x = random.randint(0, self.W-1)
                    y = random.randint(0, self.H-1)

                self.board[y][x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["FOOD"]

            self.DrawScene()
            print("Score: {}".format(self.snake.length - self.initLen))


if __name__ == '__main__':
    game = SnakeGame(60, 24, 4, 300)
    game.GameLoop()