from Util.shared_constants import SharedConstants
from imutils   import face_utils
from Util.analytics import Analytics

class CalibrateModel:

    def __init__(self):
        self.analytics     = Analytics()
        self.listeners     = []
        self.camQuality    = "original"
        self.stopped       = False
        self.frame         = None
        self.secondsNeeded = 3
        self.anchorPoints  = [0, 0, 0, 0]
        self.faceAligned   = False
        self.timeAligned   = 0
        self.faceDetected  = False
        self.landmarks     = None
        self.CONST         = SharedConstants()
        self.RED           = ( 0, 0,   165 )
        self.GREEN         = ( 0, 235, 0   )
        self.boundColours  = {
            "Face"  : self.RED,
            "LEye"  : self.RED,
            "REye"  : self.RED,
            "Nose"  : self.RED,
            "Mouth" : self.RED
        }

    def addListener(self, listener):
        self.listeners.append(listener)

    def post(self, event):
        for listener in self.listeners:
            listener.events(event)

    def getFrame(self, frame):
        self.frame = frame

    def setup(self):
        self.post("GET_FRAME")

        self.FRAME_WIDTH  = self.frame.shape[1]
        self.FRAME_HEIGHT = self.frame.shape[0]

        #Rectangles to place each face feature in
        self.BOUNDS = {
            "X_FACE"  : ( int( self.FRAME_WIDTH  * 0.25 ), int( self.FRAME_WIDTH *  0.75 ) ),
            "Y_FACE"  : ( int( self.FRAME_HEIGHT * 0.2  ), int( self.FRAME_HEIGHT * 0.8  ) ),
            "X_LEYE"  : ( int( self.FRAME_WIDTH  * 0.35 ), int( self.FRAME_WIDTH  * 0.5  ) ),
            "Y_LEYE"  : ( int( self.FRAME_HEIGHT * 0.35 ), int( self.FRAME_HEIGHT * 0.45 ) ),
            "X_REYE"  : ( int( self.FRAME_WIDTH  * 0.5  ), int( self.FRAME_WIDTH  * 0.65 ) ),
            "Y_REYE"  : ( int( self.FRAME_HEIGHT * 0.35 ), int( self.FRAME_HEIGHT * 0.45 ) ),
            "X_MOUTH" : ( int( self.FRAME_WIDTH  * 0.4  ), int( self.FRAME_WIDTH  * 0.6  ) ),
            "Y_MOUTH" : ( int( self.FRAME_HEIGHT * 0.55 ), int( self.FRAME_HEIGHT * 0.7  ) ),
            "X_NOSE"  : ( int( self.FRAME_WIDTH  * 0.48 ), int( self.FRAME_WIDTH  * 0.52 ) ),
            "Y_NOSE"  : ( int( self.FRAME_HEIGHT * 0.45 ), int( self.FRAME_HEIGHT * 0.55 ) )
        }

        self.post("NEXT_FRAME")

    def stop(self):
        self.stopped = True

    def run(self):
        self.setup()
        while not self.stopped:
            self.update()
        return self.anchorPoints

    def update(self):
        self.post("GET_FRAME")
        self.analytics.makeTimestamp( check=self.faceDetected )

        if self.faceDetected:
            #Average anchor points and stop the loop
            if self.secondsNeeded < 0:
                for i in range( len(self.anchorPoints) ):
                    self.anchorPoints[i] = int(self.anchorPoints[i] / 4)
                self.analytics.makeRecord(type="calibrate")
                self.post("STOP")
                self.stopped = True
                return

            leftSide  = self.landmarks[ self.CONST.LEFT_SIDE  ]
            rightSide = self.landmarks[ self.CONST.RIGHT_SIDE ]
            foreHead  = self.landmarks[ self.CONST.FOREHEAD   ]
            nose      = self.landmarks[ self.CONST.NOSE_TIP   ]
            chin      = foreHead[1] + ( 2*( nose[1] - foreHead[1] ) )
            tempAnchorPoints = [ leftSide[0], rightSide[0], foreHead[1], chin ]
            (lEyeStart,  lEyeEnd)  = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
            (rEyeStart,  rEyeEnd)  = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
            (mouthStart, mouthEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
            lEyePoints  = self.landmarks[ lEyeStart  : lEyeEnd  ]
            rEyePoints  = self.landmarks[ rEyeStart  : rEyeEnd  ]
            mouthPoints = self.landmarks[ mouthStart : mouthEnd ]

            #Check each landmark is within the correct rectangle
            checkList = [
                checkPointsWithinBounds( self.landmarks, self.BOUNDS["X_FACE"],  self.BOUNDS["Y_FACE"]  ), # FACE
                checkPointsWithinBounds( lEyePoints,     self.BOUNDS["X_REYE"],  self.BOUNDS["Y_REYE"]  ), # LEFT EYE
                checkPointsWithinBounds( rEyePoints,     self.BOUNDS["X_LEYE"],  self.BOUNDS["Y_LEYE"]  ), # RIGHT EYE
                checkPointsWithinBounds( [nose],         self.BOUNDS["X_NOSE"],  self.BOUNDS["Y_NOSE"]  ), # NOSE
                checkPointsWithinBounds( mouthPoints,    self.BOUNDS["X_MOUTH"], self.BOUNDS["Y_MOUTH"] )  # MOUTH
            ]

            checkSum = 0
            #Change the colour of the rectangle, depending on the outcome of the previous checks
            for i, key in enumerate( self.boundColours ):
                if checkList[i]:
                    checkSum += 1
                    self.boundColours[key] = self.GREEN
                else:
                    self.boundColours[key] = self.RED

            #If all checks are successful, continue the aligned timer
            if checkSum == len( checkList ):
                self.faceAligned = True
                self.timeAligned += 1
                if self.timeAligned % 10 == 0:
                    for i in range( len(self.anchorPoints) ):
                        self.anchorPoints[i] += tempAnchorPoints[i]
                    self.secondsNeeded -= 1
            else:
                self.faceAligned   = False
                self.timeAligned   = 0
                self.secondsNeeded = 3
                self.anchorPoints  = [0, 0, 0, 0]

        else:
            self.timeAligned   = 0
            self.secondsNeeded = 3
            for key in self.boundColours:
                self.boundColours[key] = self.RED

        self.post("NEXT_FRAME")


def checkPointsWithinBounds(points, xBounds, yBounds):
    for point in points:
        if (point[0] < xBounds[0]) or (point[0] > xBounds[1]) or (point[1] > yBounds[1]) or (point[1] < yBounds[0]):
            return False
    return True