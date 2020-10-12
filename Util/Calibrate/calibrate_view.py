import cv2

class CalibrateView:

    def __init__(self, model):
        self.model = model
        self.model.addListener(self)
        self.YELLOW             = ( 75,  255, 255 )
        self.PURPLE             = ( 130, 0,   75  )
        self.BLACK              = ( 0,   0,   0   )
        self.FONT_TYPE          = cv2.FONT_HERSHEY_COMPLEX
        self.TOP_TEXT           = "Face: "
        self.BOTTOM_TEXT1       = "Centre your face, eyes, mouth and nose tip inside of each box,"
        self.BOTTOM_TEXT2       = "and look towards the middle of your screen."
        self.FONT_SCALE         = 0.5
        self.FEATURE_FONT_SCALE = 0.4
        self.DETECTED_TEXT1     = "not detected - Make sure you have good lighting"
        self.DETECTED_TEXT2     = "and hair is not covering your face."
        self.PADDING            = 2
        (self.TEXT_WIDTH, self.TEXT_HEIGHT) = cv2.getTextSize(
            self.TOP_TEXT, self.FONT_TYPE, fontScale=self.FONT_SCALE, thickness=1
        )[0]
        self.FACE_EYE_PADDING_Y     = int( self.TEXT_HEIGHT * 0.45 )
        self.MOUTH_PADDING_Y        = int( self.TEXT_HEIGHT )
        self.OTHER_FEATURES_PADDING = 3

    def renderFrame(self):
        frame = self.model.frame
        frame = cv2.flip( frame, 1 )

        # DETECTION TEXT
        if self.model.faceDetected:
            if self.model.faceAligned:
                secondsNeeded = self.model.secondsNeeded if self.model.secondsNeeded > 0 else 0
                secondsText  = "second." if secondsNeeded == 1 else "seconds."
                detectedText = f"aligned, hold still for {secondsNeeded} more {secondsText}"
            else:
                detectedText = "detected, now align the rest of your face in the boxes"
            putHighlightedText( frame, text=[detectedText], textColour=self.YELLOW, highlightColour=self.PURPLE,
                                font=self.FONT_TYPE, scale=self.FONT_SCALE,
                                pos=(self.TEXT_WIDTH, self.model.FRAME_HEIGHT-self.TEXT_HEIGHT) )
        else:
            detectedText1 = "not detected - Make sure you have good lighting"
            detectedText2 = "and hair is not covering your face."
            putHighlightedText( frame, text=[detectedText1, detectedText2], textColour=self.YELLOW,
                                highlightColour=self.PURPLE, font=self.FONT_TYPE, scale=self.FONT_SCALE,
                                pos=( self.TEXT_WIDTH, self.model.FRAME_HEIGHT-(2*self.TEXT_HEIGHT) ) )

        #INSTRUCTION TEXT
        putHighlightedText( frame, text=[self.TOP_TEXT], textColour=self.YELLOW, highlightColour=self.PURPLE,
                            font=self.FONT_TYPE, scale=self.FONT_SCALE, pos=(0, self.model.FRAME_HEIGHT-self.TEXT_HEIGHT) )

        putHighlightedText( frame, text=[self.BOTTOM_TEXT1, self.BOTTOM_TEXT2], pos=(0, self.TEXT_HEIGHT),
                            textColour=self.YELLOW, highlightColour=self.PURPLE,
                            font=self.FONT_TYPE, scale=self.FONT_SCALE )

        # RECTANGLE LABELS
        putHighlightedText( frame, text=["Face "], font=self.FONT_TYPE, scale=self.FONT_SCALE,
                            textColour=self.BLACK, highlightColour=self.model.boundColours["Face"],
                            pos=( self.model.BOUNDS["X_FACE"][0]+self.OTHER_FEATURES_PADDING,
                                  self.model.BOUNDS["Y_FACE"][0]-self.FACE_EYE_PADDING_Y ) )

        putHighlightedText( frame, text=["Left Eye "], font=self.FONT_TYPE, scale=self.FEATURE_FONT_SCALE,
                            textColour=self.BLACK, highlightColour=self.model.boundColours["LEye"],
                            pos=( self.model.BOUNDS["X_LEYE"][0] + self.OTHER_FEATURES_PADDING,
                                  self.model.BOUNDS["Y_LEYE"][0] - self.FACE_EYE_PADDING_Y ) )

        putHighlightedText( frame, text=["Right Eye "], font=self.FONT_TYPE, scale=self.FEATURE_FONT_SCALE,
                            textColour=self.BLACK, highlightColour=self.model.boundColours["REye"],
                            pos=( self.model.BOUNDS["X_REYE"][0] + self.OTHER_FEATURES_PADDING,
                                  self.model.BOUNDS["Y_REYE"][0] - self.FACE_EYE_PADDING_Y ) )

        putHighlightedText( frame, text=["Mouth "], font=self.FONT_TYPE, scale=self.FEATURE_FONT_SCALE,
                            textColour=self.BLACK, highlightColour=self.model.boundColours["Mouth"],
                            pos=( self.model.BOUNDS["X_MOUTH"][0] + self.OTHER_FEATURES_PADDING,
                                  self.model.BOUNDS["Y_MOUTH"][1] + self.MOUTH_PADDING_Y ) )

        putHighlightedText( frame, text=["Nose Tip "], font=self.FONT_TYPE, scale=self.FEATURE_FONT_SCALE,
                            textColour=self.BLACK, highlightColour=self.model.boundColours["Nose"],
                            pos=( self.model.BOUNDS["X_NOSE"][1] + self.OTHER_FEATURES_PADDING,
                                  self.model.BOUNDS["Y_NOSE"][1] - self.OTHER_FEATURES_PADDING ) )

        #RECTANGLES
        cv2.rectangle( frame, pt1=( self.model.BOUNDS["X_NOSE"][0], self.model.BOUNDS["Y_NOSE"][0] ),
                              pt2=( self.model.BOUNDS["X_NOSE"][1], self.model.BOUNDS["Y_NOSE"][1] ),
                              color=self.model.boundColours["Nose"], thickness=self.PADDING )
        cv2.rectangle( frame, pt1=( self.model.BOUNDS["X_FACE"][0], self.model.BOUNDS["Y_FACE"][0] ),
                              pt2=( self.model.BOUNDS["X_FACE"][1], self.model.BOUNDS["Y_FACE"][1] ),
                              color=self.model.boundColours["Face"], thickness=self.PADDING)
        cv2.rectangle( frame, pt1=( self.model.BOUNDS["X_LEYE"][0], self.model.BOUNDS["Y_LEYE"][0] ),
                              pt2=( self.model.BOUNDS["X_LEYE"][1], self.model.BOUNDS["Y_LEYE"][1] ),
                              color=self.model.boundColours["LEye"], thickness=self.PADDING)
        cv2.rectangle( frame, pt1=( self.model.BOUNDS["X_REYE"][0], self.model.BOUNDS["Y_REYE"][0] ),
                              pt2=( self.model.BOUNDS["X_REYE"][1], self.model.BOUNDS["Y_REYE"][1] ),
                              color=self.model.boundColours["REye"], thickness=self.PADDING)
        cv2.rectangle( frame, pt1=( self.model.BOUNDS["X_MOUTH"][0], self.model.BOUNDS["Y_MOUTH"][0] ),
                              pt2=( self.model.BOUNDS["X_MOUTH"][1], self.model.BOUNDS["Y_MOUTH"][1] ),
                              color=self.model.boundColours["Mouth"], thickness=self.PADDING )

        # SHOW FRAME
        cv2.imshow( "Calibration", frame )
        cv2.waitKey( 1 )

    def events(self, event):
        if event == "NEXT_FRAME":
            self.renderFrame()
        elif event == "STOP":
            cv2.destroyAllWindows()


def putHighlightedText(frame, text, pos, font, scale, textColour, highlightColour, padding=2):
    # Displays a set of lines with a box as a highlighted background
    text_width = 0
    # Find the most wide line
    for line in text:
        line_width = cv2.getTextSize(line, font, scale, thickness=1)[0][0]
        if line_width > text_width:
            text_width = line_width
    # Each line will be the same height
    line_height = cv2.getTextSize(text[0], font, scale, thickness=1)[0][1]
    # Height of all the lines
    text_height = line_height * len(text)

    # Start and end points of the highlight, which will cover all lines of text
    highlight_coords = (
        ( pos[0] - (2*padding), pos[1] + line_height*(len(text) - 1) + (2*padding) ),
        ( pos[0] + text_width - padding, pos[1] - text_height - padding )
    )
    # Draw the rectangle from the previously calculated points
    cv2.rectangle(frame, highlight_coords[0], highlight_coords[1], highlightColour, cv2.FILLED)
    hight_offset = 0
    # Draw each line in text, progressively starting further down depending on the line number
    for line in text:
        cv2.putText(frame, line, (pos[0], pos[1] + line_height*hight_offset), font, fontScale=scale, color=textColour, thickness=1)
        hight_offset += 1