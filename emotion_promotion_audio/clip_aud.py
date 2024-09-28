from pydub import AudioSegment
 
audio_file = "./sad.mp3"
audio = AudioSegment.from_file(audio_file)
 
start = 0  # 从0秒处开始
end = 1000    # 到1秒处结束
 
# 剪切音频
clipped_audio = audio[start:end]
 
# 保存剪切后的音频
clipped_audio_file = "sad_2.mp3"
clipped_audio.export(clipped_audio_file, format="mp3")