import cv2
import numpy as np
from PIL import Image
import torch.nn as nn
import torch
from torchvision import transforms
# from moviepy.editor import VideoFileClip
import os
import time


# haar xml文件的引入
face_xml = cv2.CascadeClassifier('./haarcascade_frontalface_alt.xml')
eye_xml = cv2.CascadeClassifier('./haarcascade_eye_tree_eyeglasses.xml')

# 情绪识别
class VGG(nn.Module):
    def __init__(self, features, num_classes=1000, init_weights=False):
        super(VGG, self).__init__()
        self.features = features
        self.classifier = nn.Sequential(
            nn.Linear(512*7*7, 4096),
            nn.ReLU(True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, num_classes)
        )
        if init_weights:
            self._initialize_weights()

    def forward(self, x):
        # N x 3 x 224 x 224
        x = self.features(x)
        # N x 512 x 7 x 7
        x = torch.flatten(x, start_dim=1)
        # N x 512*7*7
        x = self.classifier(x)
        return x

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                # nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)


class FaceEmotion():

    def __init__(self, video_name):
        self.video_name = video_name
        self.file_name, _ = os.path.splitext(self.video_name)
        self.cfgs = {
            'vgg11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
            'vgg13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
            'vgg16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
            'vgg19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
        }
        self. device = torch.device("cuda:0" if torch.cuda.is_available() else "mps")
        print("use device:", self.device)
        self.data_transform = transforms.Compose(
            [transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        self.class_indict = {
            "0": "angry",
            "1": "disgust",
            "2": "fear",
            "3": "happy",
            "4": "neutral",
            "5": "sad",
            "6": "surprise"
        }
        # 创建网络
        self.model = self.vgg(model_name="vgg16", num_classes=7).to(self.device)
        # 加载权重
        self.weights_path = "./Lin_vgg16Net.pth"
        self.model.load_state_dict(torch.load(self.weights_path, map_location=self.device))
        

    def make_features(self, cfg: list):
        layers = []
        in_channels = 3
        for v in cfg:
            if v == "M":
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
                layers += [conv2d, nn.ReLU(True)]
                in_channels = v
        return nn.Sequential(*layers)

    # 网络
    def vgg(self, model_name="vgg16", **kwargs):
        assert model_name in self.cfgs, "Warning: model number {} not in cfgs dict!".format(model_name)
        cfg = self.cfgs[model_name]
        model = VGG(self.make_features(cfg), **kwargs)
        return model

   
    def get_face_emotion(self):
        video_path = self.video_name
        self.output_video_path = self.file_name + '_with_emotion.mp4'

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Cannot open video file")
            exit()

        # 获取视频帧率和帧尺寸
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        fps += 1
        # print('<<<<<<<<<<<<<<<,,,')
        # print(fps)
        # print('>>>>>>>>>>>>>>>>>>>>>>>>>>')
        # import sys
        # sys.exit()
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 获取视频总帧数

        # 设置输出视频参数
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(self.output_video_path, fourcc, fps, (frame_width, frame_height))

        frame_count = 0  # 记录处理的帧数

        # while cap.isOpened():
        #     # 逐帧读取视频
        #     ret, img = cap.read()
        #     if not ret:
        #         break  # 视频结束，退出循环

        #     # 计算haar特征和对图像进行灰度转化gray
        #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #     # 人脸识别的检测
        #     faces = face_xml.detectMultiScale(gray, 1.3, 5)
        #     print('检测到人脸数量：', len(faces))  # 检测当前的人脸个数

        #     # 绘制人脸，为检测到的每个人脸进行画方框绘制
        #     # -------------------------------人 脸 检 测-------------------------------
        #     for (x, y, w, h) in faces:
        #         cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)  # 人脸识别
        #         roi_face = gray[y:y + h, x:x + w]  # 灰色人脸数据
        #         roi_color = img[y:y + h, x:x + w]  # 彩色人脸数据

        #         # 1 gray
        #     # -------------------------------双 目 注 视-------------------------------
        #         eyes = eye_xml.detectMultiScale(roi_face)  # 眼睛识别，图片类型必须是灰度图
        #         if len(eyes) == 2: # 双眼注视
        #             print('-------检测到目光注视!---------')  # 打印检测出眼睛的个数
        #             for (e_x, e_y, e_w, e_h) in eyes:  # 绘制眼睛方框到彩色图片上
        #                 cv2.rectangle(roi_color, (e_x, e_y), (e_x + e_w, e_y + e_h), (0, 255, 0), 2)

        #     # -------------------------------情 绪 识 别-------------------------------
        #     Emotion_detect = True

        #     if Emotion_detect and len(faces) >= 1:
        #         image = roi_color.copy()
        #         img_Image = Image.fromarray(np.uint8(image))
        #         # [N, C, H, W]
        #         Img = self.data_transform(img_Image)
        #         # expand batch dimension
        #         Img = torch.unsqueeze(Img, dim=0)
        #         self.model.eval()
        #         with torch.no_grad():
        #             # predict class
        #             output = torch.squeeze(self.model(Img.to(self.device))).cpu()
        #             predict = torch.softmax(output, dim=0)
        #             predict_cla = torch.argmax(predict).numpy()

        #         dic = {self.class_indict[str(predict_cla)]: predict[predict_cla].numpy()}
        #         print(dic,'\n')
        #         # img
        #         Emotion_class = 'Emotion:{}'.format(self.class_indict[str(predict_cla)])

        #         prob = 'prob:{:.2f}%'.format(predict[predict_cla].numpy()*100)
        #         cv2.putText(img, Emotion_class, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        #         cv2.putText(img, prob, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #     else:
        #         pass

        #     # 将帧写入输出视频
        #     writer.write(img)

        #     frame_count += 1  # 更新处理的帧数
        #     if frame_count >= total_frames:
        #         break  # 处理完所有视频帧，退出循环
        #     # 延迟一段时间以保持原视频的帧率
        #     time.sleep(1 / fps)

        # # 完成所有操作后，释放捕获器和写入器
        # cap.release()
        # writer.release()
        # cv2.destroyAllWindows()


        while cap.isOpened():
            # 逐帧读取视频
            ret, img = cap.read()
            if not ret:
                break  # 视频结束，退出循环

            # 计算haar特征和对图像进行灰度转化gray
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 人脸识别的检测
            faces = face_xml.detectMultiScale(gray, 1.3, 5)
            print('检测到人脸数量：', len(faces))  # 检测当前的人脸个数

            # 绘制人脸，为检测到的每个人脸进行画方框绘制
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)  # 人脸识别
                roi_face = gray[y:y + h, x:x + w]  # 灰色人脸数据
                roi_color = img[y:y + h, x:x + w]  # 彩色人脸数据

                # 人脸情绪识别
                Emotion_detect = True

                if Emotion_detect and len(faces) >= 1:
                # if Emotion_detect:
                    image = roi_color.copy()
                    img_Image = Image.fromarray(np.uint8(image))
                    Img = self.data_transform(img_Image)
                    Img = torch.unsqueeze(Img, dim=0)
                    self.model.eval()
                    with torch.no_grad():
                        output = torch.squeeze(self.model(Img.to(self.device))).cpu()
                        predict = torch.softmax(output, dim=0)
                        predict_cla = torch.argmax(predict).numpy()

                    Emotion_class = 'Emotion:{}'.format(self.class_indict[str(predict_cla)])
                    prob = 'prob:{:.2f}%'.format(predict[predict_cla].numpy()*100)
                    cv2.putText(img, Emotion_class, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.putText(img, prob, (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # 眼睛检测
                eyes = eye_xml.detectMultiScale(roi_face)
                if len(eyes) == 2: # 双眼注视
                    print('-------检测到目光注视!---------')  # 打印检测出眼睛的个数
                    for (e_x, e_y, e_w, e_h) in eyes:  # 绘制眼睛方框到彩色图片上
                        cv2.rectangle(roi_color, (e_x, e_y), (e_x + e_w, e_y + e_h), (0, 255, 0), 2)

            # 将帧写入输出视频
            writer.write(img)

            frame_count += 1  # 更新处理的帧数
            if frame_count >= total_frames:
                break  # 处理完所有视频帧，退出循环
            # 延迟一段时间以保持原视频的帧率
            time.sleep(1 / fps)
        # 完成所有操作后，释放捕获器和写入器
        cap.release()
        writer.release()
        cv2.destroyAllWindows()

