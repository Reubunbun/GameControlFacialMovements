from Util.Face_Detector.base_face_controller import BaseFaceController
from Util.analytics import Analytics

class BaseMenuController( BaseFaceController ):

    def __init__(self, model):
        BaseFaceController.__init__( self, model )
        self.analytics = Analytics()
        self.detected  = True
        self.squinting = False
        self.mouthOpen = False
        self.squintCounter      = 0
        self.mouthCounter       = 0
        self.instructionCounter = 0
        self.startXTurnCounters = [0, 0]

        self.X_DIR_THRESHOLD       = 0.2
        self.SQUINT_THRESHOLD      = 0.18
        self.MAR_THRESHOLD         = 1
        self.SELECT_UNDO_THRESHOLD = 25
        self.START_TURN_THRESHOLD  = 10
        self.INSTRUCTION_THRESHOLD = 150

    def events(self, event):
        if event == "NEXT_FRAME":
            self.controller()
        elif event == "RECORD":
            if self.model.onMenu:
                type = "main menu"
            elif self.model.onSettings:
                type = "settings"
            elif self.model.onTutorial:
                type = "tutorial"
            self.analytics.makeRecord( type=type )
        elif event == "PAUSE":
            self.stopped = True
            return self
        elif event == "STOP":
            self.stopped = True
            if self.model.onMenu:
                type = "main menu"
            elif self.model.onSettings:
                type = "settings"
            elif self.model.onTutorial:
                type = "tutorial"
            self.analytics.makeRecord( type=type, newline=True )

    def controller(self):
        pass

    def toggleStatus(self, status):
        #Change the status rectangle
        self.analytics.makeTimestamp( check=self.detected )
        if not self.detected and status == "ON":
            detectedColour = [0, 255, 0]
            # First rect border
            self.model.instructions.rectList[0][1] = detectedColour
            # Second rect border
            self.model.instructions.rectList[1][1] = detectedColour
            # Second rect background
            self.model.instructions.rectList[1][3] = detectedColour
            self.model.labelDict["status"].text = "Status: Detected"
            self.model.post("UPDATE_STATUS")
            self.detected = True
            return
        elif self.detected and status == "OFF":
            detectedColour = [255, 0, 0]
            # First rect border
            self.model.instructions.rectList[0][1] = detectedColour
            # Second rect border
            self.model.instructions.rectList[1][1] = detectedColour
            # Second rect background
            self.model.instructions.rectList[1][3] = detectedColour
            self.model.labelDict["status"].text = "Status: Not Detected"
            self.model.post("UPDATE_STATUS")
            self.detected = False
            return

    def toggleInstruction(self):
        #Change the instructions
        self.instructionCounter += 1
        if self.instructionCounter == self.INSTRUCTION_THRESHOLD:
            self.model.post("CHANGE_INSTRUCTION")
            self.instructionCounter = 0

    def holdSelect(self):
        #If the user was some way through undoing, release the undo first
        if self.mouthCounter > 0:
            self.releaseUndo()
        else:
            self.squinting = True
            self.squintCounter = min( self.SELECT_UNDO_THRESHOLD, self.squintCounter + 1 )
            penColour = self.model.selector.rectList[0][1]
            #Increase green value, reduce other values
            penColour = [
                max(   0, int( penColour[0] - ( 255 / self.SELECT_UNDO_THRESHOLD ) ) ),
                min( 255, int( penColour[1] + ( 255 / self.SELECT_UNDO_THRESHOLD ) ) ),
                max(   0, int( penColour[2] - ( 255 / self.SELECT_UNDO_THRESHOLD ) ) )
            ]
            self.model.selector.rectList[0][1] = penColour
            self.model.post("UPDATE_COLOUR")

    def releaseSelect(self):
        self.squinting = False
        self.squintCounter = max( 0, self.squintCounter - 1 )
        penColour = self.model.selector.rectList[0][1]
        #Increase red value, reduce other values
        penColour = [
            min( 255, int( penColour[0] + ( 255 / self.SELECT_UNDO_THRESHOLD ) ) ),
            max(   0, int( penColour[1] - ( 255 / self.SELECT_UNDO_THRESHOLD ) ) ),
            max(   0, int( penColour[2] - ( 255 / self.SELECT_UNDO_THRESHOLD ) ) )
        ]
        self.model.selector.rectList[0][1] = penColour
        self.model.post("UPDATE_COLOUR")

    def holdUndo(self):
        #If the user was some way thought selecting, release the select first
        if self.squintCounter > 0:
            self.releaseSelect()
        else:
            self.mouthOpen = True
            self.mouthCounter = min( self.SELECT_UNDO_THRESHOLD, self.mouthCounter + 1 )
            penColour = self.model.selector.rectList[0][1]
            #Increase the blue value, reduce other values
            penColour = [
                max(   0, int( penColour[0] - (255 / self.SELECT_UNDO_THRESHOLD) ) ),
                max(   0, int( penColour[1] - (255 / self.SELECT_UNDO_THRESHOLD) ) ),
                min( 255, int( penColour[2] + (255 / self.SELECT_UNDO_THRESHOLD) ) )
            ]
            self.model.selector.rectList[0][1] = penColour
            self.model.post("UPDATE_COLOUR")

    def releaseUndo(self):
        self.mouthOpen = False
        self.mouthCounter = max( 0, self.mouthCounter - 1 )
        penColour = self.model.selector.rectList[0][1]
        #Increase the red value, reduce other values
        penColour = [
            min( 255, int( penColour[0] + (255 / self.SELECT_UNDO_THRESHOLD) ) ),
            max(   0, int( penColour[1] - (255 / self.SELECT_UNDO_THRESHOLD) ) ),
            max(   0, int( penColour[2] - (255 / self.SELECT_UNDO_THRESHOLD) ) )
        ]
        self.model.selector.rectList[0][1] = penColour
        self.model.post("UPDATE_COLOUR")
