import cv2 as cv
import csv
import datetime
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QSizePolicy, QHBoxLayout, QLabel, QInputDialog
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, Qt, QImage, QFontMetrics
from PySide6.QtCore import Signal, QPoint
from Utils.ThreadUtility import RegisterThread, CaptureThread, CheckThread


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('AttendanceCheck')
        self.setFixedSize(800, 600)

        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)


class CentralWidget(QWidget):

    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent)

        self.__status = False  # 摄像头开关状态

        self.v_layout = QVBoxLayout()
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont('Consolas', 12)
        self.label.setFont(font)
        self.v_layout.addWidget(self.label)

        self.back_btn = QPushButton(self)
        self.back_btn.setText('< Back')
        self.back_btn.clicked.connect(self.__on_back_btn_clicked)
        self.v_layout.addWidget(self.back_btn)

        self.camera_panel = CameraPanel(self)
        self.camera_panel.tips_updated.connect(self.on_tips_updated)
        self.camera_panel.mode_changed.connect(self.on_mode_changed)
        self.v_layout.addWidget(self.camera_panel)

        self.h_layout = QHBoxLayout()

        self.register_btn = QPushButton(self)
        self.register_btn.setText('Register')
        self.register_btn.clicked.connect(self.__on_register_btn_clicked)
        self.h_layout.addWidget(self.register_btn)

        self.check_btn = QPushButton(self)
        self.check_btn.setText('Check')
        self.check_btn.clicked.connect(self.__on_check_btn_clicked)
        self.h_layout.addWidget(self.check_btn)

        self.v_layout.addLayout(self.h_layout)

        self.camera_btn = QPushButton(self)
        self.camera_btn.setText('Open Camera')
        self.camera_btn.clicked.connect(self.on_cam_btn_clicked)
        self.v_layout.addWidget(self.camera_btn)

        self.setLayout(self.v_layout)

    '''
    :brief 处理摄像头按钮点击事件
    '''
    def on_cam_btn_clicked(self):
        self.__status = ~self.__status

        self.camera_panel.set_camera(self.__status)
        if self.__status:
            self.camera_btn.setText('Close Camera')
            self.label.setText('Camera opened')
        else:
            self.camera_btn.setText('Open Camera')
            self.label.setText('Camera closed')

    '''
    :brief 处理注册模式按钮点击事件
    '''
    def __on_register_btn_clicked(self):
        state = self.camera_panel.get_camera_state()
        if state:
            self.on_mode_changed(1)
            self.camera_panel.set_mode(1)
            self.label.setText('Register mode enabled')
        else:
            self.on_tips_updated('Please open the camera')

    '''
    :brief 处理返回按钮点击事件
    '''
    def __on_back_btn_clicked(self):
        self.on_mode_changed(0)
        self.camera_panel.set_mode(0)
        self.label.setText('Running on normal mode')

    '''
    :brief 处理打卡模式按钮点击事件
    '''
    def __on_check_btn_clicked(self):
        state = self.camera_panel.get_camera_state()
        if state:
            self.on_mode_changed(2)
            self.camera_panel.set_mode(2)
            self.label.setText('Check mode enabled')
        else:
            self.on_tips_updated('Please open the camera')

    '''
    :brief 处理模式切换事件
    :param mode 模式
    '''
    def on_mode_changed(self, mode):
        if mode == 0:
            self.register_btn.setEnabled(True)
            self.check_btn.setEnabled(True)
        elif mode == 1:
            self.register_btn.setEnabled(True)
            self.check_btn.setEnabled(False)
        elif mode == 2:
            self.register_btn.setEnabled(False)
            self.check_btn.setEnabled(True)

    '''
    :brief 处理系统提示更新事件
    :param text 系统提示文字
    '''
    def on_tips_updated(self, text):
        self.label.setText(text)


