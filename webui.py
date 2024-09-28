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

import gradio as gr
import shutil
import os
from run import main_face, main_audio

def generate_video_face(video,detect_emotions):
    try:
        video_name = 'gradio_' + os.path.basename(video.name)
        shutil.copyfile(video.name, video_name)
        print("视频生成成功 - Face")
        mf = main_face(video_name, detect_emotions)
        if mf != '2＆2以上の顔が存在するので音声感情識別を選択して下さい':
            return "视频生成成功 - Face", mf
        else:
            return f"视频生成失败 - Face:{mf}", None
        # return "处理完成 - Face"
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

def generate_video_audio(video, detect_emotions):
    video_name = 'gradio_' + os.path.basename(video.name)
    shutil.copyfile(video.name, video_name)
    print("视频生成成功 - Audio")
    return "视频生成成功 - Audio", main_audio(video_name, detect_emotions)
    # return "音声感情識別完了！"

input_video = gr.inputs.File(label="上传视频")
output_text = gr.outputs.Textbox()

# 创建一个界面，包含多个按钮，每个按钮对应不同的回调函数
def main_interface():
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("## 视频情绪识别系统")
        with gr.Row():
            input_video = gr.File(label="上传视频")
        with gr.Row():
            emotions = gr.CheckboxGroup(
                ["angry", "fear", "happy", "sad", "surprise"], 
                label="感情を選んでくだいさい"
            )
        with gr.Row():
            # face_audio_btn = gr.Button("生成视频 (Face and Audio)")
            face_btn = gr.Button("生成视频 (Face)")
            audio_btn = gr.Button("生成视频 (Audio)")
        with gr.Row():
            output_text = gr.Textbox(label="处理状态")
        with gr.Row():
            output_video = gr.Video(label="生成的视频")
        def update_output(status, video_path):
            if video_path is not None:
                return status, gr.update(value=video_path, visible=True)
            else:
                return status, gr.update(visible=False)

        # face_audio_btn.click(generate_video_face_audio, inputs=input_video, outputs=output_text)
        face_btn.click(generate_video_face, inputs=[input_video, emotions], outputs=[output_text,output_video],postprocess=update_output)
        audio_btn.click(generate_video_audio, inputs=[input_video, emotions], outputs=[output_text,output_video],postprocess=update_output)

    return demo

iface = main_interface()
iface.launch(share=True)
