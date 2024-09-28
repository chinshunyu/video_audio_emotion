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



from pyAudioAnalysis import audioSegmentation as aS

# 读取音频文件
filename = "003.wav"

# 将音频文件分割成段落
segments = aS.speaker_diarization(filename, 3)

# 对每个段落进行情感分类
for segment in segments:
    emotion = aS.emotionFile(filename, [segment[0], segment[1]], "svm_rbf")
    print("段落起始时间: ", segment[0], " 结束时间: ", segment[1], "情感状态: ", emotion)