class CameraPanel(QWidget):

    tips_updated = Signal(str)  # 系统提示更新信号
    mode_changed = Signal(int)  # 摄像头模式改变信号

    def __init__(self, parent=None):
        super(CameraPanel, self).__init__(parent)

        self.__img = None
        self.__camera_opened = False
        self.__camera_mode = 0  # 摄像头模式 0：默认模式 1：注册模式 2：打卡模式
        self.__capture_thread = CaptureThread()
        self.__register_thread = RegisterThread()
        self.__check_thread = CheckThread()
        self.__painter = QPainter()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(400, 400)

        self.__capture_thread.frame_captured.connect(self.__on_frame_captured)
        self.__capture_thread.frame_captured.connect(self.__register_thread.set_img)
        self.__capture_thread.frame_captured.connect(self.__check_thread.set_img)
        self.__register_thread.reg_state_changed.connect(self.__on_reg_state_changed)
        self.__register_thread.face_recognized.connect(self.__on_face_recognized)
        self.__check_thread.face_checked.connect(self.__on_face_checked)

        self.__painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)

    def paintEvent(self, event):
        pen = QPen(Qt.PenStyle.NoPen)
        self.__painter.setPen(pen)
        brush = QBrush(Qt.BrushStyle.NoBrush)
        self.__painter.setBrush(brush)

        self.__painter.begin(self)

        # 绘制摄像头框内容
        if self.__camera_opened and self.__img is not None:
            self.__painter.drawImage(0, 0, self.__img)
        else:
            font = QFont('微软雅黑', 10, 1)
            self.__painter.setFont(font)
            pen.setStyle(Qt.PenStyle.SolidLine)
            pen.setColor(Qt.GlobalColor.black)
            pen.setWidth(1)
            self.__painter.setPen(pen)
            s = 'Camera Closed'
            font_matrix = QFontMetrics(font)
            str_width = font_matrix.horizontalAdvance(s)
            str_height = font_matrix.height()
            self.__painter.drawText(int((self.width() - str_width) / 2), int((self.height() - str_height) / 2), s)

        # 绘制人脸对准框
        if self.__camera_mode == 1:
            mask = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
            mask_painter = QPainter(mask)

            mask_painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.NonCosmeticBrushPatterns)
            pen.setStyle(Qt.PenStyle.NoPen)
            mask_painter.setPen(pen)
            brush.setStyle(Qt.BrushStyle.SolidPattern)
            brush.setColor(QColor(127, 127, 127))
            mask_painter.setBrush(brush)

            mask_painter.begin(mask)

            mask_painter.drawRect(self.rect())
            brush.setColor(QColor(255, 255, 255))
            mask_painter.setBrush(brush)
            mask_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOut)
            mask_painter.drawEllipse(QPoint(int(self.width() / 2), int(self.height() / 2)), 200, 200)

            mask_painter.end()

            self.__painter.drawImage(0, 0, mask)

        # 绘制边框
        self.__painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

        self.__painter.end()

    '''
    :brief 设置摄像头状态
    :param state 摄像头状态
    '''
    def set_camera(self, state):
        self.__camera_opened = state

        if self.__camera_opened:
            self.__capture_thread.start()
        else:
            self.__capture_thread.stop_immediately()
            self.update()

    '''
    :brief 设置模式
    :param mode 模式
    '''
    def set_mode(self, mode):
        if mode == 0:
            if self.__camera_mode == 1:
                self.__register_thread.stop_immediately()
            elif self.__camera_mode == 2:
                self.__check_thread.stop_immediately()
            self.__camera_mode = mode
            self.tips_updated.emit('')
        elif self.__camera_opened:
            if mode == 1 and not self.__register_thread.isRunning():
                self.__register_thread.start()
            elif mode == 2 and not self.__check_thread.isRunning():
                self.__check_thread.start()
            self.__camera_mode = mode

    '''
    :brief 获取摄像头状态
    :return 返回摄像头状态
    '''
    def get_camera_state(self):
        return self.__camera_opened

    '''
    :brief 处理人脸登记成功事件，将人脸保存至本地
    :param des 人脸标识符
    '''
    def __on_face_recognized(self, des):
        name, ok = QInputDialog.getText(self, 'Please enter your name', 'Name: ')
        if name and ok:
            with open('./data/face_database.csv', 'a+', newline='') as f:
                csv_reader = csv.reader(f)
                num_list = set()
                uid = 1
                for line in csv_reader:
                    num_list.add(int(line[0]))
                num_list = sorted(num_list)
                for i in num_list:
                    if i != uid:
                        break
                    uid += 1

                csv_writer = csv.writer(f)
                csv_format = [uid, name, des]
                csv_writer.writerow(csv_format)
                self.tips_updated.emit('id: ' + str(uid) + ' name: ' + name + ' registered')
                self.__camera_mode = 0
                self.mode_changed.emit(0)
                f.close()

    '''
    :brief 处理人脸对比成功事件，登记用户打卡信息
    :param info 用户信息
    '''
    def __on_face_checked(self, info):
        with open('./data/check_log.csv', 'a', newline='') as f:
            csv_writer = csv.writer(f)
            csv_format = [info[0], info[1], datetime.datetime.now()]
            csv_writer.writerow(csv_format)
            f.close()
        self.tips_updated.emit('id: ' + str(info[0]) + ' name: ' + str(info[1]) + ' checked')

    '''
    :brief 处理人脸注册状态事件
    :param ret 注册状态事件号
    '''
    def __on_reg_state_changed(self, ret):
        if ret == 0:
            self.tips_updated.emit('No face')
        elif ret == 1:
            self.tips_updated.emit('Face recognised successfully')
        elif ret == 2:
            self.tips_updated.emit('Multiple faces')
        elif ret == 3:
            self.tips_updated.emit('Please place your face within the circle')

    '''
    :brief 获取并处理图像帧
    :param frame 原始帧
    '''
    def __on_frame_captured(self, frame):
        row, col, channel = frame.shape
        bytes_per_line = channel * col
        cv.cvtColor(frame, cv.COLOR_BGR2RGB, frame)
        self.__img = QImage(frame.data, col, row, bytes_per_line, QImage.Format.Format_RGB888).copy(int((col - row) / 2), 0, row, row)

        self.update()
