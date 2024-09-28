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

from face2emotion import FaceEmotion
from aud2emotion import Subtitle
from utils import merge_video_audio,insert_promotion
import os


def main_face(video_name, detect_emotions):
    st = Subtitle(video_name=video_name)
    fe = FaceEmotion(video_name=video_name)
    face_num = fe.count_video_face_num()
    if face_num == 2:
        print('2＆2以上の顔が存在するので音声感情識別を選択して下さい')
        return '2＆2以上の顔が存在するので音声感情識別を選択して下さい'
    st.extract_audio()
    fe.get_face_emotion(detect_emotions)
    insert_promotion(st.audio_name)
    merge_video_audio(fe.output_video_path, st.audio_name, 'face_'+ fe.output_video_path)
    os.remove(st.audio_name)
    os.remove(fe.output_video_path)
    return 'face_'+ fe.output_video_path

def main_audio(video_name, detect_emotions):
    st = Subtitle(video_name=video_name)
    st.extract_audio()
    # st.get_text_emotion()
    st.get_aud_emotion(detect_emotions)
    st.merge_sub_movie(video_name)
    merge_video_audio(st.output_path, st.audio_name, 'audio_'+ st.output_path)
    os.remove(st.audio_name)
    os.remove(st.output_path)
    return 'audio_'+ st.output_path
    

if __name__ == '__main__':
    video_name = '1.mp4'
    # main_face(video_name, detect_emotion='happy')
    main_audio(video_name, detect_emotions = ['angry','fear','happy','sad','surprise'])
