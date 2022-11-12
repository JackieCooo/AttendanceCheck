import dlib
import cv2 as cv
import csv
import numpy as np


class FaceRecognition:

    def __init__(self):
        self.__face_detector = dlib.get_frontal_face_detector()
        self.__shape_detector = dlib.shape_predictor('./models/shape_predictor_68_face_landmarks.dat')
        self.__face_model = dlib.face_recognition_model_v1('./models/dlib_face_recognition_resnet_model_v1.dat')
        self.__csv_filepath = './data/face_database.csv'
        self.__threshold = 0.5  # 人脸对比的阈值

    '''
    :brief 人脸识别，获取特征点
    :param img 采集的图像
    :return ret 分析结果，0：无人脸，1：有一个人脸，2：有多个人脸
    :return rect 人脸框范围
    :return points 人脸特征点
    :return descriptor 人脸特征描述符
    '''
    def recognise(self, img):
        detection = self.__face_detector(img, 1)
        if len(detection) == 0:
            return 0, None, None, None
        if len(detection) > 1:
            return 2, None, None, None
        descriptor = None
        rect = None
        points = None
        for face in detection:
            left, top, right, bottom = face.left(), face.top(), face.right(), face.bottom()
            rect = [left, top, right, bottom]
            points = self.__shape_detector(img, face)
            descriptor = self.__face_model.compute_face_descriptor(img, points)
            descriptor = [f for f in descriptor]
        return 1, rect, points, descriptor

    '''
    :brief 注册人脸，保存人脸信息到本地
    :param descriptor 人脸描述符
    :param user_id 用户ID
    :param user_name 用户名
    '''
    def register(self, descriptor, user_id=1, user_name='undefined'):
        f = open(self.__csv_filepath, 'a', newline='')
        csv_writer = csv.writer(f)
        csv_format = [user_id, user_name, descriptor]
        csv_writer.writerow(csv_format)
        f.close()
        print('id:', user_id, 'name:', user_name, 'face saved')

    '''
    :brief 从数据表中查找人脸
    :param src_des 目标人脸的描述符
    :return res 对比结果
    :return user_id 用户ID
    :return user_name 用户名
    '''
    def check(self, src_des):
        res = 0
        uid = None
        uname = None
        with open(self.__csv_filepath, 'r') as f:
            csv_reader = csv.reader(f)
            user_id_list = []
            user_name_list = []
            src_des = np.asarray(src_des, dtype=np.float64)
            res_set = []
            for line in csv_reader:
                user_id_list.append(line[0])
                user_name_list.append(line[1])
                can_des = eval(line[2])
                can_des = np.asarray(can_des, dtype=np.float64)
                dis = np.linalg.norm(can_des - src_des)  # 计算欧式距离
                res_set.append(dis)
            # 从结果集中选一个匹配度最高的作为结果
            index = 0
            min_dis = 9999
            min_index = 0
            for i in res_set:
                if i < min_dis:
                    min_index = index
                    min_dis = i
                index += 1
            # 检查是否在阈值范围内
            if min_dis <= self.__threshold:
                uid = user_id_list[min_index]
                uname = user_name_list[min_index]
                res = 1
            f.close()
        return res, uid, uname


if __name__ == '__main__':
    face_recognition = FaceRecognition()
    camera = cv.VideoCapture(0, cv.CAP_DSHOW)
    while True:
        ret, frame = camera.read()
        if ret:
            ret, r, ps, des = face_recognition.recognise(frame)
            if ret == 1:
                for point in ps.parts():
                    cv.circle(frame, (point.x, point.y), 2, (0, 255, 0), -1)
                cv.rectangle(frame, (r[0], r[1]), (r[2], r[3]), (0, 0, 255), 1)
            cv.imshow('res', frame)
            if cv.waitKey(10) & 0xFF == ord('q'):
                break
            # if ret == 1:
                # face_recognition.register(des, 1, 'admin')
                # face_recognition.check(des)
    camera.release()
    cv.destroyAllWindows()
