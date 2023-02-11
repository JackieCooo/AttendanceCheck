import cv2 as cv
import numpy
import math
from PySide6.QtCore import QThread, Signal, QMutex
from Utils.FaceUtility import FaceRecognition


class CaptureThread(QThread):

    frame_captured = Signal(numpy.ndarray)  # 帧捕捉完成信号，返回对应帧

    def __init__(self):
        super(CaptureThread, self).__init__()

        self.__camera = None
        self.__mutex = QMutex()
        self.__runnable = False

    def __del__(self):
        if self.__camera is not None:
            self.__camera.release()

    def run(self):
        self.__camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.__runnable = True
        while True:
            ret, frame = self.__camera.read()
            if ret:
                self.frame_captured.emit(frame)
            self.__mutex.unlock()
            if not self.__runnable:
                if self.__camera is not None:
                    self.__camera.release()
                return
            self.msleep(40)  # 25fps

    def stop_immediately(self):
        self.__mutex.lock()
        self.__runnable = False


class RegisterThread(QThread):

    reg_state_changed = Signal(int)  # 注册检测状态信号，0：无人脸 1：有一个人脸且人脸在框内 2：有多个人脸 3：有一个人脸但不在框内
    face_recognized = Signal(list)  # 人脸识别成功信号

    def __init__(self):
        super(RegisterThread, self).__init__()

        self.__mutex = QMutex()
        self.__runnable = False
        self.__face_recognition = FaceRecognition()
        self.__img = None

    def stop_immediately(self):
        self.__mutex.lock()
        self.__runnable = False

    '''
    :brief 设置图像
    :param img 图像
    '''
    def set_img(self, img):
        self.__img = img

    def run(self):
        self.__runnable = True
        while True:
            if self.__img is not None:
                status = -1

                # 识别人脸
                ret, rect, ps, des = self.__face_recognition.recognise(self.__img)
                # print(type(des))
                if ret == 0:  # 没有人脸
                    status = 0
                elif ret == 1:  # 有一个人脸
                    fixed_x1, fixed_y1 = self.__translate_coordinate(rect[0], rect[1])
                    fixed_x2, fixed_y2 = self.__translate_coordinate(rect[2], rect[3])
                    if self.__is_in_circle(fixed_x1, fixed_y1, fixed_x2, fixed_y2):  # 在框内
                        status = 1
                    else:  # 不在框内
                        status = 3
                elif ret == 2:  # 有多个人脸
                    status = 2
                self.reg_state_changed.emit(status)  # 发送注册检测状态

                # 注册人脸
                if status == 1:
                    self.face_recognized.emit(des)
                    self.__runnable = False

            self.__mutex.unlock()
            if not self.__runnable:
                return
            self.msleep(500)

    '''
    :brief 检测人脸是否在对准框中
    :param x1 左上点x坐标
    :param y1 左上点y坐标
    :param x2 右下点x坐标
    :param y2 右下点y坐标
    :return 返回是否在对准框中
    '''
    @staticmethod
    def __is_in_circle(x1, y1, x2, y2):
        p1_len = math.sqrt((x1 - 200) ** 2 + (y1 - 200) ** 2)
        p2_len = math.sqrt((x2 - 200) ** 2 + (y2 - 200) ** 2)
        return p1_len <= 200 and p2_len <= 200

    '''
    :brief 转换原图坐标至显示框坐标
    :param x x坐标
    :param y y坐标
    :return 返回转换后的坐标
    '''
    def __translate_coordinate(self, x, y):
        row, col, channel = self.__img.shape
        offset = int((col - row) / 2)
        return x - offset, y


class CheckThread(QThread):

    face_checked = Signal(tuple)  # 打卡完成信号

    def __init__(self):
        super(CheckThread, self).__init__()

        self.__mutex = QMutex()
        self.__runnable = False
        self.__face_recognition = FaceRecognition()
        self.__img = None

    def stop_immediately(self):
        self.__mutex.lock()
        self.__runnable = False

    '''
    :brief 设置图像
    :param img 图像
    '''
    def set_img(self, img):
        self.__img = img

    def run(self):
        self.__runnable = True
        while True:
            if self.__img is not None:
                ret, r, ps, des = self.__face_recognition.recognise(self.__img)
                if ret == 1:
                    res, uid, uname = self.__face_recognition.check(des)
                    print('res:', res, 'uid:', uid, 'uname:', uname)
                    if res == 1:
                        self.face_checked.emit((uid, uname))
                        self.sleep(2)

            self.__mutex.unlock()
            if not self.__runnable:
                return
            self.msleep(500)
