from Menu.base_menu_controller  import BaseMenuController
from Util.Face_Detector.detection_utils import eyeAspectRatio

class TutorialController( BaseMenuController ):

    def __init__(self, model):
        BaseMenuController.__init__(self, model)

    def controller(self):

        detected, landmarks = self.getLandmarks()
        if detected:
            self.toggleStatus("ON")

            lEar = eyeAspectRatio( landmarks, eye="left_eye"  )
            rEar = eyeAspectRatio( landmarks, eye="right_eye" )

            if (lEar <= self.SQUINT_THRESHOLD) and (rEar <= self.SQUINT_THRESHOLD):
                self.holdSelect()
                if self.squintCounter == self.SELECT_UNDO_THRESHOLD:
                    self.squinting = False
                    self.squintCounter = 0
                    self.instructionCounter = 0
                    self.model.post("RECORD")
                    self.model.onMenu     = True
                    self.model.onTutorial = False
                    self.model.transitionUI( direction="DOWN" )
                    self.model.post("CHANGE_INSTRUCTION")
                    self.model.changeController()
            else:
                self.releaseSelect()

        else:
            self.toggleStatus("OFF")