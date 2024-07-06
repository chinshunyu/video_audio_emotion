import os
import pretty_errors
os.system('clear')
pretty_errors.configure(
    separator_character='*',
    filename_display=pretty_errors.FILENAME_EXTENDED,
    line_number_first=True,
    display_link=True,
    lines_before=5,
    lines_after=2,
    line_color=pretty_errors.RED+'> '+pretty_errors.BRIGHT_RED,
    filename_color=pretty_errors.YELLOW,
    header_color=pretty_errors.BRIGHT_GREEN,
    link_color=pretty_errors.BRIGHT_BLUE,
    code_color=pretty_errors.BRIGHT_RED,
    # code_color='  '+pretty_errors.default_config.line_color
    line_number_color=pretty_errors.BRIGHT_RED
)

# from pyAudioAnalysis import audioBasicIO
# from pyAudioAnalysis import audioFeatureExtraction
# from pyAudioAnalysis import audioTrainTest as aT
# pyAudioAnalysis           0.2.5
# # 载入音频文件
# audio_file = "003.wav"

# # 提取音频特征
# # [Fs, x] = audioBasicIO.read_audio_file(audio_file)
# [Fs, x] = audioBasicIO.readAudioFile(audio_file)
# print('========================')
# print(x)
# print('=============================')
# # 提取音频特征
# win_len = 0.050 * Fs  # 设置窗口长度为 50 毫秒
# step = 0.025 * Fs      # 设置帧移为 25 毫秒
# features, feature_names = audioFeatureExtraction.stFeatureExtraction(x, Fs, win_len, step)

# # features, feature_names = audioFeatureExtraction.stFeatureExtraction(x, Fs, 0.050*Fs, 0.025*Fs)

# # 加载情绪分类器
# model_path = "data/svm_rbf_emotion"
# # 这里使用了 SVM RBF 核的分类器，你也可以选择其他分类器
# result, P, classNames = aT.fileClassification(audio_file, model_path, "svm_rbf")

# # 输出情绪标签
# print("Predicted emotion:", classNames[result[0]])


from pyAudioAnalysis import audioSegmentation as aS

# 读取音频文件
filename = "003.wav"

# 将音频文件分割成段落
segments = aS.speaker_diarization(filename, 3)

# 对每个段落进行情感分类
for segment in segments:
    emotion = aS.emotionFile(filename, [segment[0], segment[1]], "svm_rbf")
    print("段落起始时间: ", segment[0], " 结束时间: ", segment[1], "情感状态: ", emotion)
