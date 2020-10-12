import time

class Analytics:

    def __init__(self):
        self.detected = True
        self.detectedSeconds = 0
        self.undetectedSeconds = 0
        self.startT = time.time()

    def makeTimestamp(self, check):
        if check != self.detected:
            if self.detected:
                currentT = time.time()
                timeDetected = currentT - self.startT
                self.detectedSeconds += timeDetected
                self.detected = False
            else:
                currentT = time.time()
                timeUndetected = currentT - self.startT
                self.undetectedSeconds += timeUndetected
                self.detected = True
            self.startT = time.time()

    def makeRecord(self, type, newline=False):
        endT = time.time()
        if self.detected:
            timeDetected = endT - self.startT
            self.detectedSeconds += timeDetected
        else:
            timeunDetected = endT - self.startT
            self.undetectedSeconds += timeunDetected
        self.startT = time.time()
        totalTime = self.detectedSeconds + self.undetectedSeconds
        with open("analytics.txt", 'a') as f:
            f.write(f"{type} total time: {totalTime:.2f}, detected time: {self.detectedSeconds:.2f}, "
                    f"undetected time: {self.undetectedSeconds:.2f}, "
                    f"percentage time detected: {(self.detectedSeconds / totalTime)*100:.2f}%\n")
            if newline:
                f.write("end of sesion\n")