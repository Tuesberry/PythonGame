import tkinter as tk
import numpy as np
from tkinter import messagebox

class Game(tk.Frame):
    element = {"SPRITE":0, "COUNT":1, "CLICK": 2}
    click = {"NONE":0, "OPEN":1, "MEMO":2}
    sprite = {"EMPTY":0, "MINE":1}

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.square = 30
        self.width = 9 * self.square
        self.height = 9 * self.square
        self.canvas = tk.Canvas(self, bg='#aaaaff', width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()
        self.setup_game(9, 9)

        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff = 0)
        filemenu.add_command(label="9*9", command = lambda : self.begin(9, 9))
        filemenu.add_command(label="16*16", command = lambda : self.begin(16, 16))
        filemenu.add_command(label="16*30", command = lambda : self.begin(16, 30))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        master.config(menu=menubar)

        self.canvas.bind('<Button-1>', self.left_button)
        self.canvas.bind('<Button-3>', self.right_button)

    def left_button(self, event):
        x = event.x//self.square
        y = event.y//self.square
        self.CheckMine(x,y)

    def right_button(self, event):
        x = event.x//self.square
        y = event.y//self.square
        self.Memo(x,y)

    def begin(self, numOfRow, numOfCol):
        # Resize and Clear Canvas
        self.width = numOfCol * self.square
        self.height = numOfRow * self.square
        self.canvas.config(width = self.width, height = self.height)
        self.canvas.delete('all')

        # Setup_game
        self.setup_game(numOfRow, numOfCol)

    def setup_game(self, numOfRow, numOfCol):
        # board 초기화
        self.board = [[[0]*3 for i in range(numOfCol)] for k in range(numOfRow)]
        
        if numOfCol == 9 :
            # 9*9인 경우
            numOfMine = 10
        elif numOfCol == 16 :
            # 16*16인 경우
            numOfMine = 40
        elif numOfCol == 30 :
            # 30*16인 경우
            numOfMine = 99
            
        # mine 위치 랜덤 설정
        Count = 0
        while Count < numOfMine :
            random_y = np.random.randint(numOfRow)
            random_x = np.random.randint(numOfCol)
            if self.board[random_y][random_x][Game.element["SPRITE"]] == Game.sprite["EMPTY"]:
                self.board[random_y][random_x][Game.element["SPRITE"]] = Game.sprite["MINE"]
                Count += 1
                
        # Counting
        for x in range(0, numOfCol):
            for y in range(0, numOfRow):
                # sprite가 mine이면 count를 하지 않는다
                if self.board[y][x][Game.element["SPRITE"]] == Game.sprite["MINE"]:
                    continue
                # 사방을 체크한다
                numOfMine = 0
                for check_x in range(x-1,x+2):
                    for check_y in range(y-1,y+2):
                        if check_x == x and check_y == y :
                            continue
                        elif check_x < 0 or check_x >= numOfCol or check_y < 0 or check_y >= numOfRow :
                            continue
                        elif self.board[check_y][check_x][Game.element["SPRITE"]] == Game.sprite["MINE"] :
                            numOfMine += 1
                self.board[y][x][Game.element["COUNT"]] = numOfMine

        # Create Line
        for x in range(0, numOfCol+1):
            pos = x*self.square
            self.canvas.create_line(pos,0,pos,self.square*numOfRow, fill='#000000')
        for y in range(0, numOfRow+1):
            pos = y*self.square
            self.canvas.create_line(0,pos, self.square*numOfCol, pos, fill='#000000')

    def CheckClear(self):
        numOfCol = self.width // self.square
        numOfRow = self.height // self.square

        for x in range(0,numOfCol):
            for y in range(0,numOfRow):
                if self.board[y][x][Game.element["CLICK"]] != Game.click["OPEN"] :
                    if self.board[y][x][Game.element["SPRITE"]] == Game.sprite["EMPTY"]:
                        # 클릭X and 빈 경우
                        return

        messagebox.showinfo('Win', 'You win!')
        self.begin(numOfRow, numOfCol)

    def CheckMine(self, x, y):
        numOfCol = self.width // self.square
        numOfRow = self.height // self.square

        # 클릭 후 mine인지, 아닌지 
        if self.board[y][x][Game.element["CLICK"]] == Game.click["NONE"] :
            #아직 오픈 되지 않은 곳인 경우
            if self.board[y][x][Game.element["SPRITE"]] == Game.sprite["MINE"] :
                #mine인 경우 게임 오버
                messagebox.showinfo('GameOver', 'GameOver!')
                self.begin(numOfRow, numOfCol)
            elif self.board[y][x][Game.element["COUNT"]] == 0 :
                self.detect_region(x,y)
                self.CheckClear()
            else :
                self.board[y][x][Game.element["CLICK"]] = Game.click["OPEN"]
                x_pos = x*self.square + self.square/2
                y_pos = y*self.square + self.square/2
                text = self.board[y][x][Game.element["COUNT"]]
                self.canvas.create_text(x_pos,y_pos,text=text,fill="black")
                self.CheckClear()

    def detect_region(self, x, y):
        numOfCol = self.width // self.square
        numOfRow = self.height // self.square

        for pos_x in range(x-1, x+2):
            for pos_y in range(y-1, y+2):
                if pos_x < 0 or pos_y < 0 or pos_x >= numOfCol or pos_y >= numOfRow :
                    continue
                if self.board[pos_y][pos_x][Game.element["CLICK"]] == Game.click["NONE"] :
                    #아직 오픈되지 않은 경우
                    self.board[pos_y][pos_x][Game.element["CLICK"]] = Game.click["OPEN"]
                    text_x_pos = pos_x*self.square + self.square/2
                    text_y_pos = pos_y*self.square + self.square/2
                    text = self.board[pos_y][pos_x][Game.element["COUNT"]]
                    self.canvas.create_text(text_x_pos,text_y_pos,text=text,fill="black")
                    
                    if self.board[pos_y][pos_x][Game.element["COUNT"]] == 0 :
                        self.detect_region(pos_x, pos_y)

    def Memo(self, x, y):
        if self.board[y][x][Game.element["CLICK"]] == Game.click["NONE"] :
            self.board[y][x][Game.element["CLICK"]] = Game.click["MEMO"]
            x_pos = x*self.square + self.square/2
            y_pos = y*self.square + self.square/2
            memo_tag = str(x_pos) + '*' + str(y_pos)
            self.canvas.create_text(x_pos,y_pos,text='X',fill="red",tags=memo_tag)
        elif self.board[y][x][Game.element["CLICK"]] == Game.click["MEMO"] :
            self.board[y][x][Game.element["CLICK"]] = Game.click["NONE"]
            x_pos = x*self.square + self.square/2
            y_pos = y*self.square + self.square/2
            memo_tag = str(x_pos) + '*' + str(y_pos)
            self.canvas.delete(memo_tag)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hello, Mine!')
    game = Game(root)
    game.mainloop()