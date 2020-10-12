#Fix for pyinstaller, so the program can be used as an .exe file
from Util.ammend_import import _append_run_path
_append_run_path()
from PyQt5           import QtWidgets, QtCore, QtGui, QtTest
from PyQt5.QtWidgets import QWidget

class MenuView( QWidget ):

    def __init__(self, size, model):
        super().__init__()

        self.FRAME_WAIT = 1

        self.model = model
        self.model.addListener( self )
        widthSpace  = size.width() - self.model.WIDTH
        heightSpace = size.height() - self.model.HEIGHT
        #Centres the window on the users screen
        self.setGeometry( widthSpace * 0.5, heightSpace * 0.5, self.model.WIDTH, self.model.HEIGHT )
        self.setFixedSize( self.size() )
        self.setWindowTitle("Main Menu")

        self.qtGameIcons = []
        for game in self.model.gameIconList:
            gameIcons = []
            for imageIcon in game:
                gameIcons.append( self.placeImageIcon( imageIcon ) )
            self.qtGameIcons.append( gameIcons )

        self.qtSettingsCrosses = []
        for imageIcon in self.model.settingsCrosses:
            self.qtSettingsCrosses.append( self.placeImageIcon( imageIcon ) )

        self.qtSettingsIcons = []
        for i, pixmapIcon in enumerate( self.model.settingsIcons ):
            self.qtSettingsIcons.append( self.placePixmapIcon( pixmapIcon ) )

        self.qtTutorialBack = self.placeImageIcon( self.model.backButton )

        self.qtInstructions = self.placePixmapIcon( self.model.instructions )

        self.qtLabelDict = {}
        for key, label in self.model.labelDict.items():
            self.qtLabelDict[key] = self.placeLabel( label )
        for key in self.qtLabelDict:
            if key.startswith("description") or key.startswith("instruction"):
                self.qtLabelDict[key].hide()
        self.qtLabelDict["description0"].show()
        self.qtLabelDict["instructionsMenu0"].show()

        self.qtSelector = self.placePixmapIcon(self.model.selector)

    def placeLabel(self, modelLabel):
        label = QtWidgets.QLabel( self )
        label.setGeometry(
            QtCore.QRect( modelLabel.rect[0], modelLabel.rect[1], modelLabel.rect[2], modelLabel.rect[3] )
        )
        font = QtGui.QFont()
        font.setFamily( modelLabel.fontType )
        font.setPointSize( modelLabel.fontSize )
        label.setFont( font )
        label.setText( modelLabel.text )
        return label

    def placeImageIcon(self, modelImageIcon):
        imageIcon = QtWidgets.QLabel( self )
        imageIcon.setPixmap( QtGui.QPixmap( modelImageIcon.image ) )
        imageIcon.setScaledContents( True )
        imageIcon.setGeometry(
            QtCore.QRect( modelImageIcon.rect[0], modelImageIcon.rect[1], modelImageIcon.rect[2], modelImageIcon.rect[3] )
        )
        return imageIcon

    def placePixmapIcon(self, modelPixmapIcon):
        pixmapIcon = QtWidgets.QLabel( self )
        pixmapIcon.setGeometry( modelPixmapIcon.canvasRect[0], modelPixmapIcon.canvasRect[1],
                                modelPixmapIcon.canvasRect[2], modelPixmapIcon.canvasRect[3] )

        pixmap = getPixmap( canvWidth=modelPixmapIcon.canvasRect[2], canvHeight=modelPixmapIcon.canvasRect[3],
                            penWidth=modelPixmapIcon.penWidth,
                            rectList=modelPixmapIcon.rectList )

        pixmapIcon.setPixmap( pixmap )
        return pixmapIcon

    def moveGameIcons(self):
        for i, gameIcons in enumerate( self.qtGameIcons ):
            for j, gameIcon in enumerate( gameIcons ):
                gameIcon.move( self.model.gameIconList[i][j].rect[0], self.model.gameIconList[i][j].rect[1] )
        QtTest.QTest.qWait( self.FRAME_WAIT )

    def moveSelector(self):
        #Moves the selector

        selectorX  = self.model.selector.canvasRect[0]
        selectorY  = self.model.selector.canvasRect[1]
        pixmapRect = self.model.selector.rectList[0][0]
        self.qtSelector.move( selectorX, selectorY )

        #If on the main menu, the selector canvas should change height depending on its y position
        if self.model.onMenu:
            MAX_DIST = self.model.GAME_SUB_ICON_HEIGHT
            MAX_RECT_HEIGHT = self.model.GAME_ICON_SIZE - self.model.GAME_SUB_ICON_HEIGHT
            currentDist = abs( self.model.GAME_CENTRE_Y - selectorY )
            rectHeightChange = currentDist * (MAX_RECT_HEIGHT / MAX_DIST)

            if selectorY < self.model.GAME_CENTRE_Y:
                pixmapRect[3] = self.model.GAME_ICON_SIZE - rectHeightChange
                self.model.selector.rectList[0][0] = pixmapRect
                pixmap = getPixmap( canvWidth=self.model.selector.canvasRect[2],
                                    canvHeight=self.model.selector.canvasRect[3], penWidth=self.model.selector.penWidth,
                                    rectList=self.model.selector.rectList )
                self.qtSelector.setPixmap( pixmap )

            elif selectorY > self.model.GAME_CENTRE_Y:
                pixmapRect[1] = rectHeightChange
                pixmapRect[3] = self.model.GAME_ICON_SIZE - rectHeightChange
                self.model.selector.rectList[0][0] = pixmapRect
                pixmap = getPixmap( canvWidth=self.model.selector.canvasRect[2],
                                    canvHeight=self.model.selector.canvasRect[3], penWidth=self.model.selector.penWidth,
                                    rectList=self.model.selector.rectList )
                self.qtSelector.setPixmap( pixmap )

        QtTest.QTest.qWait( self.FRAME_WAIT )


    def updateSelectorColour(self):
        pixmap = getPixmap( canvWidth=self.model.selector.canvasRect[2],
                            canvHeight=self.model.selector.canvasRect[3], penWidth=self.model.selector.penWidth,
                            rectList=self.model.selector.rectList )
        self.qtSelector.setPixmap(pixmap)
        QtTest.QTest.qWait( self.FRAME_WAIT )

    def changeLabels(self):
        title, highscore = self.model.gamesList[ self.model.iconPointer[0] ]
        self.qtLabelDict["title"].setText( title )
        self.qtLabelDict["highscore"].setText( highscore )

    def changeSettingFocus(self):
        #Change the opacity of different elements on the settings screen

        NUM_SETTINGS = 4

        for i in range( NUM_SETTINGS ):
            self.qtLabelDict[ "description" + str(i) ].hide()
            transparentCross = QtGui.QPixmap( "Menu/Images/t_cross.png" )
            self.qtSettingsCrosses[i].setPixmap( transparentCross )
            newPixmap = getPixmap( canvWidth=self.model.settingsIcons[i].canvasRect[2],
                                   canvHeight=self.model.settingsIcons[i].canvasRect[3],
                                   penWidth=self.model.settingsIcons[i].penWidth,
                                   rectList=self.model.settingsIcons[i].rectList, opacity=75 )
            self.qtSettingsIcons[i].setPixmap( newPixmap )

            for key, text in self.model.labelDict.items():
                if key.startswith("setting"):
                    transparentSettingText = '<div style="color: rgba(0, 0, 0, 0.5);">' + \
                                                self.model.labelDict[key].text + \
                                             '</div>'
                    self.qtLabelDict[key].setText( transparentSettingText )

        pointer = self.model.settingsPointer[1]
        cross = QtGui.QPixmap( self.model.settingsCrosses[pointer].image )
        self.qtSettingsCrosses[pointer].setPixmap( cross )
        newPixmap = getPixmap( canvWidth=self.model.settingsIcons[pointer].canvasRect[2],
                               canvHeight=self.model.settingsIcons[pointer].canvasRect[3],
                               penWidth=self.model.settingsIcons[pointer].penWidth,
                               rectList=self.model.settingsIcons[pointer].rectList )
        self.qtSettingsIcons[pointer].setPixmap(newPixmap)

        self.qtLabelDict[ "description" + str( pointer ) ].show()


        for key, text in self.model.labelDict.items():
            if key.startswith( "setting" + str( self.model.settingsPointer[1] ) ):
                settingText = self.model.labelDict[key].text
                self.qtLabelDict[key].setText( settingText )

        SELECT_SETTING_WAIT = 400
        QtTest.QTest.qWait( SELECT_SETTING_WAIT )

    def updateSettingsCrosses(self):
        for i, imageIcon in enumerate( self.qtSettingsCrosses ):
            imageIcon.move( self.model.settingsCrosses[i].rect[0], self.model.settingsCrosses[i].rect[1] )
        QtTest.QTest.qWait( self.FRAME_WAIT )

    def transitionUI(self):
        self.moveGameIcons()
        self.updateSettingsCrosses()

        for key, label in self.qtLabelDict.items():
            label.move( self.model.labelDict[key].rect[0], self.model.labelDict[key].rect[1] )

        for i, pixmapIcon in enumerate( self.qtSettingsIcons ):
            pixmapIcon.move( self.model.settingsIcons[i].canvasRect[0], self.model.settingsIcons[i].canvasRect[1] )

        self.qtTutorialBack.move( self.model.backButton.rect[0], self.model.backButton.rect[1] )

        self.qtSelector.move( self.model.selector.canvasRect[0], self.model.selector.canvasRect[1] )
        pixmap = getPixmap( canvWidth=self.model.selector.canvasRect[2], canvHeight=self.model.selector.canvasRect[3],
                            penWidth=self.model.selector.penWidth, rectList=self.model.selector.rectList )
        self.qtSelector.setPixmap( pixmap )

        if self.model.onMenu:
            self.setWindowTitle("Main Menu")
        elif self.model.onSettings:
            self.setWindowTitle("Settings")
        elif self.model.onTutorial:
            self.setWindowTitle("Tutorial")

        QtTest.QTest.qWait( self.FRAME_WAIT )

    def changeTutorialLabels(self):
        currentGameName = self.model.gamesList[ self.model.iconPointer[0] ]
        for key in self.qtLabelDict:
            if key.endswith("tutorial") and not key.startswith( currentGameName ):
                self.qtLabelDict[key].hide()
            elif key.endswith("tutorial") and key.startswith( currentGameName ):
                self.qtLabelDict[key].show()

    def changeStatus(self):
        pixmap = getPixmap( canvWidth=self.model.instructions.canvasRect[2],
                            canvHeight=self.model.instructions.canvasRect[3],
                            penWidth=self.model.instructions.penWidth, rectList=self.model.instructions.rectList )
        self.qtInstructions.setPixmap( pixmap )
        self.qtLabelDict["status"].setText( self.model.labelDict["status"].text )

        QtTest.QTest.qWait( self.FRAME_WAIT )

    def changeInstruction(self):
        menuKey     = "instructionsMenu"
        settingsKey = "instructionsSettings"
        tutorialKey = "instructionTutorial"

        if self.model.onTutorial:
            #Hide all other instructions that may be visible
            for i in range( 3 ):
                if self.qtLabelDict[ menuKey + str(i) ].isVisible():
                    self.qtLabelDict[ menuKey + str(i) ].hide()
                if self.qtLabelDict[ settingsKey + str(i) ].isVisible():
                    self.qtLabelDict[ settingsKey + str(i) ].hide()
            if self.qtLabelDict[ menuKey + "3" ].isVisible():
                self.qtLabelDict[ menuKey + "3" ].hide()
            #Show the tutorial instruction
            self.qtLabelDict[ tutorialKey ].show()

            QtTest.QTest.qWait( self.FRAME_WAIT )
            return

        elif self.model.onMenu:
            currentKey = menuKey
            otherKey   = settingsKey
            currNumInstructions  = self.model.numMenuInstructions
            otherNumInstructions = self.model.numSettingsInstructions

        elif self.model.onSettings:
            currentKey = settingsKey
            otherKey   = menuKey
            currNumInstructions  = self.model.numSettingsInstructions
            otherNumInstructions = self.model.numMenuInstructions

        #Loop for all instructions on current GUI part
        for i in range( currNumInstructions ):
            #If one of the instructions is visible, make it invisible, and show the next instruction
            if self.qtLabelDict[ currentKey + str(i) ].isVisible():
                self.qtLabelDict[ currentKey + str(i) ].hide()
                if i == currNumInstructions - 1:
                    self.qtLabelDict[ currentKey + "0" ].show()
                else:
                    self.qtLabelDict[ currentKey + str(i + 1) ].show()
                break
        #If none of the instructions were visible, we must be transitioning to this part of the GUI
        else:
            #Hide all other intructions that may be visible
            if self.qtLabelDict[ tutorialKey ].isVisible():
                self.qtLabelDict[ tutorialKey ].hide()
            for i in range( otherNumInstructions ):
                if self.qtLabelDict[ otherKey + str(i) ].isVisible():
                    self.qtLabelDict[ otherKey + str(i) ].hide()
            #Now show the first instruction of the the current GUI section
            self.qtLabelDict[currentKey + "0"].show()

        QtTest.QTest.qWait( self.FRAME_WAIT )

    def closeEvent(self, event):
        self.model.exit()

    def events(self, event):

        if event == "MOVE_GAMES":
            self.moveGameIcons()
        elif event == "MOVE_SELECTOR":
            self.moveSelector()
        elif event == "UPDATE_COLOUR":
            self.updateSelectorColour()
        elif event == "CHANGE_LABELS":
            self.changeLabels()
        elif event == "CHANGE_CROSSES":
            self.updateSettingsCrosses()
        elif event == "CHANGE_SETTING_FOCUS":
            self.changeSettingFocus()
        elif event == "UPDATE_STATUS":
            self.changeStatus()
        elif event == "CHANGE_INSTRUCTION":
            self.changeInstruction()
        elif event == "TRANSITION_UI":
            self.transitionUI()
        elif event == "CHANGE_TUTORIAL":
            self.changeTutorialLabels()
        elif event == "STOP":
            self.close()


