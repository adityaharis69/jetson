from ImageConvert import *
from MVSDK import *
import struct
import time
import datetime
import numpy
import cv2
import gc


g_cameraStatusUserInfo = b"statusInfo"



class BITMAPFILEHEADER(Structure):
    _fields_ = [
                ('bfType', c_ushort),
                ('bfSize', c_uint),
                ('bfReserved1', c_ushort),
                ('bfReserved2', c_ushort),
                ('bfOffBits', c_uint),
                ]
 
class BITMAPINFOHEADER(Structure):
    _fields_ = [
                ('biSize', c_uint),
                ('biWidth', c_int),
                ('biHeight', c_int),
                ('biPlanes', c_ushort),
                ('biBitCount', c_ushort),
                ('biCompression', c_uint),
                ('biSizeImage', c_uint),
                ('biXPelsPerMeter', c_int),
                ('biYPelsPerMeter', c_int),
                ('biClrUsed', c_uint),
                ('biClrImportant', c_uint),
                ] 

# 调色板，只有8bit及以下才需要
# color palette
class RGBQUAD(Structure):
    _fields_ = [
                ('rgbBlue', c_ubyte),
                ('rgbGreen', c_ubyte),
                ('rgbRed', c_ubyte),
                ('rgbReserved', c_ubyte),
                ]


def deviceLinkNotify(connectArg, linkInfo):
    if (EVType.offLine == connectArg.contents.m_event):
        print("camera has off line, userInfo [%s]" % (
            c_char_p(linkInfo).value))
    elif (EVType.onLine == connectArg.contents.m_event):
        print("camera has on line, userInfo [%s]" % (c_char_p(linkInfo).value))



# grabbing callback function                             
def onGetFrame(frame):
    nRet = frame.contents.valid(frame)
    if ( nRet != 0):
        print("frame is invalid!")
        # 释放驱动图像缓存资源
        # release frame resource before return
        frame.contents.release(frame)
        return    
    
    print("BlockId = %d"  %(frame.contents.getBlockId(frame)))
    #此处客户应用程序应将图像拷贝出使用
    #Here you can copy image data out from frame for your own use
    '''
    '''
    # 释放驱动图像缓存资源
    # release frame resource at the end of use
    frame.contents.release(frame)

# 取流回调函数Ex
# grabbing callback function with userInfo parameter
def onGetFrameEx(frame, userInfo):
    nRet = frame.contents.valid(frame)
    if ( nRet != 0):
        print("frame is invalid!")
        # 释放驱动图像缓存资源
        # release frame resource before return
        frame.contents.release(frame)
        return         
 
    print("BlockId = %d userInfo = %s"  %(frame.contents.getBlockId(frame), c_char_p(userInfo).value))
    #此处客户应用程序应将图像拷贝出使用
    #Here you should copy image data out from frame for your own use
    '''
    '''
    # 释放驱动图像缓存资源
    # release frame resource at the end of use
    frame.contents.release(frame)


connectCallBackFuncEx = connectCallBackEx(deviceLinkNotify)
frameCallbackFunc = callbackFunc(onGetFrame)
frameCallbackFuncEx = callbackFuncEx(onGetFrameEx)


connectCallBackFuncEx = connectCallBackEx(deviceLinkNotify)



