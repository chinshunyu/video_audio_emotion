from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

def insert_promotion(audio_path):
    # 加载长音频和短音频
    long_audio = AudioSegment.from_file(audio_path)
    final_audio = long_audio
    happy_audio = AudioSegment.from_file('./emotion_promotion_audio/joy.mp3')
    insert_position = 3000
    # 分割长音频
    first_part = final_audio[:insert_position]
    second_part = final_audio[insert_position:]
    # 混合短音频和长音频的第二部分
    mixed_audio = second_part.overlay(happy_audio)
    # 拼接混合后的音频
    final_audio = first_part + mixed_audio
    print('拼接成功')
    final_audio.export(audio_path, format="wav")
    print('~~~~~~~~~~~~~~~~~~~~~~~~`')
    print(audio_path)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')

if __name__ == '__main__':
    insert_promotion('./gradio_1.wav')