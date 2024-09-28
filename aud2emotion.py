import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import detect_silence, split_on_silence
from asari.api import Sonar
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os
import datetime
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'speech_emotion')))
from speech_emotion.infer import get_predictor
from ASR.LongFormAsr import createRequest
import json
import re

class Subtitle(object):
    def __init__(self, video_name) -> None:
        self.video_name = video_name
        self.video = VideoFileClip(video_name)
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(self.video.duration)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        self.sonar = Sonar()
        self.speech_predictor = get_predictor()
        self.min_silence_len=220
        self.silence_thresh=-41
    def extract_audio(self):
        self.file_name, _ = os.path.splitext(self.video_name)
        self.audio_name = self.file_name + '.wav'
        audio = self.video.audio
        audio.write_audiofile(self.audio_name, codec="pcm_s16le")  # 保存为 WAV 格式的音频文件

    def get_aud_emotion(self, detect_emotions):
        # 语音识别并生成字幕文件
        get_result_result = createRequest(self.audio_name)
        get_result_result = json.loads(get_result_result)
        results =  get_result_result['result']
        short_sentences = []
        for result in results:
            words = result['words']
            word_timestamps = result['word_timestamps']
            stop_idxs = []
            for idx, word in enumerate(words):
                if '、' in word or '。' in word:
                    stop_idxs.append(idx)
            
            last_stop_idx = 0
            for idx, stop_idx in enumerate(stop_idxs):
                if idx == 0:
                    this_text = words[last_stop_idx:stop_idx+1]
                else:
                    this_text = words[last_stop_idx+1:stop_idx+1]
                if idx != 0:
                    last_stop_idx = stop_idxs[idx]
                else:
                    last_stop_idx = stop_idxs[0]
                this_stop_time = word_timestamps[stop_idx]
                this_text = ''.join(this_text)
                short_sentences.append({'short_sentence':this_text,
                                        'stop_time':this_stop_time})
        
        # 获取每一小段音频的情感，并添加到short_sentence的文本中
        # 读取原始音频文件
        all_audio = AudioSegment.from_wav(self.audio_name)
        # 初始开始时间
        start_time = 0
        pause_times = [i['stop_time'] for i in short_sentences]
        aud_emotions = []
        promotion_emo =[] # 提示音情绪{'emo':'','time':}
        for i, end_time in enumerate(pause_times):
            # 提取音频片段
            audio_segment = all_audio[start_time:end_time]
            
            # 保存音频片段
            output_file = 'output_segment.wav'
            audio_segment.export(output_file, format="wav")
            label, score = self.speech_predictor.predict(audio_data='output_segment.wav')
            if label in detect_emotions:
                emo = label
                time = end_time
                promotion_emo.append({'emo':emo,
                                      'time':time})
            aud_emotions.append((label,score))
            # 更新开始时间
            start_time = end_time

        # 将语音情感识别结果（aud_emotions）添加到short_sentences文本中，然后再写入字幕
        short_sentences_new = []
        for idx, short_sentence in enumerate(short_sentences):
            text = short_sentence['short_sentence']
            stop_time = short_sentence['stop_time']
            text_new = text + f'({aud_emotions[idx][0]}<{aud_emotions[idx][1]}>)'
            short_sentence_new = {'short_sentence':text_new,
                                  'stop_time':stop_time}
            short_sentences_new.append(short_sentence_new)
        
        # 在出现检测的情绪的地方加上提示音
        long_audio = all_audio
        final_audio = long_audio
        angry_audio = AudioSegment.from_file('./emotion_promotion_audio/angry.mp3')
        fear_audio = AudioSegment.from_file('./emotion_promotion_audio/fear_2.mp3')
        happy_audio = AudioSegment.from_file('./emotion_promotion_audio/joy.mp3')
        sad_audio = AudioSegment.from_file('./emotion_promotion_audio/sad_2.mp3')
        surprise_audio = AudioSegment.from_file('./emotion_promotion_audio/surprise.mp3')
        for pe in promotion_emo:
            emo = pe['emo']
            time = pe['time']
            if emo == 'angry':
                short_audio = angry_audio
            elif emo == 'fear':
                short_audio = fear_audio
            elif emo == 'happy':
                short_audio = happy_audio
            elif emo == 'sad':
                short_audio = sad_audio
            elif emo == 'surprise':
                short_audio = surprise_audio
            
            # 分割长音频
            first_part = final_audio[:time]
            second_part = final_audio[time:]
            # 混合短音频和长音频的第二部分
            mixed_audio = second_part.overlay(short_audio)
            # 拼接混合后的音频
            final_audio = first_part + mixed_audio
        final_audio.export(self.audio_name, format="wav")
        print('音频情绪：插入短音频成功')

        def ms_to_timecode(ms):
            td = datetime.timedelta(milliseconds=ms)
            return str(td)[:-3].replace('.', ',')
        # 生成 SRT 文件内容
        srt_content = ""
        previous_stop_time = 0
        for i, item in enumerate(short_sentences_new):
            start_time = previous_stop_time
            stop_time = item['stop_time']
            
            srt_content += f"{i + 1}\n"
            srt_content += f"{ms_to_timecode(start_time)} --> {ms_to_timecode(stop_time)}\n"
            srt_content += f"{item['short_sentence']}\n\n"
            
            previous_stop_time = stop_time
        # 写入到文件
        with open("subtitles.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)

    def merge_sub_movie(self, emotion_video_name):
        # 读取视频文件
        # video_path = "test002.mp4"
        video = VideoFileClip(emotion_video_name)

        # 生成字幕剪辑
        def time_to_seconds(time_str):
            time_str = time_str.strip()
            parts = re.split('[:,]', time_str)
            # 默认值
            hour, minute, second, millisecond = 0, 0, 0, 0
            if len(parts) == 2:  # 只提供了分钟和秒
                minute, second = map(int, parts)
            elif len(parts) == 3:  # 提供了小时、分钟和秒
                hour, minute, second = map(int, parts)
            elif len(parts) == 4:  # 提供了小时、分钟、秒和毫秒
                hour, minute, second, millisecond = map(int, parts)
            else:
                raise ValueError(f"Unexpected time format: {time_str}")
            return hour * 3600 + minute * 60 + second + millisecond / 1000
        
        subtitles_path = "subtitles.srt"
        subtitles_clips = []
        with open(subtitles_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.isdigit():  # 判断是否为字幕序号
                    continue
                if "-->" in line:  # 判断是否为时间轴
                    start, end = line.split("-->")
                    start_time = time_to_seconds(start)
                    end_time = time_to_seconds(end)
                    continue
                if line:  # 判断是否为字幕文本
                    # subtitle_clip = TextClip(line, fontsize=24, color='white', font='Osaka',method='caption').set_position(('center', 'bottom')).set_start(start_time).set_end(end_time)
                    subtitle_clip = TextClip(line, fontsize=24, color='green', font='Osaka').set_position(('center', 'bottom')).set_start(start_time).set_end(end_time)
                    subtitles_clips.append(subtitle_clip)

        # 合并视频与字幕
        video_with_subtitles = CompositeVideoClip([video] + subtitles_clips)

        # 保存带字幕的视频
        self.output_path = self.file_name+ '_subtitle.mp4'
        video_with_subtitles.write_videofile(self.output_path, codec="libx264", fps=video.fps)
