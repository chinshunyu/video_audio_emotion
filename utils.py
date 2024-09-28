from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

def merge_video_audio(video_path, audio_path, output_path):
    # 加载视频和音频文件
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    # 将音频添加到视频中
    video_clip = video_clip.set_audio(audio_clip)

    # 保存合并后的视频文件
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # 关闭视频和音频文件
    video_clip.close()
    audio_clip.close()

def insert_promotion(audio_path):
    # 加载长音频和短音频
    long_audio = AudioSegment.from_file(audio_path)
    final_audio = long_audio
    angry_audio = AudioSegment.from_file('./emotion_promotion_audio/angry.mp3')
    fear_audio = AudioSegment.from_file('./emotion_promotion_audio/fear_2.mp3')
    happy_audio = AudioSegment.from_file('./emotion_promotion_audio/joy.mp3')
    sad_audio = AudioSegment.from_file('./emotion_promotion_audio/sad_2.mp3')
    surprise_audio = AudioSegment.from_file('./emotion_promotion_audio/surprise.mp3')
    with open('./face_detected_emotions.txt','r') as f:
        lines = f.readlines()
        if not lines:
            return
        for line in lines:
            line_dic = eval(line)
            emotion = line_dic['detect_emotion']
            fpth = line_dic['fpth'] * 1.0
            fps = line_dic['fps'] * 1.0
            sec = fpth / fps
            print(f'插入第{sec}秒')
            insert_position = sec * 1000
            if emotion == 'angry':
                short_audio = angry_audio
            elif emotion == 'fear':
                short_audio = fear_audio
            elif emotion == 'happy':
                short_audio = happy_audio
            elif emotion == 'sad':
                short_audio = sad_audio
            elif emotion == 'surprise':
                short_audio = surprise_audio
            
            # 分割长音频
            first_part = final_audio[:insert_position]
            second_part = final_audio[insert_position:]
            # 混合短音频和长音频的第二部分
            mixed_audio = second_part.overlay(short_audio)
            # 拼接混合后的音频
            final_audio = first_part + mixed_audio
            print('拼接成功')
        final_audio.export(audio_path, format="wav")