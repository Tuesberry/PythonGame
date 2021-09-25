import tkinter as tk
import random
import math
import numpy as np
from numpy.linalg import norm

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1/math.sqrt(2), -1/math.sqrt(2)]  #방향벡터의 크기 1
        self.speed = 10

        # 문제1. ball2.png로 변경하기
        self.filename = tk.PhotoImage(file="ball2.png")
        item = canvas.create_image(x,y,anchor = tk.CENTER, image = self.filename)

        super(Ball, self).__init__(canvas, item)

    def get_position(self):
        pos = super().get_position()
        x = pos[0]
        y = pos[1]
        coords = [x-self.radius, y-self.radius, x+self.radius, y+self.radius]
        return coords

    def get_center(self):
        return super().get_position()

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def calc_intersection(self, game_objects):
        # collide
        # 공 센터 x,y 좌표
        ball_center = self.get_center()
        ball_x = ball_center[0]
        ball_y = ball_center[1]
        
        # 교점 리스트
        intersection_point = []

        # 교점 구하기
        for game_object in game_objects:
            coords = game_object.get_position()
            for i in range(0,4):
                if i == 0 or i == 2:
                    # x좌표인 경우 y^2 + 2by + c = 0
                    b = -1 * ball_y
                    c = pow((coords[i]-ball_x),2) + pow(ball_y,2) - pow(self.radius,2)
                    # 판별식
                    judge = pow(b, 2) - c
                    if judge >= 0 :
                        # 근이 2개 or 중근
                        y = [-1 * b + math.sqrt(pow(b,2)-c), -1 * b - math.sqrt(pow(b,2)-c)]
                        for pos_y in y:
                            if ball_y - self.radius <= pos_y and pos_y <= ball_y + self.radius and coords[1] <= pos_y and pos_y <= coords[3]:
                                # 교점 추가
                                isExist = False
                                pos = [coords[i], pos_y]
                                for point in intersection_point:
                                    if pos == point:
                                        isExist = True
                                if isExist == False:
                                    intersection_point.append(pos) 
                else:
                    # y좌표인 경우 ax^2 + 2bx = c = 0
                    b = -1 * ball_x
                    c = pow((coords[i]-ball_y),2) + pow(ball_x,2) - pow(self.radius,2)
                    # 판별식
                    judge = pow(b,2) - c
                    if judge >= 0 :
                        # 근이 2개 or 중근
                        x = [-1 * b + math.sqrt(pow(b,2)-c), -1 * b - math.sqrt(pow(b,2)-c)]
                        for pos_x in x:
                            if ball_x - self.radius <= pos_x and pos_x <= ball_x + self.radius and coords[0] <= pos_x and pos_x <= coords[2]:
                                # 교점 추가
                                isExist = False
                                pos = [pos_x, coords[i]]
                                for point in intersection_point:
                                    if pos == point:
                                        isExist = True
                                if isExist == False:
                                    intersection_point.append(pos)
        return intersection_point

    @staticmethod
    def normalize(vec):
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm

    def collide(self, game_objects):  
        #교점 구하기
        intersection_point = self.calc_intersection(game_objects)  

        if len(game_objects) >= 1 and len(intersection_point) > 0:
            if len(intersection_point) == 1:
                intersection_point = intersection_point[0]
                
                #이전 방향
                before_vec = np.array(self.direction)

                #법선 벡터 구하기
                normvec = np.array([[0,-1],[1,0]]).dot(np.transpose(before_vec))

                #새로운 방향 벡터 구하기
                new_direction = before_vec * -1
                new_direction = Ball.normalize(new_direction)
                new_direction = new_direction.tolist()
            elif len(intersection_point) > 1 :
                intersection_vec = np.array([intersection_point[0][0]-intersection_point[1][0],intersection_point[0][1]-intersection_point[1][1]])

                #2개의 법선 벡터
                normvec1 = np.array([[0,-1],[1,0]]).dot(np.transpose(intersection_vec)) #+90
                normvec2 = np.array([[0,1],[-1,0]]).dot(np.transpose(intersection_vec)) #-90
                normvec1 = np.transpose(normvec1)
                normvec2 = np.transpose(normvec2)

                #이전 방향
                before_vec = np.array(self.direction)

                #법선 벡터와 교점의 중심에서 물체의 중심을 잇는 벡터와의 각도
                intersection_center_point = [(intersection_point[0][0]+intersection_point[1][0])/2, (intersection_point[0][1]+intersection_point[1][1])/2] #교점의 중심
                game_object = game_objects[0]
                game_object_coords = game_object.get_position()
                gameobject_center_point = [(game_object_coords[0]+game_object_coords[2])/2, (game_object_coords[1]+game_object_coords[3])/2] #오브젝트의 중심
                from_intersection_to_center_vec = [gameobject_center_point[0]-intersection_center_point[0],gameobject_center_point[1]-intersection_center_point[1]] #교점에서 오브젝트 까지 벡터
                from_intersection_to_center_vec = np.array(from_intersection_to_center_vec)
                normvec1_degree = math.acos(from_intersection_to_center_vec.dot(normvec1)/(np.sqrt(from_intersection_to_center_vec.dot(from_intersection_to_center_vec))*np.sqrt(normvec1.dot(normvec1))))
                normvec2_degree = math.acos(from_intersection_to_center_vec.dot(normvec2)/(np.sqrt(from_intersection_to_center_vec.dot(from_intersection_to_center_vec))*np.sqrt(normvec2.dot(normvec2))))
                
                #새로운 방향 벡터 구하기
                new_direction = np.array([0,0])
                if normvec1_degree <= normvec2_degree:
                    #normvec2가 법선벡터가 된다.
                    normvec = Ball.normalize(normvec2)
                    #normvec = normvec2
                else :
                    #normvec1이 법선벡터가 된다.
                    normvec = Ball.normalize(normvec1)
                    #normvec = normvec1
                new_direction = 2 * (-1 * before_vec).dot(normvec) * normvec + before_vec
                new_direction = Ball.normalize(new_direction)
                new_direction = new_direction.tolist()

            #법선벡터와 충돌 전의 진행 방향과의 사잇각이 90도 이하인 경우 충돌 반응 안함
            norm_before_degree = math.acos(before_vec.dot(normvec)/(np.sqrt(before_vec.dot(before_vec))*np.sqrt(normvec.dot(normvec))))
            if math.degrees(norm_before_degree) > 90 :
                # 충돌 반응함
                self.direction = new_direction
                for game_object in game_objects:
                    if isinstance(game_object, Brick):
                        game_object.hit()

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='blue')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.level = 1
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        self.setup_level()

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))

    #문제2. setup_level
    def setup_level(self):
        blocklist = [0,1,2,3,4,5,6,7]
        if self.level == 1 :
            NumOfBlock = random.randint(1,8)
            random.shuffle(blocklist)
            for x in range(0,NumOfBlock):
                location = 5 + blocklist[x] * 75 + 37.5
                self.add_brick(location, 50, 1)
        else :
            for n in range(0,2):
                NumOfBlock = random.randint(1,8)
                random.shuffle(blocklist)
                for x in range(0,NumOfBlock):
                    location = 5 + blocklist[x] * 75 + 37.5
                    if n == 0:
                        self.add_brick(location, 50, 2)
                    else :
                        self.add_brick(location, 70, 1)

    def setup_game(self):
           self.add_ball()
           self.update_lives_text()
           self.text = self.draw_text(300, 200,
                                      'Press Space to start')
           self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s Level: %s' % (self.lives, self.level)
        if self.hud is None:
            self.hud = self.draw_text(80, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            if self.level == 1:
                self.level = 2
                self.setup_game()
                self.setup_level()
            elif self.level == 2: 
                self.ball.speed = None
                self.draw_text(300, 200, 'You win!')
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game Over')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hello, Pong!')
    game = Game(root)
    game.mainloop()
