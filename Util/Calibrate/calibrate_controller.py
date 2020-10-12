from Util.Face_Detector.base_face_controller import BaseFaceController

class CalibrateController(BaseFaceController):

    def __init__(self, model):
        BaseFaceController.__init__(self, model=model)

    def nextFrame(self):
        self.model.faceDetected, self.model.landmarks = self.getLandmarks()