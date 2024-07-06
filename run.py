from face2emotion import FaceEmotion
from text2emotion import Subtitle
from utils import merge_video_audio
import os

def main_face_audio(video_name):
    st = Subtitle(video_name=video_name)
    fe = FaceEmotion(video_name=video_name)

    st.extract_audio()
    st.get_text_emotion()
    fe.get_face_emotion()
    # merge_video_audio(fe.output_video_path, st.audio_name, 'aud_'+ fe.output_video_path)
    st.merge_sub_movie(fe.output_video_path)
    merge_video_audio(st.output_path, st.audio_name,  'face_audio_'+ fe.output_video_path)
    os.remove(st.audio_name)
    # os.remove(st.video_name)
    os.remove(fe.output_video_path)
    os.remove(st.output_path)
    # os.remove('chunk.wav')
    # os.remove('fce_audio_'+ fe.output_video_path)

def main_face(video_name):
    st = Subtitle(video_name=video_name)
    fe = FaceEmotion(video_name=video_name)
    st.extract_audio()
    fe.get_face_emotion()
    merge_video_audio(fe.output_video_path, st.audio_name, 'face_'+ fe.output_video_path)
    os.remove(st.audio_name)
    os.remove(fe.output_video_path)

def main_audio(video_name):
    st = Subtitle(video_name=video_name)
    st.extract_audio()
    st.get_text_emotion()
    st.merge_sub_movie(video_name)
    merge_video_audio(st.output_path, st.audio_name, 'audio_'+ st.output_path)
    os.remove(st.audio_name)
    os.remove(st.output_path)
    

if __name__ == '__main__':
    video_name = '8.mp4'
    main_face_audio(video_name)
