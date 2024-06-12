from marscam import*

class CameraContrastech():
    
    def __init__(self) -> None:
        super().__init__()
        self._run_flag = True
        self.cam = None
        self.rescale_factor = 0
    
    def run(self):
        while self._run_flag:
            self.image = self.cam.stream()
            self.update_frame.emit(self.image)

    def opencam(self):
        self.cam =  marscam.marscam()
        self.cam.setCamera(0)
        self.cam.openCamera()
        
    def setExposureAuto(self, mode):
        self.cam.setExposureAuto(mode)

    def setWhiteBalance(self, mode):
        self.cam.setWBAuto(mode)

    def setBrightness(self, val):
        self.cam.setBrightness(val)

    def setExposure(self, val):
        self.cam.setExposureTime(val)

    def setGainRaw(self, val):
        self.cam.setGainRaw(val)

    def setGamma(self, val):
        self.cam.setGamma(val)

    def setSharpnessEnable(self, val):
        self.cam.setSharpnessEnable(str(val))

    def setSharpness(self, val):
        self.cam.setSharpness(val)

    def setWBRatio(self, channel, dval):
        self.cam.setWBRatio(channel, dval)

    def rescale_frame(self, frame, percent=75):
        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    def saveimage(self, dir):
        while not self.cekfile(dir):
            print("save image : " + dir)
            img = self.cam.stream()
            cv2.imwrite(dir + ".jpg", img)
        self.fileExist.emit()

    def stop(self):
        self._run_flag = False
        self.wait()