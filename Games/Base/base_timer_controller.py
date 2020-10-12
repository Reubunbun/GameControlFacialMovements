import pygame
import time
import xml.etree.ElementTree as ET

class BaseTimerController:

    def __init__(self, model):
        self.model   = model
        self.stopped = False
        self.startT  = 0
        self.endT    = 0
        self.model.addListener( self )

    def run(self):
        self.startT = time.time()
        while not self.stopped:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.model.post("STOP")
                    return
            self.passTime()
            self.model.update()
        return

    def passTime(self):
        pass

    def events(self, event):
        if event == "STOP":
            self.stopped = True
            self.endT    = time.time()
            self.writeScore()

    def writeScore(self):
        tree = ET.parse("Games/Data/games.xml")
        for game in tree.getroot().iter("game"):
            if game.find("name").text == self.model.name:
                highscore = int( game.find("highscore").text )
                if self.model.score > highscore:
                    game.find("highscore").text = str( self.model.score )
                    tree.write("Games/Data/games.xml")

        totalT = self.endT - self.startT
        frameRate = self.model.numFrames / totalT
        with open("performance.txt", 'a') as f:
            f.write(f"{self.model.name} framerate: {frameRate:.2f}\n")