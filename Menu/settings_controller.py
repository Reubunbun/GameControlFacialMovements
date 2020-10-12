from Menu.base_menu_controller  import BaseMenuController
from Util.Face_Detector.detection_utils import detectDirectionX, eyeAspectRatio, mouthAspectRatio

class SettingsController( BaseMenuController ):

    def __init__(self, model):
        BaseMenuController.__init__( self, model )

        self.mouthOpen = False

        self.MIN_X_SNAP = (self.model.firstSettingsX + self.model.middleSettingsX) / 2
        self.MAX_X_SNAP = (self.model.middleSettingsX + self.model.lastSettingsX) / 2
        self.SELECTOR_MOVE_AMOUNT = 0.5

    def moveSelectorLeft(self):
        if self.model.settingsPointer[0] == 2:
            self.model.settingsPointer[0] = 1
            dest = self.model.middleSettingsX - (self.model.selector.penWidth / 2)
        elif self.model.settingsPointer[0] == 1:
            self.model.settingsPointer[0] = 0
            dest = self.model.firstSettingsX
        else:
            self.startXTurnCounters = [0, 0]
            return

        while not ( dest - 2 < self.model.selector.canvasRect[0] < dest + 2 ):
            self.model.moveSelector( xAmount=-self.SELECTOR_MOVE_AMOUNT, yAmount=0 )
        self.model.selector.canvasRect[0] = dest
        self.model.moveSelector( 0, 0 )
        self.startXTurnCounters = [0, 0]

    def moveSelectorRight(self):
        if self.model.settingsPointer[0] == 0:
            self.model.settingsPointer[0] = 1
            dest = self.model.middleSettingsX - (self.model.selector.penWidth / 2)
        elif self.model.settingsPointer[0] == 1 and self.model.settingsPointer[1] <= 1:
            self.model.settingsPointer[0] = 2
            dest = self.model.lastSettingsX - (self.model.selector.penWidth / 2)
        else:
            self.startXTurnCounters = [0, 0]
            return

        while not ( dest - 2 < self.model.selector.canvasRect[0] < dest + 2 ):
            self.model.moveSelector( xAmount=self.SELECTOR_MOVE_AMOUNT, yAmount=0 )
        self.model.selector.canvasRect[0] = dest
        self.model.moveSelector( 0, 0 )
        self.startXTurnCounters = [0, 0]

    def controller(self):
        self.toggleInstruction()

        detected, landmarks = self.getLandmarks()
        if detected:
            self.toggleStatus("ON")

            xDirVal = -detectDirectionX( landmarks )
            lEar    =  eyeAspectRatio( landmarks, eye="left_eye"  )
            rEar    =  eyeAspectRatio( landmarks, eye="right_eye" )
            mar     =  mouthAspectRatio( landmarks )

            #MOVE SELECTOR RIGHT
            if (xDirVal < -self.X_DIR_THRESHOLD) and not self.squinting and not self.mouthOpen:
                self.startXTurnCounters[0] = min(self.START_TURN_THRESHOLD, self.startXTurnCounters[0] + 1)
                if self.startXTurnCounters[0] == self.START_TURN_THRESHOLD:
                    self.moveSelectorRight()
            #MOVE SELECTOR LEFT
            elif (xDirVal > self.X_DIR_THRESHOLD) and not self.squinting and not self.mouthOpen:
                self.startXTurnCounters[1] = min(self.START_TURN_THRESHOLD, self.startXTurnCounters[1] + 1)
                if self.startXTurnCounters[1] == self.START_TURN_THRESHOLD:
                    self.moveSelectorLeft()
            else:
                self.startXTurnCounters = [0, 0]

            #SELECT
            if (lEar <= self.SQUINT_THRESHOLD and rEar <= self.SQUINT_THRESHOLD) \
                    and (-self.X_DIR_THRESHOLD < xDirVal < self.X_DIR_THRESHOLD) and not self.mouthOpen:

                self.holdSelect()
                if self.squintCounter == self.SELECT_UNDO_THRESHOLD:
                    self.squinting = False
                    self.squintCounter = 0
                    self.instructionCounter = 0
                    self.model.selectSetting( undo=False )
                    if self.model.settingsPointer[1] == 3:
                        self.model.settingsPointer = [0, 0]
                        self.model.post("RECORD")
                        self.model.onSettings = False
                        self.model.onMenu     = True
                        self.model.transitionUI( direction="UP" )
                        self.model.post("CHANGE_INSTRUCTION")
                        self.model.changeController()
                    else:
                        self.model.transitionSettingsSelector( direction="DOWN" )
            elif not self.mouthOpen:
                self.releaseSelect()

            #UNDO
            if mar >= self.MAR_THRESHOLD and (-self.X_DIR_THRESHOLD < xDirVal < self.X_DIR_THRESHOLD) \
                    and not self.squinting:
                self.holdUndo()
                if self.mouthCounter == self.SELECT_UNDO_THRESHOLD:
                    self.mouthOpen    = False
                    self.mouthCounter = 0
                    if self.model.settingsPointer[1] == 0:
                        self.model.settingsPointer = [0, 0]
                        self.model.post("RECORD")
                        self.model.onSettings = False
                        self.model.onMenu     = True
                        self.model.transitionUI( direction="UP" )
                        self.model.post("CHANGE_INSTRUCTION")
                        self.model.changeController()
                    else:
                        self.model.selectSetting( undo=True )
                        self.model.transitionSettingsSelector( direction="UP" )
            elif not self.squinting:
                self.releaseUndo()

        else:

            self.toggleStatus("OFF")