def getPixmap(canvWidth, canvHeight, penWidth, rectList, opacity=255):
    """
    Returns a pixmap that shows a list of desired rectangles

    :param canvWidth:  Width of the canvas
    :param canvHeight: Height of the canvas
    :param penWidth:   Width of the rectangle outlines
    :param rectList:   List of rectangles to draw
    :param opacity:    Opacity of the final pixmap
    :return: The final pixmap showing all rectangles
    """
    pixmap = QtGui.QPixmap( canvWidth, canvHeight )
    pixmap.fill( QtCore.Qt.transparent )

    painter = QtGui.QPainter( pixmap )

    pen = QtGui.QPen()
    pen.setWidth( penWidth )

    brush = QtGui.QBrush()

    for rect in rectList:
        #Unpack the current rectangle into its individual properties
        x, y, width, height = rect[0]
        penColour  = rect[1]
        style      = rect[2]
        backColour = rect[3]
        #Setup the pen and brush
        pen.setColor( QtGui.QColor( penColour[0], penColour[1], penColour[2], opacity ) )
        if style == "solid":
            pen.setStyle( QtCore.Qt.SolidLine )
        elif style == "dotted":
            pen.setStyle( QtCore.Qt.DashLine )
        if backColour:
            brush.setStyle( QtCore.Qt.SolidPattern )
            brush.setColor( QtGui.QColor( backColour[0], backColour[1], backColour[2] ) )
        else:
            brush.setColor( QtGui.QColor( 0, 0, 0, 0 ) )
        #Draw the rectangle
        painter.setPen( pen )
        painter.setBrush( brush )
        painter.drawRect( x, y, width, height )
    painter.end()

    return pixmap
