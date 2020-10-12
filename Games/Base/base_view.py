from Util.shared_constants import SharedConstants
import pygame
import cv2

class BaseView:

    def __init__(self, model):
        pygame.init()

        MAIN_FONT_SIZE = 25
        FONT_TYPE = "Sans"
        self.CONST = SharedConstants()

        self.model = model
        self.model.addListener( self )

        self.gameDisplay = pygame.display.set_mode( (self.model.width, self.model.height) )
        self.clock       = pygame.time.Clock()
        self.MAIN_FONT   = pygame.font.SysFont( FONT_TYPE, MAIN_FONT_SIZE )

        if self.model.showCam:
            self.ROTATE_DEGREES   = 270
            self.RED              = ( 165, 0,   0 )
            self.GREEN            = ( 0,   235, 0 )
            self.SCALE_X_VAL      = int( self.model.width  * 0.2 )
            self.SCALE_Y_VAL      = int( self.model.height * 0.2 )
            self.CAM_X_POS        = 4 * self.SCALE_X_VAL
            self.CAM_Y_POS        = 4 * self.SCALE_Y_VAL
            self.THICKNESS        = 20
            DETECTED_FONT_SIZE    = 15
            self.DETECTED_FONT    = pygame.font.SysFont( FONT_TYPE, DETECTED_FONT_SIZE )
            self.HIGHLIGHT_PADDING = 3

        pygame.display.set_caption( self.model.name )

    def messageToScreen(self, msg, colour, pos, font):
        screenText = font.render( msg, True, colour )
        self.gameDisplay.blit( screenText, pos )

    def renderFrame(self):
        self.gameDisplay.fill( self.CONST.WHITE )

        scoreText = "SCORE: " + str( self.model.score )
        self.messageToScreen( msg=scoreText, colour=self.CONST.BLACK, pos=(0, 0), font=self.MAIN_FONT )
        livesText = "LIVES: " + str( self.model.player.lives )
        self.messageToScreen( msg=livesText, colour=self.CONST.BLACK, pos=(200, 0), font=self.MAIN_FONT )

        pygame.draw.rect(
            self.gameDisplay,
            self.CONST.BLUE,
            [self.model.player.x, self.model.player.y, self.model.player.size, self.model.player.size]
        )

        for obstacle in self.model.obstacles:
            pygame.draw.rect(
                self.gameDisplay,
                self.CONST.RED,
                [obstacle.x, obstacle.y, obstacle.width, obstacle.height]
            )

        if self.model.showCam:
            self.showCam()

        pygame.display.update()
        self.clock.tick( self.model.fps )
        self.model.numFrames += 1

    def showCam(self):
        #Displays webcam frames

        frame = self.model.frame
        frameHeight, frameWidth, _ = frame.shape
        rectColour = self.GREEN if self.model.detected else self.RED
        text       = "Detected" if self.model.detected else "Not Detected"
        textWidth, textHeight = self.DETECTED_FONT.size( text )
        cv2.rectangle( frame, pt1=(0, 0), pt2=(frameWidth, frameHeight+self.THICKNESS),
                       color=rectColour, thickness=self.THICKNESS )
        surface = pygame.surfarray.make_surface( frame )
        surface = pygame.transform.rotate( surface, self.ROTATE_DEGREES )
        surface = pygame.transform.scale( surface, (self.SCALE_X_VAL, self.SCALE_Y_VAL) )

        textHighlight = pygame.Surface( (textWidth + (2 * self.HIGHLIGHT_PADDING), textHeight + self.HIGHLIGHT_PADDING) )
        textHighlight.fill( rectColour )

        self.gameDisplay.blit( surface, (self.CAM_X_POS, self.CAM_Y_POS) )
        self.gameDisplay.blit( textHighlight, (self.CAM_X_POS, self.CAM_Y_POS) )
        self.messageToScreen( msg=text, colour=self.CONST.BLACK, font=self.DETECTED_FONT,
                              pos=(self.CAM_X_POS+self.HIGHLIGHT_PADDING, self.CAM_Y_POS) )

    def events(self, event):
        if event == "NEXT_FRAME":
            self.renderFrame()
        elif event == "STOP":
            quitGame()

def quitGame():
    pygame.quit()