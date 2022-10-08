# coding: UTF-8
import pyxel
from random import *
from math import *
from enum import Enum, auto

WINDOW_WIDTH = 200
WINDOW_HEIGHT = 200

WALL_FREQUANCY = 40 #wallの頻度
INITIAL_DIFFICULTY = 1 #初期難易度
WALL_HOLE_RANGE = 20
WALL_HOLE_HEIGHT = 50
SINE_FREQUANCY = 10

class Mode(Enum):
    Title = auto()
    Main = auto()
    End = auto()

class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, fps=60, title="anwall")
        self.init()
        pyxel.load('./assets/anwall.pyxres')
        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def init(self):
        self.gamemode = Mode.Title
        self.cursor = 0
        self.r = 2
        self.x = 100
        self.y = WINDOW_HEIGHT//3
        self.vx = 0.6
        self.vy = 0.5
        self.g = 0.05
        self.walls = []
        self.score = 0
        self.items = []
        self.item_count = 0
        self.state = 0 #1は無敵状態
        self.state_count = 7
        self.upper = False

        self.difficulty = INITIAL_DIFFICULTY
        self.wall_freq = WALL_FREQUANCY
        self.wall_hole_range = WALL_HOLE_RANGE
        self.wall_hole_height = WALL_HOLE_HEIGHT
        self.sine_freq = SINE_FREQUANCY

        self.levels = ["BEGINNER", "AMATEUR", "PROFESSIONAL", "TUNNEL"]
        self.lines = [Line(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT), 7, [0, -1]) for _ in range(200)]

        
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_R):
            self.init()

        if self.gamemode == Mode.Title:
            self.update_title()
        elif self.gamemode == Mode.Main:
            self.update_main()
        elif self.gamemode == Mode.End:
            self.update_end()

    def update_title(self):
        if pyxel.btnp(pyxel.KEY_F):
            self.cursor += -1
            pyxel.play(3, 6)
        if pyxel.btnp(pyxel.KEY_J):
            self.cursor += 1
            pyxel.play(3, 6)

        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.cursor%4 == 0:                  #beginner
                self.difficulty += 0                #1
                self.wall_freq += 50                #100
                self.wall_hole_range += 0           #20
                self.wall_hole_height += 0          #50
                self.sine_freq += 0                 #10

            elif self.cursor%4 == 1:                #amatuer
                self.difficulty += 10               #11
                self.wall_freq += 40                #90
                self.wall_hole_range += 0           #20
                self.wall_hole_height += -10        #40
                self.sine_freq += 5                 #15

            elif self.cursor%4 == 2:                #professional
                self.difficulty += 30               #31
                self.wall_freq += 30                #80
                self.wall_hole_range += 0           #20
                self.wall_hole_height += -25        #25
                self.sine_freq += 15                #25
            else:                                   #tunnel
                self.difficulty += 50               #51
                self.wall_freq += 30                #80
                self.wall_hole_range += -5          #15
                self.wall_hole_height += -40        #10
                self.sine_freq += 0                 #10

            pyxel.play(3, 5)
            self.tmp_cursor = self.cursor
            self.gamemode = Mode.Main
        
        #lines
        for line in self.lines:
            line.update()
            line.revive()
            
    def update_main(self):
        pyxel.playm(1, loop=True)

        #player
        if not self.gamemode == Mode.End:
            if pyxel.btn(pyxel.KEY_F):
                self.x += -self.vx 
            if pyxel.btn(pyxel.KEY_J):
                self.x += self.vx 
            if self.item_count > 0:
                if pyxel.btnp(pyxel.KEY_H):
                    if self.state == 0:
                        pyxel.play(3, 8)
                        self.state = 1
                        self.item_count += -1
                    else:
                        pyxel.play(3, 8)
                        self.item_count += -1
                        self.state_count += 7

            if self.state == 1 and pyxel.frame_count%60 == 0:
                self.state_count += -1
            
            if self.state_count == 0:
                pyxel.play(3, 9)
                self.state = 0
                self.state_count = 7      

            if self.x <= 0:
                self.x = max(0, self.x)
            if self.x >= WINDOW_WIDTH:
                self.x = min(WINDOW_WIDTH, self.x)

            self.y += self.vy
            if pyxel.btn(pyxel.KEY_SPACE):
                self.upper = True
                self.vy += -self.g
            else:
                self.upper = False
                self.vy += self.g

            if self.y < 0:
                self.y = WINDOW_HEIGHT
            if self.y > WINDOW_HEIGHT:
                self.y = 0

            if self.vy >= 3:
                self.vy = min(3, self.vy)
            if self.vy <= -3:
                self.vy = max(-3, self.vy)
        
        #wall
        if not self.gamemode == Mode.End:
            if pyxel.frame_count%(self.wall_freq) == 0:
                wall_status = randint(1, 100)
                py = randint(WINDOW_HEIGHT//2 - 30 -self.wall_hole_range,WINDOW_HEIGHT//2+self.wall_hole_range - 30)
                ph = randint(40, 40+self.wall_hole_height)
                for i in range(self.difficulty):
                    self.walls.append(Wall(WINDOW_WIDTH + i, py, ph, wall_status)) 
            for wall in self.walls:
                wall.x += -self.vx 
                if wall.y <= 0:
                    wall.y = max(0, wall.y)
                if wall.y + wall.h >= WINDOW_HEIGHT:
                    wall.y = min(WINDOW_HEIGHT - wall.h, wall.y)
                if wall.status <= self.sine_freq:
                    wall.y += (wall.h//50)*sin(radians(2*pyxel.frame_count%360))
                
                if wall.x <= 0:
                    self.walls.pop(0)

        #item
        if not self.gamemode == Mode.End:
            if pyxel.frame_count % 600 == 0:
                self.items.append(Item(WINDOW_WIDTH, randint(0+100, WINDOW_WIDTH-100), 2, randint(0, 100)))
            for item in self.items:
                if item.state_num <= 20:
                    item.x += -self.vx 
                    item.y += sin(radians(2*pyxel.frame_count%360))**3
                elif item.state_num <= 50:
                    item.x += -self.vx + sin(radians(2*pyxel.frame_count%360))**3 
                    item.y += sin(radians(pyxel.frame_count%360))**3
                elif item.state_num <= 70:
                    item.x += -self.vx 
                    item.y += 0
                else:
                    item.x += -self.vx 
                    item.y += sin(radians(pyxel.frame_count%360)) if pyxel.frame_count%180<=90 else 0
                if item.x <= 0:
                    self.items.pop(self.items.index(item))
            
        #difficulty
        if not self.gamemode == Mode.End:
            if (pyxel.frame_count != 0) and pyxel.frame_count % 300 == 0:
                self.difficulty += 1

        #score
        if not self.gamemode == Mode.End:
            if (pyxel.frame_count != 0) and pyxel.frame_count%60 == 0:
                self.score += 1
            
    def update_end(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.init()

        #lines
        for line in self.lines:
            line.update()
            line.revive()

    def draw(self):
        pyxel.cls(0)

        if self.gamemode == Mode.Title:
            self.draw_title()
        elif self.gamemode == Mode.Main:
            self.draw_main()
        elif self.gamemode == Mode.End:
            self.draw_end()

    def draw_title(self):

        #lines
        for line in self.lines:
            line.draw()
        
        pyxel.rect(WINDOW_WIDTH//2 - 59, WINDOW_HEIGHT//2 - 59, 118, 58, 0)

        pyxel.blt(WINDOW_WIDTH//2 - 45, WINDOW_HEIGHT//2 - 38, 0, 0, 0, 16, 16)#A
        pyxel.blt(WINDOW_WIDTH//2 - 30, WINDOW_HEIGHT//2 - 38, 0, 16, 0, 16, 16)#N
        pyxel.blt(WINDOW_WIDTH//2 - 15, WINDOW_HEIGHT//2 - 38, 0, 32, 0, 16, 16)#W
        pyxel.blt(WINDOW_WIDTH//2 + 0, WINDOW_HEIGHT//2 - 38, 0, 0, 0, 16, 16)#A
        pyxel.blt(WINDOW_WIDTH//2 + 15, WINDOW_HEIGHT//2 - 38, 0, 48, 0, 16, 16)#L
        pyxel.blt(WINDOW_WIDTH//2 + 30, WINDOW_HEIGHT//2 - 38, 0, 48, 0, 16, 16)#L

        pyxel.rectb(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT//2 - 60, 120, 60, 10)
        pyxel.rectb(WINDOW_WIDTH//2 - 61, WINDOW_HEIGHT//2 - 61, 122, 62, 10)

        #level
        pyxel.text(WINDOW_WIDTH//2 - 50, 120, "BEGINNER", 8 if self.cursor%4 == 0 else 13)
        pyxel.text(WINDOW_WIDTH//2 - 50, 130, "AMATEUR", 8 if self.cursor%4 == 1 else 13)
        pyxel.text(WINDOW_WIDTH//2 - 50, 140, "PROFESSIONAL", 8 if self.cursor%4 == 2 else 13)
        pyxel.text(WINDOW_WIDTH//2 - 50, 150, "TUNNEL", 8 if self.cursor%4 == 3 else 13)

        #cursor
        pyxel.text(WINDOW_WIDTH//2 - 60, 120 + self.cursor%4 * 10, "->", 8)

        pyxel.text(WINDOW_WIDTH//2 - 50, 160, "SELECT LEVEL (USE F or J)", 7 if pyxel.frame_count%16 >= 8 else 6)
        pyxel.text(WINDOW_WIDTH//2 - 50, 170, "START TO SPACE_KEY", 7 if pyxel.frame_count%16 >= 8 else 6)

        #credit
        pyxel.text(WINDOW_WIDTH//2 - 50, 180, "PROCUDED BY ANCHY 2021", 13)

    def draw_main(self):

        #wall
        for wall in self.walls:
            pyxel.line(wall.x, 0, wall.x, wall.y, 7)
            pyxel.line(wall.x, wall.y + wall.h, wall.x, WINDOW_HEIGHT, 7)

        #player
        if self.upper:
            pyxel.circ(self.x, self.y, self.r, 8 if self.state == 0 else 9)
        else:
            pyxel.circ(self.x, self.y, self.r, 12 if self.state == 0 else 10)
        
        #item
        for item in self.items:
            pyxel.circ(item.x, item.y, item.r, 10)
            if sqrt((self.x - item.x)**2+(self.y - item.y)**2) <= item.r + self.r:
                pyxel.play(3, 7)
                self.items.pop(self.items.index(item))
                self.item_count += 1

        #item_message
        if self.score <= 2:
            pyxel.text(WINDOW_WIDTH//2 - 25, WINDOW_HEIGHT//2, 'YOU CAN USE ITEM', 7 if pyxel.frame_count%60 <= 30 else 12)
            pyxel.text(WINDOW_WIDTH//2 - 30, WINDOW_HEIGHT//2+10, 'IF YOU PRESS "H" KEY', 7 if pyxel.frame_count%60 <= 30 else 12)


        #hitting judge
        if not self.state == 1: #無敵じゃなかったら
            for wall in self.walls:
                y_points = wall.get_y()
                if self.judge(wall.x, y_points[0][0], y_points[0][1]) or self.judge(wall.x, y_points[1][0], y_points[1][1]):
                    pyxel.play(3, 4)
                    pyxel.stop(0)
                    self.score += self.item_count*2
                    self.gamemode = Mode.End
                
        #item_count
        for i in range(self.item_count):
            pyxel.circ(i*8+4, 3, 3, 10)

        #score
        pyxel.text(0, 10, f'SCORE: {self.score}', 10)

        #state_count
        if self.state == 1:
            pyxel.text(0, 20, f"INVINCIBLE: {self.state_count}", 8)

    def draw_end(self):

        #lines
        for line in self.lines:
            line.draw()

        pyxel.rect(WINDOW_WIDTH//2 - 69, WINDOW_HEIGHT//2 - 59, 138, 58, 0)

        pyxel.blt(WINDOW_WIDTH//2 - 64, WINDOW_HEIGHT//2 - 38, 0, 0, 16, 16, 16)#G
        pyxel.blt(WINDOW_WIDTH//2 - 48, WINDOW_HEIGHT//2 - 38, 0, 0, 0, 16, 16)#A
        pyxel.blt(WINDOW_WIDTH//2 - 32, WINDOW_HEIGHT//2 - 38, 0, 16, 16, 16, 16)#M
        pyxel.blt(WINDOW_WIDTH//2 - 16, WINDOW_HEIGHT//2 - 38, 0, 0, 32, 16, 16)#E
        pyxel.blt(WINDOW_WIDTH//2 + 0, WINDOW_HEIGHT//2 - 38, 0, 32, 16, 16, 16)#O
        pyxel.blt(WINDOW_WIDTH//2 + 16, WINDOW_HEIGHT//2 - 38, 0, 48, 16, 16, 16)#V
        pyxel.blt(WINDOW_WIDTH//2 + 32, WINDOW_HEIGHT//2 - 38, 0, 0, 32, 16, 16)#E
        pyxel.blt(WINDOW_WIDTH//2 + 48, WINDOW_HEIGHT//2 - 38, 0, 16, 32, 16, 16)#R

        pyxel.rectb(WINDOW_WIDTH//2 - 70, WINDOW_HEIGHT//2 - 60, 140, 60, 2)
        pyxel.rectb(WINDOW_WIDTH//2 - 71, WINDOW_HEIGHT//2 - 61, 142, 62, 2)

        pyxel.text(WINDOW_WIDTH//2 - 30, 140, f"YOUR SCORE: {self.score}", 10)
        pyxel.text(WINDOW_WIDTH//2 - 50, 150, f"YOUR LEVEL: {self.levels[self.tmp_cursor%4]}", 10)
        pyxel.text(WINDOW_WIDTH//2 - 35, 160, "RETRY TO PRESS_R", pyxel.frame_count%16)

    def judge(self, px1, py1, py2):
        if py1 <= self.y + self.r and self.y - self.r <= py2:
            if abs(px1 - self.x) <= self.r:
                return True
            else:
                return False
        else:
            return False


class Wall:
    def __init__(self, x, y, h, wall_status):
        self.x = x
        self.y = y
        self.h = h
        self.status = wall_status

    def get_y(self):
        return (0, self.y) ,(self.y+self.h, WINDOW_HEIGHT)

    def crash(self):
        self.x = WINDOW_WIDTH

class Line:
    def __init__(self, x, y, c, vec):
        self.x = x
        self.y = y
        self.c = c
        self.vec = vec

    def update(self):
        self.x += self.vec[0]
        self.y += self.vec[1]

    def draw(self):
        pyxel.line(self.x, self.y, self.x+self.vec[0], self.y+self.vec[1], self.c)

    def revive(self):
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        if self.y > WINDOW_HEIGHT:
            self.y = 0

class Item:
    def __init__(self, x, y, r, state_num):
        self.x = x
        self.y = y
        self.r = r
        self.state_num = state_num

App()