import os
import sys
import argparse
import functools
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from mser.predict import MSERPredictor
from mser.utils.utils import add_arguments, print_arguments


print(current_dir)
parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
add_arg('configs',          str,    os.path.join(current_dir,'configs/bi_lstm.yml'),   '配置文件')
add_arg('use_gpu',          bool,   False,                    '是否使用GPU预测')
add_arg('audio_path',       str,    os.path.join(current_dir,'dataset/audios/angry/audio_0.wav'), '音频路径')
add_arg('model_path',       str,    os.path.join(current_dir, 'models/BiLSTM_Emotion2Vec/best_model/'),     '导出的预测模型文件路径')
args = parser.parse_args()
print_arguments(args=args)

# 获取识别器
def get_predictor():
    predictor = MSERPredictor(configs=args.configs,
                            model_path=args.model_path,
                            use_gpu=args.use_gpu)
    return predictor
# predictor = get_predictor()
# label, score = predictor.predict(audio_data='./dataset/chunk.wav')

# print(f'音频：{args.audio_path} 的预测结果标签为：{label}，得分：{score}')
