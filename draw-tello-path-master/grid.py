from turtle import Turtle
from turtle import Screen


WIDTH,HEIGHT=800,700 #Same as main screen.setup()
START_POSITION = (-370,300)

class Grid(Turtle):
    def __init__(self):
        super().__init__()
        self.draw_grid()

    def draw_grid(self):

        self.x=-334 # moves pen by x = -334
        self.y=248 # moves pen by y = 248
        self.penup()
        self.pencolor("lightgreen")
        self.speed("fast")
        self.hideturtle()
        # self.hideturtle()
        # #Horizontal
        for grid in range(0,21):
            self.goto(self.x,self.y)
            self.pendown()
            self.forward(500)
            self.y -= 25 # intervals of 25 pixels between each grid
            self.penup()
        """reset x and y values"""
        self.x = -334
        self.y = 248
        #Vertical
        self.goto(self.x, self.y)
        self.right(90)
        for grid in range(0,21):
            self.goto(self.x,self.y)
            self.pendown()
            self.forward(500)
            self.x += 25 # intervals of 25 pixels between each grid
            self.penup()
        self.hideturtle()

    def clear_grid(self):
        self.clear()