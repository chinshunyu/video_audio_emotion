import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import detect_silence, split_on_silence
from asari.api import Sonar
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'speech_emotion')))
from speech_emotion.infer import get_predictor


class Subtitle(object):
    def __init__(self, video_name) -> None:
        self.video_name = video_name
        self.video = VideoFileClip(video_name)
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(self.video.duration)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        self.sonar = Sonar()
        self.speech_predictor = get_predictor()
        # 002
        # self.min_silence_len=500
        # self.silence_thresh=-50
        # 003
        # self.min_silence_len=260 #410
        # self.silence_thresh=-50 #绝对值越小切得越短 -58
        ## 8
        # self.min_silence_len=200
        # self.silence_thresh=-40
        self.min_silence_len=220
        self.silence_thresh=-41
    def extract_audio(self):
        self.file_name, _ = os.path.splitext(self.video_name)
        self.audio_name = self.file_name + '.wav'
        audio = self.video.audio
        audio.write_audiofile(self.audio_name, codec="pcm_s16le")  # 保存为 WAV 格式的音频文件

    def get_text_emotion(self):
        recognizer = sr.Recognizer()
        # 读取音频文件
        sound = AudioSegment.from_wav(self.audio_name)
        # 检测视频开头的静默部分并计算初始偏移量
        # 002
        # initial_silence = detect_silence(sound, min_silence_len=500, silence_thresh=-50)
        # 003
        initial_silence = detect_silence(sound, min_silence_len=self.min_silence_len, silence_thresh=self.silence_thresh)
        # print(initial_silence)
        if initial_silence:
            initial_offset = initial_silence[0][1]  # 初始静默的结束时间
        else:
            initial_offset = 0  # 如果找不到静默部分，则初始偏移量为0

        # 切片识别音频并保存文本和起始时间
        subtitle_texts = []
        subtitle_start_times = []
        # 002
        # audio_chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=-50)
        # 003
        audio_chunks = split_on_silence(sound, min_silence_len=self.min_silence_len, silence_thresh=self.silence_thresh)

        # 对每个切片进行语音识别，并记录识别结果和起始时间
        offset = initial_offset

        for i, chunk in enumerate(audio_chunks):
            print(f'i={i}')
            chunk.export("chunk.wav", format="wav")
            #TODO 对chunk.wav做音频情绪识别并把识别结果添加到字幕
            label, score = self.speech_predictor.predict(audio_data='chunk.wav')
            # 添加字幕
            with sr.AudioFile("chunk.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language='ja-JP')
                    
                    # 情感识别
                    text += (f" ({label}<{score}>)")
                    # text = text.replace(' ', '\n').replace('\t', '\n')
                    # if len(text) > 30:
                    #     po = len(text)//2
                    #     text = text[:po] + '\n'+text[po:]
                    print(text)
                    # all_emo = self.sonar.ping(text=text)
                    # top_class = all_emo['top_class']
                    # for j in all_emo['classes']:
                    #     if j['class_name'] == top_class:
                    #         text += (f"({ top_class} <{'%.2f' % j['confidence']}>)")
                except sr.UnknownValueError:
                    text = " "  # 如果无法识别，则将文本设为空字符串
                subtitle_texts.append(text)
                subtitle_start_times.append(offset)
                # 考虑静默时间的长度
                # 002
                # if i < len(initial_silence)-1:
                #     offset += (len(chunk) + (initial_silence[i+1][1]-initial_silence[i+1][0])-300)  # 添加静默时间长度
                # else:
                #     offset += 300
                # 008
                if i < len(initial_silence)-1:
                    offset += (len(chunk) + (initial_silence[i+1][1]-initial_silence[i+1][0])-200)  # 添加静默时间长度
                else:
                    offset += 300 
                # offset += len(chunk)
        os.remove('chunk.wav')
        # 生成字幕文件
        with open("subtitles.srt", "w", encoding="utf-8") as file:
            for i, text in enumerate(subtitle_texts):
                start_time = subtitle_start_times[i] / 1000  # 起始时间，转换为秒
                if i < len(subtitle_start_times) - 1:
                    end_time = subtitle_start_times[i + 1] / 1000  # 下一个字幕的起始时间
                else:
                    end_time = self.video.duration  # 如果是最后一个字幕，则结束时间为视频总时长
                file.write(f"{i + 1}\n")
                file.write(f"{start_time:.3f} --> {end_time:.3f}\n")
                file.write(f"{text}\n\n")

        print("Subtitles generated successfully!")

    def merge_sub_movie(self, emotion_video_name):
        print('====================')
        print(emotion_video_name)
        print('===============================')
        # 读取视频文件
        # video_path = "test002.mp4"
        video = VideoFileClip(emotion_video_name)

        # 生成字幕剪辑
        subtitles_path = "subtitles.srt"
        subtitles_clips = []
        with open(subtitles_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.isdigit():  # 判断是否为字幕序号
                    continue
                if "-->" in line:  # 判断是否为时间轴
                    start, end = line.split("-->")
                    start_time = float(start.split()[0].replace(",", "."))
                    end_time = float(end.split()[0].replace(",", "."))
                    continue
                if line:  # 判断是否为字幕文本
                    # subtitle_clip = TextClip(line, fontsize=24, color='white', font='Osaka',method='caption').set_position(('center', 'bottom')).set_start(start_time).set_end(end_time)
                    subtitle_clip = TextClip(line, fontsize=24, color='green', font='Osaka').set_position(('center', 'bottom')).set_start(start_time).set_end(end_time)
                    subtitles_clips.append(subtitle_clip)

        # 合并视频与字幕
        video_with_subtitles = CompositeVideoClip([video] + subtitles_clips)

        # 保存带字幕的视频
        # output_path = "output_video_with_subtitles.mp4"
        self.output_path = self.file_name+ '_subtitle.mp4'
        video_with_subtitles.write_videofile(self.output_path, codec="libx264", fps=video.fps)