class marscam:

    def __init__(self):
        self.nRet = None
        self.streamSourceInfo = None
        self.streamSource = None
        self.trigModeEnumNode = None
        self.trigModeEnumNodeInfo = None
        self.camera = 0
        self.status=False
        self.ss=0
        

    # subscribe camera connection status change
    def subscribeCameraStatus(self, camera):
        # subscribe connection status notify
        eventSubscribe = pointer(GENICAM_EventSubscribe())
        eventSubscribeInfo = GENICAM_EventSubscribeInfo()
        eventSubscribeInfo.pCamera = pointer(camera)
        self.nRet = GENICAM_createEventSubscribe(
            byref(eventSubscribeInfo), byref(eventSubscribe))
        if (self.nRet != 0):
            print("create eventSubscribe fail!")
            return -1

        self.nRet = eventSubscribe.contents.subscribeConnectArgsEx(
            eventSubscribe, connectCallBackFuncEx, g_cameraStatusUserInfo)
        if (self.nRet != 0):
            print("subscribeConnectArgsEx fail!")
            # release subscribe resource before return
            eventSubscribe.contents.release(eventSubscribe)
            return -1

        # release subscribe resource at the end of use
        eventSubscribe.contents.release(eventSubscribe)
        return 0

    # unsubscribe camera connection status change
    def unsubscribeCameraStatus(self, camera):
        # unsubscribe connection status notify
        eventSubscribe = pointer(GENICAM_EventSubscribe())
        eventSubscribeInfo = GENICAM_EventSubscribeInfo()
        eventSubscribeInfo.pCamera = pointer(camera)
        self.nRet = GENICAM_createEventSubscribe(
            byref(eventSubscribeInfo), byref(eventSubscribe))
        if (self.nRet != 0):
            print("create eventSubscribe fail!")
            return -1

        self.nRet = eventSubscribe.contents.unsubscribeConnectArgsEx(
            eventSubscribe, connectCallBackFuncEx, g_cameraStatusUserInfo)
        if (self.nRet != 0):
            print("unsubscribeConnectArgsEx fail!")
            # release subscribe resource before return
            eventSubscribe.contents.release(eventSubscribe)
            return -1

        # release subscribe resource at the end of use
        eventSubscribe.contents.release(eventSubscribe)
        return 0

    # set software trigger
    def setSoftTriggerConf(self, camera):
        # create AcquisitionControl node
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        self.nRet = GENICAM_createAcquisitionControl(
            pointer(acqCtrlInfo), byref(acqCtrl))
        if (self.nRet != 0):
            print("create AcquisitionControl fail!")
            return -1

        # set trigger source to Software
        trigSourceEnumNode = acqCtrl.contents.triggerSource(acqCtrl)
        self.nRet = trigSourceEnumNode.setValueBySymbol(
            byref(trigSourceEnumNode), b"Software")
        if (self.nRet != 0):
            print("set TriggerSource value [Software] fail!")
            # release node resource before return
            trigSourceEnumNode.release(byref(trigSourceEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        trigSourceEnumNode.release(byref(trigSourceEnumNode))

        # set trigger selector to FrameStart
        trigSelectorEnumNode = acqCtrl.contents.triggerSelector(acqCtrl)
        self.nRet = trigSelectorEnumNode.setValueBySymbol(
            byref(trigSelectorEnumNode), b"FrameStart")
        if (self.nRet != 0):
            print("set TriggerSelector value [FrameStart] fail!")
            # release node resource before return
            trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        trigSelectorEnumNode.release(byref(trigSelectorEnumNode))

        # set trigger mode to On
        self.trigModeEnumNode = acqCtrl.contents.triggerMode(acqCtrl)
        self.nRet = self.trigModeEnumNode.setValueBySymbol(
            byref(self.trigModeEnumNode), b"On")
        if (self.nRet != 0):
            print("set TriggerMode value [On] fail!")
            # release node resource before return
            self.trigModeEnumNode.release(byref(self.trigModeEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        self.trigModeEnumNode.release(byref(self.trigModeEnumNode))
        acqCtrl.contents.release(acqCtrl)

        return 0

    # set external trigger
    def setLineTriggerConf(self, camera):
        # create AcquisitionControl node
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        self.nRet = GENICAM_createAcquisitionControl(
            pointer(acqCtrlInfo), byref(acqCtrl))
        if (self.nRet != 0):
            print("create AcquisitionControl fail!")
            return -1

        # set trigger source to Line1
        trigSourceEnumNode = acqCtrl.contents.triggerSource(acqCtrl)
        self.nRet = trigSourceEnumNode.setValueBySymbol(
            byref(trigSourceEnumNode), b"Line1")
        if (self.nRet != 0):
            print("set TriggerSource value [Line1] fail!")
            # release node resource before return
            trigSourceEnumNode.release(byref(trigSourceEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        trigSourceEnumNode.release(byref(trigSourceEnumNode))

        # set trigger selector to FrameStart
        trigSelectorEnumNode = acqCtrl.contents.triggerSelector(acqCtrl)
        self.nRet = trigSelectorEnumNode.setValueBySymbol(
            byref(trigSelectorEnumNode), b"FrameStart")
        if (self.nRet != 0):
            print("set TriggerSelector value [FrameStart] fail!")
            # release node resource before return
            trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        trigSelectorEnumNode.release(byref(trigSelectorEnumNode))

        # set trigger mode to On
        self.trigModeEnumNode = acqCtrl.contents.triggerMode(acqCtrl)
        self.nRet = self.trigModeEnumNode.setValueBySymbol(
            byref(self.trigModeEnumNode), b"On")
        if (self.nRet != 0):
            print("set TriggerMode value [On] fail!")
            # release node resource before return
            self.trigModeEnumNode.release(byref(self.trigModeEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        self.trigModeEnumNode.release(byref(self.trigModeEnumNode))

        # set trigger activation to RisingEdge
        trigActivationEnumNode = acqCtrl.contents.triggerActivation(acqCtrl)
        self.nRet = trigActivationEnumNode.setValueBySymbol(
            byref(trigActivationEnumNode), b"RisingEdge")
        if (self.nRet != 0):
            print("set TriggerActivation value [RisingEdge] fail!")
            # release node resource before return
            trigActivationEnumNode.release(byref(trigActivationEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        trigActivationEnumNode.release(byref(trigActivationEnumNode))
        acqCtrl.contents.release(acqCtrl)
        return 0

    # open camera
    def _openCamera(self, camera):
        # connect camera
        self.nRet = camera.connect(camera, c_int(
            GENICAM_ECameraAccessPermission.accessPermissionControl))
        if (self.nRet != 0):
            print("camera connect fail!")
            return -1
        else:
            print("camera connect success.")

        # subscribe camera connection status change
        self.nRet = self.subscribeCameraStatus(camera)
        if (self.nRet != 0):
            print("subscribeCameraStatus fail!")
            return -1

        return 0

    # close camera
    def closeCamera(self):
        # unsubscribe camera connection status change
        self.nRet = self.unsubscribeCameraStatus(self.camera)
        if (self.nRet != 0):
            print("unsubscribeCameraStatus fail!")
            return -1

        # disconnect camera
        self.nRet = self.camera.disConnect(byref(self.camera))
        if (self.nRet != 0):
            print("disConnect camera fail!")
            return -1

        return 0

    # set camera ExposureTime
    def setExposureTime(self, dVal):
        # create corresponding property node according to the value type of property, here is doubleNode
        exposureTimeNode = pointer(GENICAM_DoubleNode())
        exposureTimeNodeInfo = GENICAM_DoubleNodeInfo()
        exposureTimeNodeInfo.pCamera = pointer(self.camera)
        exposureTimeNodeInfo.attrName = b"ExposureTime"
        self.nRet = GENICAM_createDoubleNode(
            byref(exposureTimeNodeInfo), byref(exposureTimeNode))
        if (self.nRet != 0):
            print("create ExposureTime Node fail!")
            return -1

        # set ExposureTime
        self.nRet = exposureTimeNode.contents.setValue(
            exposureTimeNode, c_double(dVal))
        if (self.nRet != 0):
            print("set ExposureTime value [%f]us fail!" % (dVal))
            # release node resource before return
            exposureTimeNode.contents.release(exposureTimeNode)
            return -1
        else:
            print("set ExposureTime value [%f]us success." % (dVal))

        # release node resource at the end of use
        exposureTimeNode.contents.release(exposureTimeNode)
        return 0

    def setBrightness(self, dVal):
        # create corresponding property node according to the value type of property, here is doubleNode
        brightnessNode = pointer(GENICAM_IntNode())
        brightnessNodeInfo = GENICAM_IntNodeInfo()
        brightnessNodeInfo.pCamera = pointer(self.camera)
        brightnessNodeInfo.attrName = b"Brightness"
        self.nRet = GENICAM_createIntNode(
            byref(brightnessNodeInfo), byref(brightnessNode))
        if (self.nRet != 0):
            print("create brightness Node fail!")
            return -1

        # set brightness
        self.nRet = brightnessNode.contents.setValue(
            brightnessNode, c_longlong(dVal))
        if (self.nRet != 0):
            print("set brightness value [%f]us fail!" % (dVal))
            # release node resource before return
            brightnessNode.contents.release(brightnessNode)
            return -1
        else:
            print("set brightness value [%f]us success." % (dVal))

        # release node resource at the end of use
        brightnessNode.contents.release(brightnessNode)
        return 0

    # set exposure mode
    def setExposureAuto(self, mode="Off"):
        # create AcquisitionControl node
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(self.camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        self.nRet = GENICAM_createAcquisitionControl(
            pointer(acqCtrlInfo), byref(acqCtrl))
        if (self.nRet != 0):
            print("create AcquisitionControl fail!")
            return -1

        # set ExposureAuto
        exposureAutoEnumNode = acqCtrl.contents.exposureAuto(acqCtrl)
        self.nRet = exposureAutoEnumNode.setValueBySymbol(
            byref(exposureAutoEnumNode), bytes(mode, 'utf-8'))
        if (self.nRet != 0):
            print("set TriggerSource value [Software] fail!")
            # release node resource before return
            exposureAutoEnumNode.release(byref(exposureAutoEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        return 0

    # set white balance mode
    def setWBAuto(self, mode="Off"):
        # create AcquisitionControl node
        acqCtrlInfo = GENICAM_AnalogControlInfo()
        acqCtrlInfo.pCamera = pointer(self.camera)
        acqCtrl = pointer(GENICAM_AnalogControl())
        self.nRet = GENICAM_createAnalogControl(
            pointer(acqCtrlInfo), byref(acqCtrl))
        if (self.nRet != 0):
            print("create AnalogControl fail!")
            return -1

        # set ExposureAuto
        balanceWhiteAutoEnumNode = acqCtrl.contents.balanceWhiteAuto(acqCtrl)
        self.nRet = balanceWhiteAutoEnumNode.setValueBySymbol(
            byref(balanceWhiteAutoEnumNode), bytes(mode, 'utf-8'))
        if (self.nRet != 0):
            print("set TriggerSource value [Software] fail!")
            # release node resource before return
            balanceWhiteAutoEnumNode.release(byref(balanceWhiteAutoEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        return 0

    # set white balance ratio
    def setWBRatio(self, channel, dVal):
        # create AcquisitionControl node
        anlgctrlInfo = GENICAM_AnalogControlInfo()
        anlgctrlInfo.pCamera = pointer(self.camera)
        anlgctrl = pointer(GENICAM_AnalogControl())
        self.nRet = GENICAM_createAnalogControl(
            pointer(anlgctrlInfo), byref(anlgctrl))
        if (self.nRet != 0):
            print("create AcquisitionControl fail!")
            return -1

        # set trigger selector to FrameStart
        balSelectorEnumNode = anlgctrl.contents.balanceRatioSelector(anlgctrl)
        self.nRet = balSelectorEnumNode.setValueBySymbol(
            byref(balSelectorEnumNode), bytes(channel, 'utf-8'))
        if (self.nRet != 0):
            print("set TriggerSelector value [FrameStart] fail!")
            # release node resource before return
            balSelectorEnumNode.release(byref(balSelectorEnumNode))
            anlgctrl.contents.release(anlgctrl)
            return -1

        # release node resource at the end of use
        balSelectorEnumNode.release(byref(balSelectorEnumNode))

        # # create corresponding property node according to the value type of property, here is doubleNode
        balRatioNode = pointer(GENICAM_DoubleNode())
        balRatioNodeInfo = GENICAM_DoubleNodeInfo()
        balRatioNodeInfo.pCamera = pointer(self.camera)
        balRatioNodeInfo.attrName = b"BalanceRatio"
        self.nRet = GENICAM_createDoubleNode(
            byref(balRatioNodeInfo), byref(balRatioNode))
        if (self.nRet != 0):
            print("create balRatio Node fail!")
            return -1

        # set balRatio
        self.nRet = balRatioNode.contents.setValue(
            balRatioNode, c_double(dVal))
        if (self.nRet != 0):
            print("set balRatio value [%f]us fail!" % (dVal))
            # release node resource before return
            balRatioNode.contents.release(balRatioNode)
            return -1
        else:
            print("set balRatio value [%f]us success." % (dVal))

        # release node resource at the end of use
        balRatioNode.contents.release(balRatioNode)

        anlgctrl.contents.release(anlgctrl)

        return 0
    # enumerate camera

    def enumCameras(self):
        # get system instance
        system = pointer(GENICAM_System())
        self.nRet = GENICAM_getSystemInstance(byref(system))
        if (self.nRet != 0):
            print("getSystemInstance fail!")
            return None, None

        # discover camera
        cameraList = pointer(GENICAM_Camera())
        cameraCnt = c_uint()
        self.nRet = system.contents.discovery(system, byref(cameraList), byref(
            cameraCnt), c_int(GENICAM_EProtocolType.typeAll))
        if (self.nRet != 0):
            print("discovery fail!")
            return None, None
        elif cameraCnt.value < 1:
            print("discovery no camera!")
            return None, None
        else:
            print("cameraCnt: " + str(cameraCnt.value))
            return cameraCnt.value, cameraList

    def grabOne(self, camera):
        # create stream source object
        self.streamSourceInfo = GENICAM_StreamSourceInfo()
        self.streamSourceInfo.channelId = 0
        self.streamSourceInfo.pCamera = pointer(camera)

        self.streamSource = pointer(GENICAM_StreamSource())
        self.nRet = GENICAM_createStreamSource(
            pointer(self.streamSourceInfo), byref(self.streamSource))
        if (self.nRet != 0):
            print("create self.streamSource fail!")
            return -1

        # create AcquisitionControl node
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        self.nRet = GENICAM_createAcquisitionControl(
            pointer(acqCtrlInfo), byref(acqCtrl))
        if (self.nRet != 0):
            print("create AcquisitionControl fail!")
            # release stream source object before return
            self.streamSource.contents.release(self.streamSource)
            return -1

        # execute software trigger once
        trigSoftwareCmdNode = acqCtrl.contents.triggerSoftware(acqCtrl)
        self.nRet = trigSoftwareCmdNode.execute(byref(trigSoftwareCmdNode))
        if (self.nRet != 0):
            print("Execute triggerSoftware fail!")
            # release node resource before return
            trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
            acqCtrl.contents.release(acqCtrl)
            self.streamSource.contents.release(self.streamSource)
            return -1

        # release node resource at the end of use
        trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
        acqCtrl.contents.release(acqCtrl)
        self.streamSource.contents.release(self.streamSource)

        return 0

    # set ROI ---Height, width, offsetX, offsetY. Input value shall comply with the step length and Max & Min limits.
    def setROI(self, camera, OffsetX, OffsetY, nWidth, nHeight):
        # get the max width of image
        widthMaxNode = pointer(GENICAM_IntNode())
        widthMaxNodeInfo = GENICAM_IntNodeInfo()
        widthMaxNodeInfo.pCamera = pointer(camera)
        widthMaxNodeInfo.attrName = b"WidthMax"
        self.nRet = GENICAM_createIntNode(
            byref(widthMaxNodeInfo), byref(widthMaxNode))
        if (self.nRet != 0):
            print("create WidthMax Node fail!")
            return -1

        oriWidth = c_longlong()
        self.nRet = widthMaxNode.contents.getValue(
            widthMaxNode, byref(oriWidth))
        if (self.nRet != 0):
            print("widthMaxNode getValue fail!")
            # release node resource before return
            widthMaxNode.contents.release(widthMaxNode)
            return -1

        # release node resource at the end of use
        widthMaxNode.contents.release(widthMaxNode)

        # get the max height of image
        heightMaxNode = pointer(GENICAM_IntNode())
        heightMaxNodeInfo = GENICAM_IntNodeInfo()
        heightMaxNodeInfo.pCamera = pointer(camera)
        heightMaxNodeInfo.attrName = b"HeightMax"
        self.nRet = GENICAM_createIntNode(
            byref(heightMaxNodeInfo), byref(heightMaxNode))
        if (self.nRet != 0):
            print("create HeightMax Node fail!")
            return -1

        oriHeight = c_longlong()
        self.nRet = heightMaxNode.contents.getValue(
            heightMaxNode, byref(oriHeight))
        if (self.nRet != 0):
            print("heightMaxNode getValue fail!")
            # release node resource before return
            heightMaxNode.contents.release(heightMaxNode)
            return -1

        # release node resource at the end of use
        heightMaxNode.contents.release(heightMaxNode)

        # check parameter valid
        if ((oriWidth.value < (OffsetX + nWidth)) or (oriHeight.value < (OffsetY + nHeight))):
            print("please check input param!")
            return -1

        # set image width
        widthNode = pointer(GENICAM_IntNode())
        widthNodeInfo = GENICAM_IntNodeInfo()
        widthNodeInfo.pCamera = pointer(camera)
        widthNodeInfo.attrName = b"Width"
        self.nRet = GENICAM_createIntNode(
            byref(widthNodeInfo), byref(widthNode))
        if (self.nRet != 0):
            print("create Width Node fail!")
            return -1

        self.nRet = widthNode.contents.setValue(widthNode, c_longlong(nWidth))
        if (self.nRet != 0):
            print("widthNode setValue [%d] fail!" % (nWidth))
            # release node resource before return
            widthNode.contents.release(widthNode)
            return -1

        # release node resource at the end of use
        widthNode.contents.release(widthNode)

        # set image height
        heightNode = pointer(GENICAM_IntNode())
        heightNodeInfo = GENICAM_IntNodeInfo()
        heightNodeInfo.pCamera = pointer(camera)
        heightNodeInfo.attrName = b"Height"
        self.nRet = GENICAM_createIntNode(
            byref(heightNodeInfo), byref(heightNode))
        if (self.nRet != 0):
            print("create Height Node fail!")
            return -1

        self.nRet = heightNode.contents.setValue(
            heightNode, c_longlong(nHeight))
        if (self.nRet != 0):
            print("heightNode setValue [%d] fail!" % (nHeight))
            # release node resource before return
            heightNode.contents.release(heightNode)
            return -1

        # release node resource at the end of use
        heightNode.contents.release(heightNode)

        # set OffsetX
        OffsetXNode = pointer(GENICAM_IntNode())
        OffsetXNodeInfo = GENICAM_IntNodeInfo()
        OffsetXNodeInfo.pCamera = pointer(camera)
        OffsetXNodeInfo.attrName = b"OffsetX"
        self.nRet = GENICAM_createIntNode(
            byref(OffsetXNodeInfo), byref(OffsetXNode))
        if (self.nRet != 0):
            print("create OffsetX Node fail!")
            return -1

        self.nRet = OffsetXNode.contents.setValue(
            OffsetXNode, c_longlong(OffsetX))
        if (self.nRet != 0):
            print("OffsetX setValue [%d] fail!" % (OffsetX))
            # release node resource before return
            OffsetXNode.contents.release(OffsetXNode)
            return -1

        # release node resource at the end of use
        OffsetXNode.contents.release(OffsetXNode)

        # set OffsetY
        OffsetYNode = pointer(GENICAM_IntNode())
        OffsetYNodeInfo = GENICAM_IntNodeInfo()
        OffsetYNodeInfo.pCamera = pointer(camera)
        OffsetYNodeInfo.attrName = b"OffsetY"
        self.nRet = GENICAM_createIntNode(
            byref(OffsetYNodeInfo), byref(OffsetYNode))
        if (self.nRet != 0):
            print("create OffsetY Node fail!")
            return -1

        self.nRet = OffsetYNode.contents.setValue(
            OffsetYNode, c_longlong(OffsetY))
        if (self.nRet != 0):
            print("OffsetY setValue [%d] fail!" % (OffsetY))
            # release node resource before return
            OffsetYNode.contents.release(OffsetYNode)
            return -1

        # release node resource at the end of use
        OffsetYNode.contents.release(OffsetYNode)
        return 0

    def getListCamera(self):
        # enumerate camera
        cameraCnt, cameraList = self.enumCameras()
        if cameraCnt is None:
            return -1

        # print camera info
        for index in range(0, cameraCnt):
            camera = cameraList[index]
            print("\nCamera Id = " + str(index))
            print("Key           = " + str(camera.getKey(camera)))
            print("vendor name   = " + str(camera.getVendorName(camera)))
            print("Model  name   = " + str(camera.getModelName(camera)))
            print("Serial number = " + str(camera.getSerialNumber(camera)))

        return cameraList

    def setCamera(self, cam):
        _, cameraList = self.enumCameras()
        self.camera = cameraList[cam]

    def openCamera(self):
        # open camera
        self.nRet = self._openCamera(self.camera)
        if (self.nRet != 0):
            print("openCamera fail.")
            return -1

        # create stream source object
        self.streamSourceInfo = GENICAM_StreamSourceInfo()
        self.streamSourceInfo.channelId = 0
        self.streamSourceInfo.pCamera = pointer(self.camera)

        self.streamSource = pointer(GENICAM_StreamSource())
        self.nRet = GENICAM_createStreamSource(
            pointer(self.streamSourceInfo), byref(self.streamSource))
        if (self.nRet != 0):
            print("create self.streamSource fail!")
            return -1

        self.trigModeEnumNode = pointer(GENICAM_EnumNode())
        self.trigModeEnumNodeInfo = GENICAM_EnumNodeInfo()
        self.trigModeEnumNodeInfo.pCamera = pointer(self.camera)
        self.trigModeEnumNodeInfo.attrName = b"TriggerMode"
        self.nRet = GENICAM_createEnumNode(
            byref(self.trigModeEnumNodeInfo), byref(self.trigModeEnumNode))
        if (self.nRet != 0):
            print("create TriggerMode Node fail!")
            # release node resource before return
            self.streamSource.contents.release(self.streamSource)
            return -1

        self.nRet = self.trigModeEnumNode.contents.setValueBySymbol(
            self.trigModeEnumNode, b"Off")
        if (self.nRet != 0):
            print("set TriggerMode value [Off] fail!")
            # release node resource before return
            self.trigModeEnumNode.contents.release(self.trigModeEnumNode)
            self.streamSource.contents.release(self.streamSource)
            return -1

        # release node resource at the end of use
        self.trigModeEnumNode.contents.release(self.trigModeEnumNode)

        # start grabbing
        self.nRet = self.streamSource.contents.startGrabbing(self.streamSource, c_ulonglong(0),
                                                             c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
        if (self.nRet != 0):
            print("startGrabbing fail!")
            # release stream source object before return
            self.streamSource.contents.release(self.streamSource)
            return -1

    def setGainRaw(self, dval):
        self.setDoubleNode('GainRaw', dval)

    def setGamma(self, dval):
        self.setDoubleNode('Gamma', dval)

    def setDigitalShift(self, dval):
        # self.setDoubleNode('Gamma', dval)
        None

    def setSharpness(self, dval):
        self.setIntNode('Sharpness', dval)

    # set camera ExposureTime
    def setDoubleNode(self, attr, dVal):
        # create corresponding property node according to the value type of property, here is doubleNode
        doubleNode = pointer(GENICAM_DoubleNode())
        doubleNodeInfo = GENICAM_DoubleNodeInfo()
        doubleNodeInfo.pCamera = pointer(self.camera)
        doubleNodeInfo.attrName = bytes(attr, 'utf-8')
        self.nRet = GENICAM_createDoubleNode(
            byref(doubleNodeInfo), byref(doubleNode))
        if (self.nRet != 0):
            print("create " + attr + " Node fail!")
            return -1

        # set double
        self.nRet = doubleNode.contents.setValue(doubleNode, c_double(dVal))
        if (self.nRet != 0):
            print("set double value [%f]us fail!" % (dVal))
            # release node resource before return
            doubleNode.contents.release(doubleNode)
            return -1
        else:
            print("set double value [%f]us success." % (dVal))

        # release node resource at the end of use
        doubleNode.contents.release(doubleNode)
        return 0

    def setIntNode(self, attr, dVal):
        # create corresponding property node according to the value type of property, here is doubleNode
        intNode = pointer(GENICAM_IntNode())
        intNodeInfo = GENICAM_IntNodeInfo()
        intNodeInfo.pCamera = pointer(self.camera)
        intNodeInfo.attrName = bytes(attr, 'utf-8')
        self.nRet = GENICAM_createIntNode(byref(intNodeInfo), byref(intNode))
        if (self.nRet != 0):
            print("create int "+attr+" fail!")
            return -1

        # set int
        self.nRet = intNode.contents.setValue(intNode, c_longlong(dVal))
        if (self.nRet != 0):
            print("set int value [%f]us fail!" % (dVal))
            # release node resource before return
            intNode.contents.release(intNode)
            return -1
        else:
            print("set int value [%f]us success." % (dVal))

        # release node resource at the end of use
        intNode.contents.release(intNode)
        return 0

    def setSharpnessEnable(self, mode="Off"):
        # create AcquisitionControl node
        acqCtrlInfo = GENICAM_ISPControlInfo()
        acqCtrlInfo.pCamera = pointer(self.camera)
        acqCtrl = pointer(GENICAM_ISPControl())
        self.nRet = GENICAM_createISPControl(
            pointer(acqCtrlInfo), byref(acqCtrl))
        if (self.nRet != 0):
            print("create ISPControl fail!")
            return -1

        # set ExposureAuto
        sharpnessEnableEnumNode = acqCtrl.contents.sharpnessEnable(acqCtrl)
        self.nRet = sharpnessEnableEnumNode.setValueBySymbol(
            byref(sharpnessEnableEnumNode), bytes(mode, 'utf-8'))
        if (self.nRet != 0):
            print("set TriggerSource value [Software] fail!")
            # release node resource before return
            sharpnessEnableEnumNode.release(byref(sharpnessEnableEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1

        # release node resource at the end of use
        return 0

    def stream(self):
            frame = pointer(GENICAM_Frame())
            nRet = self.streamSource.contents.getFrame(
                self.streamSource, byref(frame), c_uint(1000))
            if (nRet != 0):
                print("getFrame fail! Timeout:[1000]ms")
                # release stream source object before return
                self.streamSource.contents.release(self.streamSource)
                return -1
            # else:
            #         print("getFrame success BlockId = [" + str(frame.contents.getBlockId(frame)) + "], get frame time: " + str(datetime.datetime.now()))

            self.nRet = frame.contents.valid(frame)
            if (self.nRet != 0):
                print("frame is invalid!")
                # release frame resource before return
                frame.contents.release(frame)
                # release stream source object before return
                self.streamSource.contents.release(self.streamSource)
                return -1

            # fill conversion parameter
            imageParams = IMGCNV_SOpenParam()
            imageParams.dataSize = frame.contents.getImageSize(frame)
            imageParams.height = frame.contents.getImageHeight(frame)
            imageParams.width = frame.contents.getImageWidth(frame)
            imageParams.paddingX = frame.contents.getImagePaddingX(frame)
            imageParams.paddingY = frame.contents.getImagePaddingY(frame)
            imageParams.pixelForamt = frame.contents.getImagePixelFormat(frame)

            # copy image data out from frame
            imageBuff = frame.contents.getImage(frame)
            userBuff = c_buffer(b'\0', imageParams.dataSize)
            memmove(userBuff, c_char_p(imageBuff), imageParams.dataSize)

            # release frame resource at the end of use
            frame.contents.release(frame)

            # no format conversion required for Mono8
            if imageParams.pixelForamt == EPixelType.gvspPixelMono8:
                grayByteArray = bytearray(userBuff)
                cvImage = numpy.array(grayByteArray).reshape(
                    imageParams.height, imageParams.width)
            else:
                # convert to BGR24
                rgbSize = c_int()
                rgbBuff = c_buffer(b'\0', imageParams.height *
                                imageParams.width * 3)

                nRet = IMGCNV_ConvertToBGR24(cast(userBuff, c_void_p),
                                            byref(imageParams),
                                            cast(rgbBuff, c_void_p),
                                            byref(rgbSize))

                colorByteArray = bytearray(rgbBuff)
                cvImage = numpy.array(colorByteArray).reshape(
                    imageParams.height, imageParams.width, 3)
        # --- end if ---

            # cv2.imshow('myWindow', cvImage)
            gc.collect()
            return cvImage


    def stopGrabing(self):
        self.nRet = self.streamSource.contents.stopGrabbing(self.streamSource)
        if (self.nRet != 0):
            print("stopGrabbing fail!")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)
            return -1
        self.nRet = self.closeCamera(self.camera)
        if (self.nRet != 0):
            print("closeCamera fail")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)
            return -1

        # release stream source object at the end of use
        self.streamSource.contents.release(self.streamSource)
    
