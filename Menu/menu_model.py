from dataclasses import dataclass
import xml.etree.ElementTree as ET

from Menu.main_menu_controller import MainMenuController
from Menu.settings_controller  import SettingsController
from Menu.tutorial_controller  import TutorialController

from Games.Falling_Blocks.fb_model            import FallingBlocksModel
from Games.Falling_Blocks.fb_timer_controller import FallingBlocksTimerController
from Games.Falling_Blocks.fb_face_controller  import FallingBlocksFaceController
from Games.Base.base_view                     import BaseView

from Games.Drifting_Blocks.db_face_controller  import DriftingBlocksFaceController
from Games.Drifting_Blocks.db_timer_controller import DriftingBlocksTimerController
from Games.Drifting_Blocks.db_view             import DriftingBlocksView
from Games.Drifting_Blocks.db_model            import DriftingBlocksModel

from Util.Calibrate.calibrate_controller import CalibrateController
from Util.Calibrate.calibrate_model      import CalibrateModel
from Util.Calibrate.calibrate_view       import CalibrateView

#Data classes to act as structures, to store visual information
@dataclass
class Label:
    fontType : str
    fontSize : int
    text     : str
    rect     : list

@dataclass
class ImageIcon:
    image : str
    rect  : list

@dataclass
class PixmapIcon:
    canvasRect : list
    penWidth   : int
    rectList   : list

