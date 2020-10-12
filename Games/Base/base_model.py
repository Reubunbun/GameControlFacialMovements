import xml.etree.ElementTree as ET
from Util.analytics import Analytics

class BaseModel:

    def __init__(self, name, width, height):
        self.analytics = Analytics()
        self.width     = width
        self.height    = height
        self.name      = name
        self.listeners = []
        self.time      = 0
        self.score     = 0
        self.frame     = None
        self.detected  = False
        self.quitGame  = False

        tree = ET.parse("Games/Data/games.xml")
        for game in tree.getroot().iter("game"):
            if game.find("name").text == self.name:
                self.fps        = int( game.find("fps").text )
                self.camQuality = game.find("camQuality").text
                self.showCam    = True if game.find("showCam").text == "True" else False

    def addListener(self, listener):
        self.listeners.append( listener )

    def post(self, event):
        if event == "STOP":
            self.analytics.makeRecord( type=self.name )
        for listener in self.listeners:
            listener.events( event )
