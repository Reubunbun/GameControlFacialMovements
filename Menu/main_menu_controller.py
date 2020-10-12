from Menu.base_menu_controller  import BaseMenuController
from Util.Face_Detector.detection_utils import detectDirectionX, detectDirectionY, eyeAspectRatio, mouthAspectRatio

class MainMenuController( BaseMenuController ):

    def __init__(self, model):
        BaseMenuController.__init__(self, model)

        self.startYTurnCounters = [0, 0]

        self.MIN_X_SNAP = self.model.GAME_CENTRE_X - (self.model.GAME_ICON_GAP / 2)
        self.MAX_X_SNAP = self.model.GAME_CENTRE_X + (self.model.GAME_ICON_GAP / 2)
        self.MIN_Y_SNAP = self.model.GAME_CENTRE_Y - (self.model.GAME_SUB_ICON_HEIGHT / 2)
        self.MAX_Y_SNAP = self.model.GAME_CENTRE_Y + (self.model.GAME_SUB_ICON_HEIGHT / 2)
        self.SETTINGS_Y_POS       = self.model.GAME_CENTRE_Y - self.model.GAME_SUB_ICON_HEIGHT
        self.TUTORIAL_Y_POS       = self.model.GAME_CENTRE_Y + self.model.GAME_SUB_ICON_HEIGHT
        self.ICON_MOVE_AMOUNT     = 0.5
        self.SELECTOR_MOVE_AMOUNT = 0.2
        self.Y_DIR_THRESHOLD      = 0.06

    def moveIconsLeft(self):
        while True:
            if self.model.iconPointer[0] != len( self.model.gameIconList ) - 1:
                #Move slowly at first, to allow the user to react
                self.model.moveGameIcons( amount=-self.ICON_MOVE_AMOUNT )
                #X position of currently hovered icon
                currentPos = self.model.gameIconList[ self.model.iconPointer[0] ][1].rect[0]
                #When the icon is half way there, speed up the process
                if currentPos <= self.MIN_X_SNAP:
                    while currentPos > self.model.GAME_CENTRE_X - self.model.GAME_ICON_GAP:
                        #Move a larger amount now
                        self.model.moveGameIcons( amount=3*-self.ICON_MOVE_AMOUNT )
                        currentPos = self.model.gameIconList[ self.model.iconPointer[0] ][1].rect[0]
                    self.model.iconPointer[0] += 1
                    self.model.post("CHANGE_LABELS")
                    self.startXTurnCounters = [0, 0]
                    return
            # Cant move any further left
            else:
                self.startXTurnCounters = [0, 0]
                return

    def moveIconsRight(self):
        #Opposite of moving left
        while True:
            if self.model.iconPointer[0] != 0:
                self.model.moveGameIcons( amount=self.ICON_MOVE_AMOUNT )
                currentPos = self.model.gameIconList[ self.model.iconPointer[0] ][1].rect[0]
                if currentPos >= self.MAX_X_SNAP:
                    while currentPos < self.model.GAME_CENTRE_X + self.model.GAME_ICON_GAP:
                        self.model.moveGameIcons( amount=3*self.ICON_MOVE_AMOUNT )
                        currentPos = self.model.gameIconList[ self.model.iconPointer[0] ][1].rect[0]
                    self.model.iconPointer[0] -= 1
                    self.model.post("CHANGE_LABELS")
                    self.startXTurnCounters = [0, 0]
                    return
            else:
                self.startXTurnCounters = [0, 0]
                return

    def moveSelectorUp(self):
        while True:
            if self.model.iconPointer[1] != 0:
                #Move slowly to begin, allowing the user to react
                self.model.moveSelector( xAmount=0, yAmount=-self.SELECTOR_MOVE_AMOUNT )
                #If the selector is currently in the middle, move to the top
                if (self.model.selector.canvasRect[1] <= self.MIN_Y_SNAP) and self.model.iconPointer[1] == 1:
                    self.model.iconPointer[1] = 0
                    while not ( self.SETTINGS_Y_POS - 2 < self.model.selector.canvasRect[1] < self.SETTINGS_Y_POS + 2 ):
                        self.model.moveSelector( xAmount=0, yAmount=3*-self.SELECTOR_MOVE_AMOUNT )
                    self.model.selector.canvasRect[1] = self.SETTINGS_Y_POS
                    self.model.moveSelector( 0, 0 )
                    self.startYTurnCounters = [0, 0]
                    return
                #If the selector is currently at the bottom, move to the middle
                elif (self.model.selector.canvasRect[1] <= self.MAX_Y_SNAP) and self.model.iconPointer[1] == 2:
                    self.model.iconPointer[1] = 1
                    while not (self.model.GAME_CENTRE_Y - 2 < self.model.selector.canvasRect[1] < self.model.GAME_CENTRE_Y + 2):
                        self.model.moveSelector(xAmount=0, yAmount=3*-self.SELECTOR_MOVE_AMOUNT)
                    #Adjust selector position if it didnt land perfectly
                    self.model.selector.canvasRect[1] = self.model.GAME_CENTRE_Y
                    self.model.moveSelector( 0, 0 )
                    self.startYTurnCounters = [0, 0]
                    return
            #Cant move any further up
            else:
                self.startYTurnCounters = [0, 0]
                return

    def moveSelectorDown(self):
        #Opposite of moving up
        while True:
            if self.model.iconPointer[1] != len( self.model.gameIconList[0] ) - 1:
                self.model.moveSelector( xAmount=0, yAmount=self.SELECTOR_MOVE_AMOUNT )
                if (self.model.selector.canvasRect[1] >= self.MAX_Y_SNAP) and self.model.iconPointer[1] == 1:
                    self.model.iconPointer[1] = 2
                    while not ( self.TUTORIAL_Y_POS - 2 < self.model.selector.canvasRect[1] < self.TUTORIAL_Y_POS + 2 ):
                        self.model.moveSelector( xAmount=0, yAmount=3*self.SELECTOR_MOVE_AMOUNT )
                    self.model.selector.canvasRect[1] = self.TUTORIAL_Y_POS
                    self.model.moveSelector(0, 0)
                    self.startYTurnCounters = [0, 0]
                    return

                elif (self.model.selector.canvasRect[1] >= self.MIN_Y_SNAP) and self.model.iconPointer[1] == 0:
                    self.model.iconPointer[1] = 1
                    while not ( self.model.GAME_CENTRE_Y - 2 < self.model.selector.canvasRect[1] < self.model.GAME_CENTRE_Y + 2 ):
                        self.model.moveSelector( xAmount=0, yAmount=3*self.SELECTOR_MOVE_AMOUNT )
                    self.model.selector.canvasRect[1] = self.model.GAME_CENTRE_Y
                    self.model.moveSelector(0, 0)
                    self.startYTurnCounters = [0, 0]
                    return

            else:
                self.startYTurnCounters = [0, 0]
                return


    def controller(self):
        self.toggleInstruction()

        detected, landmarks = self.getLandmarks()
        if detected:
            self.toggleStatus("ON")

            xDirVal = -detectDirectionX( landmarks )
            yDirVal =  detectDirectionY( landmarks )
            lEar    =  eyeAspectRatio( landmarks, eye="left_eye"  )
            rEar    =  eyeAspectRatio( landmarks, eye="right_eye" )
            mar     =  mouthAspectRatio( landmarks )

            # MOVE ICONS LEFT/RIGHT
            if (xDirVal < -self.X_DIR_THRESHOLD) and not self.squinting and not self.mouthOpen:
                self.startXTurnCounters[0] = min(self.START_TURN_THRESHOLD, self.startXTurnCounters[0] + 1)
                if self.startXTurnCounters[0] == self.START_TURN_THRESHOLD:
                    self.moveIconsLeft()
            elif (xDirVal > self.X_DIR_THRESHOLD) and not self.squinting and not self.mouthOpen:
                self.startXTurnCounters[1] = min(self.START_TURN_THRESHOLD, self.startXTurnCounters[1] + 1)
                if self.startXTurnCounters[1] == self.START_TURN_THRESHOLD:
                    self.moveIconsRight()
            else:
                self.startXTurnCounters = [0, 0]

            # MOVE SELECTOR UP/DOWN
            if (yDirVal < -self.Y_DIR_THRESHOLD) \
                    and not (self.squintCounter > (self.SELECT_UNDO_THRESHOLD / 2)):
                self.startYTurnCounters[0] = min(self.START_TURN_THRESHOLD, self.startYTurnCounters[0] + 1)
                if self.startYTurnCounters[0] == self.START_TURN_THRESHOLD:
                    self.moveSelectorUp()
            elif (yDirVal > self.Y_DIR_THRESHOLD) \
                    and not (self.squintCounter > (self.SELECT_UNDO_THRESHOLD / 2)):
                self.startYTurnCounters[1] = min(self.START_TURN_THRESHOLD, self.startYTurnCounters[1] + 1)
                if self.startYTurnCounters[1] == self.START_TURN_THRESHOLD:
                    self.moveSelectorDown()
            else:
                self.startYTurnCounters = [0, 0]

            # SELECT AN ICON
            if (lEar <= self.SQUINT_THRESHOLD and rEar <= self.SQUINT_THRESHOLD) \
                    and (-self.X_DIR_THRESHOLD < xDirVal < self.X_DIR_THRESHOLD) \
                    and (-self.Y_DIR_THRESHOLD < yDirVal < self.Y_DIR_THRESHOLD):

                self.holdSelect()
                if self.squintCounter == self.SELECT_UNDO_THRESHOLD:
                    self.squinting = False
                    self.squintCounter = 0
                    self.instructionCounter = 0
                    #Change to settings
                    if self.model.iconPointer[1] == 2:
                        #Change tutorial text
                        self.model.post("CHANGE_TUTORIAL")
                        #Make analytics record
                        self.model.post("RECORD")
                        self.model.onMenu     = False
                        self.model.onTutorial = True
                        self.model.transitionUI( direction="UP" )
                        self.model.post("CHANGE_INSTRUCTION")
                        self.model.changeController()
                    elif self.model.iconPointer[1] == 1:
                        self.model.post("RECORD")
                        penColour = [ 255, 0, 0 ]
                        self.model.selector.rectList[0][1] = penColour
                        self.model.post("UPDATE_COLOUR")
                        self.model.startGame()
                    elif self.model.iconPointer[1] == 0:
                        self.model.placeSettings( setup=False )
                        self.model.post("CHANGE_SETTING_FOCUS")
                        self.model.post("RECORD")
                        self.model.onMenu     = False
                        self.model.onSettings = True
                        self.model.transitionUI( direction="DOWN" )
                        self.model.post("CHANGE_INSTRUCTION")
                        self.model.changeController()
            elif not self.mouthOpen:
                self.releaseSelect()

            if mar >= self.MAR_THRESHOLD and (-self.X_DIR_THRESHOLD < xDirVal < self.X_DIR_THRESHOLD) \
                    and not self.squinting:
                self.holdUndo()
                if self.mouthCounter == self.SELECT_UNDO_THRESHOLD:
                    self.mouthOpen    = False
                    self.mouthCounter = 0
                    self.model.exit()
            elif not self.squinting:
                self.releaseUndo()

        else:

            self.toggleStatus("OFF")