class MenuModel:

    def __init__(self):
        self.WIDTH  = 960
        self.HEIGHT = 540
        self.GAME_ICON_GAP  = 250
        self.GAME_ICON_SIZE = 180
        self.GAME_SUB_ICON_HEIGHT = self.GAME_ICON_SIZE / 3
        self.GAME_CENTRE_X        = (self.WIDTH  / 2) - (self.GAME_ICON_SIZE / 2)
        self.GAME_CENTRE_Y        = (self.HEIGHT / 2) - (self.GAME_ICON_SIZE / 2)
        self.SELECTOR_LINE_WIDTH  = 8
        self.FONT_TYPE            = "MS Gothic"
        self.TEXT_WIDTH, self.TEXT_HEIGHT = 285, 70
        self.GAME_DATA_PATH  = "Games/Data/games.xml"
        self.SETTINGS_VALUES = {
            "fps"        : { "15"      : 0, "30"   : 1, "60"      : 2 },
            "camQuality" : { "standard": 0, "high" : 1, "veryHigh": 2 },
            "showCam"    : { "True"    : 0, "False": 1 },
            "calibrate"  : { "True"    : 0, "False": 1 }
        }

        self.stopped     = False
        self.camQuality  = "veryHigh"
        self.listeners   = []

        self.gamesList       = []
        self.gameIconList    = []
        self.labelDict       = {}
        self.settingsIcons   = []
        self.settingsCrosses = []
        self.settingsBuffer  = []

        #Position of selector in the main menu
        self.iconPointer     = [0, 1]
        #Position of selector in the settings
        self.settingsPointer = [0, 0]
        self.onMenu          = True
        self.onSettings      = False
        self.onTutorial      = False

        self.setupMainMenu()
        self.setupSettings()
        self.setupTutorial()

    def addListener(self, listener):
        self.listeners.insert( 0, listener )

    def post(self, event):
        if not self.stopped:
            if event == "STOP":
                self.stopped = True
            for listener in self.listeners:
                listener.events( event )

    def run(self):
        while not self.stopped:
            self.post("NEXT_FRAME")
        return self

    def setupMainMenu(self):
        SETTINGS_IMAGE = "Menu/Images/settings.png"
        TUTORIAL_IMAGE = "Menu/Images/tutorial.png"
        FONT_SIZE      = 28

        tree = ET.parse("Games/Data/games.xml")
        #Position the games icons in the main menu
        for i, game in enumerate( tree.getroot().iter("game") ):
            name      = game.find("name").text
            highscore = "Highscore: " + game.find("highscore").text
            self.gamesList.append( (name, highscore) )

            image = game.find("icon").text
            path = "Menu/Images/" + image

            settingsRect = [ self.GAME_CENTRE_X + (self.GAME_ICON_GAP*i), self.GAME_CENTRE_Y - self.GAME_SUB_ICON_HEIGHT,
                             self.GAME_ICON_SIZE, self.GAME_SUB_ICON_HEIGHT ]
            settingsIcon = ImageIcon( image=SETTINGS_IMAGE, rect=settingsRect )

            gameRect     = [ self.GAME_CENTRE_X + (self.GAME_ICON_GAP*i), self.GAME_CENTRE_Y,
                             self.GAME_ICON_SIZE, self.GAME_ICON_SIZE ]
            gameIcon     = ImageIcon( image=path, rect=gameRect )

            tutorialRect = [ self.GAME_CENTRE_X + (self.GAME_ICON_GAP*i), self.GAME_CENTRE_Y + self.GAME_ICON_SIZE,
                             self.GAME_ICON_SIZE, self.GAME_SUB_ICON_HEIGHT ]
            tutorialIcon = ImageIcon( image=TUTORIAL_IMAGE, rect=tutorialRect )

            self.gameIconList.append( [settingsIcon, gameIcon, tutorialIcon] )

        #Position the selector to start in the middle
        selectorCanvasRect = [ self.GAME_CENTRE_X, self.GAME_CENTRE_Y, self.GAME_ICON_SIZE, self.GAME_ICON_SIZE ]
        selectorPixmapRect = [ 0, 0, self.GAME_ICON_SIZE, self.GAME_ICON_SIZE ]
        self.selector = PixmapIcon( canvasRect=selectorCanvasRect,
                                    rectList=[ [ selectorPixmapRect, [255, 0, 0], 'solid', [] ] ],
                                    penWidth=self.SELECTOR_LINE_WIDTH )

        titleLabelRect = [ self.GAME_CENTRE_X, self.GAME_CENTRE_Y - self.GAME_SUB_ICON_HEIGHT - self.TEXT_HEIGHT,
                           self.TEXT_WIDTH, self.TEXT_HEIGHT ]
        titleLabel = Label( fontType=self.FONT_TYPE, fontSize=FONT_SIZE,
                            text=self.gamesList[0][0], rect=titleLabelRect )
        self.labelDict["title"] = titleLabel

        highscoreLabelRect = [ 0, self.HEIGHT - self.TEXT_HEIGHT, self.TEXT_WIDTH, self.TEXT_HEIGHT ]
        highscoreLabel = Label( fontType=self.FONT_TYPE, fontSize=FONT_SIZE,
                                text=self.gamesList[0][1], rect=highscoreLabelRect )
        self.labelDict["highscore"] = highscoreLabel

        #Use a percentage of the users screen for the instructions box size
        instructionWidth  = 0.33*self.WIDTH
        instructionHeight = 0.2*self.HEIGHT
        #Rectangle for the canvas
        instructionsCanvasRect = [ self.WIDTH - instructionWidth, self.HEIGHT - instructionHeight,
                                   instructionWidth, instructionHeight ]
        #Pixmap rectangle for the box that instructions will appear over
        instructionsPixmapRect = [ 0, 0, instructionWidth, instructionHeight ]
        #Pixmap rectangle for the background to go behind the status text
        statusPixmapRect = [ 0, 0, instructionWidth / 2, instructionHeight / 5 ]
        rectList = [
            [ instructionsPixmapRect, [0, 255, 0], 'dotted', [255, 255, 255] ],
            [ statusPixmapRect, [0, 255, 0], 'solid', [0, 255, 0] ]
        ]
        self.instructions = PixmapIcon( canvasRect=instructionsCanvasRect,
                                        rectList=rectList,
                                        penWidth=8 )
        TEXT_PADDING = 3
        #Label for the status text
        statusLabelRect = [ instructionsCanvasRect[0] + TEXT_PADDING, instructionsCanvasRect[1] + TEXT_PADDING,
                            statusPixmapRect[2], statusPixmapRect[3] ]
        statusLabelText = "Status: Detected"
        statusLabel = Label( fontType=self.FONT_TYPE, fontSize=10, text=statusLabelText, rect=statusLabelRect )
        self.labelDict["status"] = statusLabel

        menuInstructionsText = [
            "Turn your head left/right<br>to change games",
            "Turn your head up/down to<br>switch between<br>settings/instructions",
            "Squint your eyes to select<br>an icon",
            "Hold your mouth open to<br>quit"
        ]
        self.numMenuInstructions = len(menuInstructionsText)
        settingsInstructionsText = [
            "Turn your head left/right<br>to switch between<br>options",
            "Squint your eyes to select<br>an option",
            "Hold your mouth open to<br>undo a selection"
        ]
        self.numSettingsInstructions = len(settingsInstructionsText)
        tutorialInstructionsText = "Squint your eyes to go<br>back to the main<br>menu"
        self.numTutorialInstructions = 1
        instructionsTextRect = [ instructionsCanvasRect[0] + self.instructions.penWidth,
                                 instructionsCanvasRect[1] + self.instructions.penWidth,
                                 instructionsCanvasRect[2], instructionsCanvasRect[3] ]
        for i in range( len( menuInstructionsText ) ):
            self.labelDict[ "instructionsMenu" + str(i) ] = Label( fontType=self.FONT_TYPE, fontSize=16,
                                                                   text=menuInstructionsText[i],
                                                                   rect=instructionsTextRect )
        for i in range( len(settingsInstructionsText) ):
            self.labelDict[ "instructionsSettings" + str(i) ] = Label( fontType=self.FONT_TYPE, fontSize=16,
                                                                       text=settingsInstructionsText[i],
                                                                       rect=instructionsTextRect )
        self.labelDict["instructionTutorial"] = Label( fontType=self.FONT_TYPE, fontSize=16,
                                                       text=tutorialInstructionsText,
                                                       rect=instructionsTextRect )

    def setupSettings(self):
        settings = [
            "              FPS",
            "Detection Quality",
            "     Show Camera?",
            "       Calibrate?",
        ]
        settingsChoices = [
            [ " 15", " 30", " 60" ],
            [ "Standard", "High", "Very<br>High" ],
            [ "True", "False" ],
            [ "True", "False" ]
        ]
        settingsDescriptions = [
            '''Changes how many frames<br>per second the game runs<br>at. The game will appear<br>smoother with higher
            <br>fps, but requires a<br>better computer. Change<br>to lower fps if the game<br>does not run well.''',

            '''Changes the quality of<br>face detection. Setting<br>to higher may more<br>accurately detect<br>
            gestures, but requires a<br>very good computer. It<br>is recommended to use<br>standard.''',

            '''Choose to display your<br>webcam stream in the<br>bottom corner while you<br>play. This may help you<br>
            align in front of your<br>camera to improve<br>detection.''',

            '''Choose whether or not to<br>calibrate before the<br>game starts, this may<br>improve detection rates.<br>
            This is recommended for<br>games that need you to<br>look up/down<br>(Drifting Blocks)'''
        ]
        MAX_CHOICES    = 3
        numSettings    = len( settings )
        FONT_SIZE      = 18
        DESC_FONT_SIZE = 24
        TEXT_WIDTH, TEXT_HEIGHT = 220, 90
        SETTING_OFFSET = 1 / ( numSettings + 1 )
        CHOICE_OFFSET  = 1 / ( MAX_CHOICES - 0.5 )
        SETTINGS_CANV_HEIGHT = 90
        SETTINGS_CANV_WIDTH  = 3*SETTINGS_CANV_HEIGHT
        SETTINGS_LINE_WIDTH  = 3

        #Create descriptions labels
        for i in range( numSettings ):
            labelRect = [ ( 0.1*self.WIDTH ) + ( 2*TEXT_WIDTH ), TEXT_HEIGHT - self.HEIGHT,
                          2*TEXT_WIDTH, 3*TEXT_HEIGHT ]
            label = Label( fontType=self.FONT_TYPE, fontSize=DESC_FONT_SIZE, text=settingsDescriptions[i],
                           rect=labelRect )
            self.labelDict[ "description" + str(i) ] = label

        for i in range( numSettings ):
            #Setting title label
            labelRect = [ 5, ( self.HEIGHT*SETTING_OFFSET*i ) + TEXT_HEIGHT - self.HEIGHT,
                          TEXT_WIDTH, TEXT_HEIGHT]
            label = Label( fontType=self.FONT_TYPE, fontSize=FONT_SIZE, text=settings[i], rect=labelRect )
            self.labelDict[ "setting" + str(i) ] = label

            for j in range( MAX_CHOICES ):
                #Last two settings only have two choices
                if i > 1 and j > 1:
                    continue

                #Adjust "standard" text
                adjust = -25 if ( i == 1 and j == 0 ) else 0
                labelRect = [ ( 1.05*TEXT_WIDTH ) + ( CHOICE_OFFSET * TEXT_WIDTH * j ) + adjust,
                              ( self.HEIGHT * SETTING_OFFSET * i ) + ( TEXT_HEIGHT / 2 ) - self.HEIGHT,
                              TEXT_WIDTH, TEXT_HEIGHT ]
                #Settings choice label
                label = Label( fontType=self.FONT_TYPE, fontSize=FONT_SIZE, text=settingsChoices[i][j], rect=labelRect )
                self.labelDict[ "setting" + str(i) + "Choice" + str(j) ] = label

            numBoxes = 3 if i < 2 else 2
            #Generate a pixmap that will contain a box for each choice
            settingsIconPixmapRects = generateSettingsRects( numBoxes=numBoxes, canvHeight=TEXT_HEIGHT )
            settingsIconCanvRect = [ TEXT_WIDTH,
                                     (self.HEIGHT * SETTING_OFFSET * i) + TEXT_HEIGHT - self.HEIGHT,
                                     SETTINGS_CANV_WIDTH, SETTINGS_CANV_HEIGHT ]
            rectList = []
            #Each choice box has a solid black border
            for rect in settingsIconPixmapRects:
                rectList.append( [ rect, [0, 0, 0], 'solid', [] ] )
            self.settingsIcons.append(
                PixmapIcon( canvasRect=settingsIconCanvRect, rectList=rectList, penWidth=SETTINGS_LINE_WIDTH )
            )

        #Useful variables containing positions of settings boxes
        self.firstSettingsX  = self.settingsIcons[0].canvasRect[0]
        self.middleSettingsX = self.settingsIcons[0].canvasRect[0] + self.settingsIcons[0].rectList[1][0][0]
        self.lastSettingsX   = self.settingsIcons[0].canvasRect[0] + self.settingsIcons[0].rectList[2][0][0]
        self.firstSettingsY  = self.settingsIcons[0].canvasRect[1] + self.settingsIcons[0].rectList[0][0][1] + self.HEIGHT
        self.secondSettingsY = self.settingsIcons[1].canvasRect[1] + self.settingsIcons[1].rectList[0][0][1] + self.HEIGHT

        self.placeSettings( setup=True )

    def setupTutorial(self):
        TUTORIAL_WIDTH  = 0.8*self.WIDTH
        TUTORIAL_HEIGHT = 0.5*self.HEIGHT

        tutorialDict = {
            "Falling Blocks" : '''In Falling Blocks, you control a blue square by turning your<br>head left to move left, 
            and turning your head right to move<br>right. Red blocks will appear from the top of the screen and<br>move
            down. The objective is to avoid being hit by these red<br>blocks for as long as possible. If you get hit three times,
            <br>the game ends. Hold your mouth open to quit the game and go<br>back to the menu.''',

            "Drifting Blocks" : '''In Drifting Blocks, you control a blue square by turning your<br>head left to move left, 
            turning your head right to move right,<br>turning your head up to move up, and turning your head down to<br>
            move down. Red blocks will appear from any side of the screen<br>and move in a random direction. The objective is 
            to avoid being<br>hit by these red blocks for as long as possible. If you get hit<br>three times, the game ends. 
            Hold your mouth open to quit the<br>game and go back to the menu.'''
        }
        backButtonRect = [ self.GAME_CENTRE_X, (0.8*self.HEIGHT) + self.HEIGHT,
                           self.GAME_ICON_SIZE, self.GAME_SUB_ICON_HEIGHT ]
        self.backButton = ImageIcon( image="Menu/Images/go_back.png", rect=backButtonRect )

        for game, tutorial in tutorialDict.items():
            tutorialRect = [ 0.15*TUTORIAL_WIDTH, (0.25*TUTORIAL_HEIGHT) + self.HEIGHT, TUTORIAL_WIDTH, TUTORIAL_HEIGHT ]
            label = Label( fontType=self.FONT_TYPE, fontSize=18, text=tutorial, rect=tutorialRect )
            self.labelDict[ game + "tutorial" ] = label

    def moveGameIcons(self, amount):
        for gameIcons in self.gameIconList:
            for icon in gameIcons:
                icon.rect[0] += amount
        self.post("MOVE_GAMES")

    def moveSelector(self, xAmount, yAmount):
        self.selector.canvasRect[0] += xAmount
        self.selector.canvasRect[1] += yAmount
        self.post("MOVE_SELECTOR")

    def transitionSettingsSelector(self, direction):
        #Moves selector up/down to a different setting

        #Number of frames the transition will take
        STEPS = 40
        if direction == "DOWN":
            #Always move to the first option of the next setting when selecting
            settingX = self.firstSettingsX
            self.settingsPointer = [ 0, self.settingsPointer[1] + 1 ]
        else:
            #Move to whatever option the user had previously selected when undoing
            if self.settingsBuffer[ self.settingsPointer[1] - 1 ] == 0:
                settingX = self.firstSettingsX
                self.settingsPointer = [ 0, self.settingsPointer[1] - 1 ]
            elif self.settingsBuffer[ self.settingsPointer[1] - 1 ] == 1:
                settingX = self.middleSettingsX
                self.settingsPointer = [ 1, self.settingsPointer[1] - 1 ]
            else:
                settingX = self.lastSettingsX
                self.settingsPointer = [ 2, self.settingsPointer[1] - 1 ]

        yDistance = (self.secondSettingsY - self.firstSettingsY) / STEPS
        xDistance = ( self.selector.canvasRect[0] - settingX ) / STEPS

        for _ in range( STEPS ):
            #Each frame, change the selector colour back to red and move it
            penColour = self.selector.rectList[0][1]
            penColour = [
                min( 255, int( penColour[0] + (255 / STEPS) ) ),
                max( 0,   int( penColour[1] - (255 / STEPS) ) ),
                max( 0,   int( penColour[2] - (255 / STEPS) ) )
            ]
            self.selector.rectList[0][1] = penColour
            self.post("UPDATE_COLOUR")
            if direction == "DOWN":
                self.moveSelector( xAmount=-xDistance, yAmount=yDistance )
            elif direction == "UP":
                self.moveSelector( xAmount=-xDistance, yAmount=-yDistance )

        #Adjust the selector position in case it didnt land perfectly
        self.selector.canvasRect[0] = settingX if settingX == self.firstSettingsX else settingX - (self.selector.penWidth / 2)
        self.selector.canvasRect[1] = \
            self.settingsIcons[ self.settingsPointer[1] ].canvasRect[1] + \
            self.settingsIcons[ self.settingsPointer[1] ].rectList[0][0][1] - (self.selector.penWidth / 2)
        self.moveSelector( 0, 0 )

        #Change the opacity of other settings
        self.post("CHANGE_SETTING_FOCUS")

    def transitionUI(self, direction):
        #Moves all elements of the UI to transition to a different part

        STEPS = 50
        amount = -self.HEIGHT if direction == "UP" else self.HEIGHT
        #Amount to move all elements of the UI, apart from the selector
        moveAmount = int( round( amount / STEPS ) )

        #Different possible amounts to move the selector in the x and y direction
        selectorXToSettings = ( self.GAME_CENTRE_X  - self.firstSettingsX ) / STEPS
        selectorXToMenu     = ( self.GAME_CENTRE_X  - self.selector.canvasRect[0] ) / STEPS
        selectorYToSettings = ( self.GAME_CENTRE_Y  - self.GAME_SUB_ICON_HEIGHT - self.firstSettingsY - self.selector.penWidth) / STEPS
        selectorYToMenu     = ( self.GAME_CENTRE_Y  - self.GAME_SUB_ICON_HEIGHT - self.selector.canvasRect[1] ) / STEPS
        selectorYToTutorial = ( self.GAME_CENTRE_Y  + self.GAME_SUB_ICON_HEIGHT - self.backButton.rect[1] ) / STEPS
        selectorWidthAmount = ( self.GAME_ICON_SIZE - self.GAME_SUB_ICON_HEIGHT ) / STEPS

        if self.onSettings:
            #Move the selector to the intial settings location
            selectorXAmount     = -selectorXToSettings
            selectorYAmount     = -selectorYToSettings
            selectorWidthAmount = -selectorWidthAmount
            #X position of pixmap rect
            self.selector.rectList[0][0][0] += self.selector.penWidth / 2
            #Y position of pixmap rect
            self.selector.rectList[0][0][1] += self.selector.penWidth / 2
        elif self.onTutorial:
            #Move the selector to the intial tutorial location
            selectorXAmount     = 0
            selectorYAmount     = -selectorYToTutorial
            selectorWidthAmount = 0
        elif self.onMenu:
            # Move the selector to the intial main menu location
            selectorXAmount     = selectorXToMenu     if direction == "UP" else 0
            selectorYAmount     = selectorYToMenu     if direction == "UP" else selectorYToTutorial
            selectorWidthAmount = selectorWidthAmount if direction == "UP" else 0
            #Transitioning to menu from settings
            if direction == "UP":
                #X position of pixmap rect
                self.selector.rectList[0][0][0] -= self.selector.penWidth / 2
                #Y position of pixmap rect
                self.selector.rectList[0][0][1] -= self.selector.penWidth / 2

        for i in range( STEPS ):
            for gameIcons in self.gameIconList:
                for icon in gameIcons:
                    icon.rect[1] += moveAmount

            for key, label in self.labelDict.items():
                if not ( key.startswith("instruction") or key == "status" ):
                    label.rect[1] += moveAmount

            for pixmapIcon in self.settingsIcons:
                pixmapIcon.canvasRect[1] += moveAmount

            for imageIcon in self.settingsCrosses:
                imageIcon.rect[1] += moveAmount

            self.backButton.rect[1] += moveAmount

            #Change the selector colour back to red as it moves
            penColour = self.selector.rectList[0][1]
            penColour = [
                min( 255, int( penColour[0] + ( 255 / STEPS ) ) ),
                max(   0, int( penColour[1] - ( 255 / STEPS ) ) ),
                max(   0, int( penColour[2] - ( 255 / STEPS ) ) )
            ]
            self.selector.rectList[0][1] = penColour
            self.selector.canvasRect[0] += selectorXAmount
            self.selector.canvasRect[1] += selectorYAmount
            if (self.onMenu and direction == "UP") or self.onSettings:
                #Width of the selector pixmap rect
                self.selector.rectList[0][0][2] += selectorWidthAmount

            self.post("TRANSITION_UI")

        #Adjust selector position if it didnt land perfectly
        if self.onSettings:
            self.selector.canvasRect[0] = self.firstSettingsX
            self.selector.canvasRect[1] = self.firstSettingsY + (self.selector.penWidth / 2)
        elif self.onTutorial:
            self.selector.canvasRect[0] = self.GAME_CENTRE_X
            self.selector.canvasRect[1] = self.backButton.rect[1] - self.GAME_ICON_SIZE + self.GAME_SUB_ICON_HEIGHT
        elif self.onMenu:
            self.selector.canvasRect[0] = self.GAME_CENTRE_X
            self.selector.canvasRect[1] = (self.GAME_CENTRE_Y - self.GAME_SUB_ICON_HEIGHT) if direction == "UP" else \
                (self.GAME_CENTRE_Y + self.GAME_SUB_ICON_HEIGHT)

        self.post("TRANSITION_UI")

    def changeController(self):
        self.post("PAUSE")
        #Remove previous controller from listeners
        del self.listeners[0]
        if self.onMenu:
            controller = MainMenuController( self )
            controller.startThread()
        elif self.onSettings:
            controller = SettingsController( self )
            controller.startThread()
        elif self.onTutorial:
            controller = TutorialController( self )
            controller.startThread()

    def placeSettings(self, setup):
        #Moves the settings cross icon

        settingsVals = []
        tree = ET.parse( self.GAME_DATA_PATH )
        #Read the game data file, store the settings options as values 0, 1 or 2
        for i, game in enumerate( tree.getroot().iter("game") ):
            if game.find("name").text == self.gamesList[ self.iconPointer[0] ][0]:
                settingsVals.append( self.SETTINGS_VALUES["fps"][ game.find("fps").text ] )
                settingsVals.append( self.SETTINGS_VALUES["camQuality"][ game.find("camQuality").text ] )
                settingsVals.append( self.SETTINGS_VALUES["showCam"][ game.find("showCam").text ] )
                settingsVals.append( self.SETTINGS_VALUES["calibrate"][ game.find("calibrate").text ] )

        image = "Menu/Images/cross.png"

        #Add imageicons to list if this is the first time viewing
        if setup:
            for i, val in enumerate( settingsVals ):
                rectToPlaceOn = self.settingsIcons[i].rectList[ val ][0]
                crossRect = [ self.settingsIcons[i].canvasRect[0] + rectToPlaceOn[0],
                              self.settingsIcons[i].canvasRect[1] + rectToPlaceOn[1],
                              rectToPlaceOn[2], rectToPlaceOn[3] ]
                imageIcon = ImageIcon( image=image, rect=crossRect )
                self.settingsCrosses.append( imageIcon )
                #Use a buffer for undoing
                self.settingsBuffer.append( val )
        #Move the icons otherwise
        else:
            for i, val in enumerate( settingsVals ):
                rectToPlaceOn = self.settingsIcons[i].rectList[ settingsVals[i] ][0]
                self.settingsCrosses[i].rect[0] = self.settingsIcons[i].canvasRect[0] + rectToPlaceOn[0]
                self.settingsBuffer[i] = val
            self.post("CHANGE_CROSSES")

    def selectSetting(self, undo):

        #Move to the setting in the buffer if undoing, otherwise move to the next one
        if undo:
            pointer = self.settingsPointer[1] - 1
            selectSettingVal = self.settingsBuffer[ pointer ]
        else:
            pointer = self.settingsPointer[1]
            selectSettingVal = self.settingsPointer[0]

        rectToPlaceOn = self.settingsIcons[ pointer ]
        self.settingsCrosses[ pointer ].rect[0] = \
            rectToPlaceOn.canvasRect[0] + rectToPlaceOn.rectList[ selectSettingVal ][0][0]
        self.post("CHANGE_CROSSES")

        #Update the setting in the data file
        tree = ET.parse( self.GAME_DATA_PATH )
        for game in tree.getroot().iter("game"):
            if game.find("name").text == self.gamesList[ self.iconPointer[0] ][0]:

                if pointer == 0:
                    search = "fps"
                elif pointer == 1:
                    search = "camQuality"
                elif pointer == 2:
                    search = "showCam"
                else:
                    search = "calibrate"

                for setting, value in self.SETTINGS_VALUES[search].items():
                    if value == selectSettingVal:
                        game.find(search).text = setting

        tree.write( self.GAME_DATA_PATH )

    def startGame(self):
        #Starts a game

        self.stopped = True
        #Stop the current face controller
        self.post("PAUSE")
        tree = ET.parse(self.GAME_DATA_PATH)
        #Find the game the user is choosing in the data file, load its settings
        for game in tree.getroot().iter("game"):
            if game.find("name").text == self.gamesList[ self.iconPointer[0] ][0]:
                if game.find("calibrate").text == "True":
                    calibrateModel = CalibrateModel()
                    calibrateView  = CalibrateView( calibrateModel )
                    caliController = CalibrateController( calibrateModel )
                    caliController.startThread()
                    anchorPoints = calibrateModel.run()
                else:
                    anchorPoints = None

        if self.iconPointer[0] == 0:
            gameModel       = FallingBlocksModel()
            timerController = FallingBlocksTimerController( gameModel )
            faceController  = FallingBlocksFaceController( gameModel )
            gameView        = BaseView( gameModel )
            faceController.startThread()
            timerController.run()
        elif self.iconPointer[0] == 1:
            gameModel       = DriftingBlocksModel()
            timerController = DriftingBlocksTimerController( gameModel )
            faceController  = DriftingBlocksFaceController( model=gameModel, anchorPoints=anchorPoints )
            gameView        = DriftingBlocksView( gameModel )
            faceController.startThread()
            timerController.run()

        self.stopped = False
        #Change the highscore if the user has reached a new one
        for game in tree.getroot().iter("game"):
            if game.find("name").text == self.gamesList[ self.iconPointer[0] ][0]:
                currentHighscore = int( game.find("highscore").text )
                savedHighscore   = int( self.gamesList[ self.iconPointer[0] ][1].split(" ")[1] )
                if currentHighscore > savedHighscore:
                    print(self.gamesList[ self.iconPointer[0] ])
                    self.gamesList[ self.iconPointer[0] ] = \
                        ( self.gamesList[ self.iconPointer[0] ][0] , "Highscore: " + game.find("highscore").text )
        #Remove the game's controller from listeners list
        del self.listeners[0]
        #Start a new main menu controller
        controller = MainMenuController( self )
        controller.startThread()
        self.run()

    def exit(self):
        self.post("STOP")

def generateSettingsRects( numBoxes, canvHeight ):
    #Generates the pixmap for the settings choices boxes

    PADDING = 5
    rects  = []
    for i in range( numBoxes ):
        rect = [ ( i*canvHeight ) + PADDING, ( canvHeight/3 ) - PADDING + 1, canvHeight * (2/3), canvHeight * (2/3) - 3 ]
        rects.append( rect )

    return rects
