class Player:

    def __init__(self, startX, startY, lives=3, size=10):
        self.lives = lives
        self.size  = size
        self.x     = startX
        self.y     = startY
        self.dx    = 0
        self.dy    = 0
        self.hit   = False

    def moveX(self, fps):
        self.x += ( self.dx / fps )

    def moveY(self, fps):
        self.y += ( self.dy / fps )

    def removeLife(self):
        self.lives -= 1

    def checkAlive(self):
        return True if self.lives > 0 else False