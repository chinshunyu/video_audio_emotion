from moviepy.editor import VideoFileClip, AudioFileClip

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

# 调用函数来合并视频和音频文件
# merge_video_audio("./output_video_with_emotion.mp4", "./temp_audio.mp3", "output_video_with_audio.mp4")



# from moviepy.editor import VideoFileClip, AudioFileClip

# def merge_video_audio(video_path, audio_path, output_path):
#     # 加载视频和音频文件
#     video_clip = VideoFileClip(video_path)
#     audio_clip = AudioFileClip(audio_path)

#     # 确定长度差异
#     video_duration = video_clip.duration
#     audio_duration = audio_clip.duration
#     duration_difference = abs(video_duration - audio_duration)

#     if video_duration > audio_duration:
#         # 如果视频比音频长，则截取视频以匹配音频的长度
#         video_clip = video_clip.subclip(0, audio_duration)
#     elif audio_duration > video_duration:
#         # 如果音频比视频长，则截取音频以匹配视频的长度
#         audio_clip = audio_clip.subclip(0, video_duration)

#     # 将音频添加到视频中
#     video_clip = video_clip.set_audio(audio_clip)

#     # 保存合并后的视频文件
#     video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

#     # 关闭视频和音频文件
#     video_clip.close()
#     audio_clip.close()