# Copyright (c) 2024 Alibaba Inc (authors: Xiang Lyu, Liu Yue)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
import argparse
import gradio as gr
import numpy as np
import torch
import torchaudio
import random
import librosa
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('{}/third_party/Matcha-TTS'.format(ROOT_DIR))
from cosyvoice.cli.cosyvoice import CosyVoice, CosyVoice2
from cosyvoice.utils.file_utils import load_wav, logging
from cosyvoice.utils.common import set_all_random_seed
import os

# Change default Gradio temp directory
os.environ["GRADIO_TEMP_DIR"] = "/data/codes/CosyVoice/gradio_temp"

# Ensure the directory exists and has correct permissions
os.makedirs("/data/codes/CosyVoice/gradio_temp", exist_ok=True)

inference_mode_list = ['自然语言控制']
instruct_dict = {'自然语言控制': '1. 输入instruct文本\n2. 点击生成音频按钮'}
stream_mode_list = [('否', False), ('是', True)]
max_val = 0.8


def generate_seed():
    seed = random.randint(1, 100000000)
    return {
        "__type__": "update",
        "value": seed
    }


def postprocess(speech, top_db=60, hop_length=220, win_length=440):
    speech, _ = librosa.effects.trim(
        speech, top_db=top_db,
        frame_length=win_length,
        hop_length=hop_length
    )
    if speech.abs().max() > max_val:
        speech = speech / speech.abs().max() * max_val
    speech = torch.concat([speech, torch.zeros(1, int(cosyvoice.sample_rate * 0.2))], dim=1)
    return speech


def change_instruction(mode_checkbox_group):
    return instruct_dict[mode_checkbox_group]


def generate_audio(tts_text, mode_checkbox_group, instruct_text,
                   seed, stream, speed):
    # if prompt_wav_upload is not None:
    #     prompt_wav = prompt_wav_upload
    # elif prompt_wav_record is not None:
    #     prompt_wav = prompt_wav_record
    # else:
    #     prompt_wav = None
    # if instruct mode, please make sure that model is iic/CosyVoice-300M-Instruct and not cross_lingual mode
    if mode_checkbox_group in ['自然语言控制']:
        # if cosyvoice.instruct is False:
        #     gr.Warning('您正在使用自然语言控制模式, {}模型不支持此模式, 请使用iic/CosyVoice-300M-Instruct模型'.format(args.model_dir))
        #     yield (cosyvoice.sample_rate, default_data)
        if instruct_text == '':
            gr.Warning('您正在使用自然语言控制模式, 请输入instruct文本')
            yield (cosyvoice.sample_rate, default_data)

    seed = 0
    
    logging.info('get instruct inference request')
    set_all_random_seed(seed)
    # prompt_speech_16k = postprocess(load_wav(prompt_wav, prompt_sr))
    # for i in cosyvoice.inference_instruct(tts_text, sft_dropdown, instruct_text, stream=stream, speed=speed):
    #     yield (cosyvoice.sample_rate, i['tts_speech'].numpy().flatten())
    for i in cosyvoice.inference_instruct3(tts_text, instruct_text, spk_id="loona", stream=stream, speed=speed):
        yield (cosyvoice.sample_rate, i['tts_speech'].numpy().flatten())

def main():
    with gr.Blocks() as demo:
        gr.Markdown("#### 请输入需要合成的文本，选择推理模式，并按照提示步骤进行操作")

        tts_text = gr.Textbox(label="输入合成文本", lines=1, value="Hi 我是loona")
        with gr.Row():
            mode_checkbox_group = gr.Radio(choices=inference_mode_list, label='选择推理模式', value=inference_mode_list[0])
            instruction_text = gr.Text(label="操作步骤", value=instruct_dict[inference_mode_list[0]], scale=0.5)
            sft_dropdown = gr.Dropdown(choices=sft_spk, label='选择预训练音色', value="loona" if len(sft_spk) != 0 else '', scale=0.25)
            stream = gr.Radio(choices=stream_mode_list, label='是否流式推理', value=stream_mode_list[0][1])
            speed = gr.Number(value=1, label="速度调节(仅支持非流式推理)", minimum=0.5, maximum=2.0, step=0.1)
            with gr.Column(scale=0.25):
                seed_button = gr.Button(value="\U0001F3B2")
                seed = gr.Number(value=0, label="随机推理种子")
                # print(seed)

        # with gr.Row():
        #     prompt_wav_upload = gr.Audio(sources='upload', type='filepath', label='选择prompt音频文件，注意采样率不低于16khz')
        #     prompt_wav_record = gr.Audio(sources='microphone', type='filepath', label='录制prompt音频文件')
        # prompt_text = gr.Textbox(label="输入prompt文本", lines=1, placeholder="请输入prompt文本，需与prompt音频内容一致，暂时不支持自动识别...", value='')
        instruct_text = gr.Textbox(label="输入instruct文本", lines=1, placeholder="你能用5岁天真儿童的语气说吗?", value="你能用5岁天真儿童的语气说吗?")

        generate_button = gr.Button("生成音频")

        audio_output = gr.Audio(label="合成音频", autoplay=True, streaming=True)

        seed_button.click(generate_seed, inputs=[], outputs=seed)
        prompt_text = None
        prompt_wav_upload = None
        prompt_wav_record = None
        # seed = 0
        generate_button.click(generate_audio,
                              inputs=[tts_text, mode_checkbox_group, instruct_text,
                                      seed, stream, speed],
                              outputs=[audio_output])
        mode_checkbox_group.change(fn=change_instruction, inputs=[mode_checkbox_group], outputs=[instruction_text])
    demo.queue(max_size=4)
    demo.launch(server_name='0.0.0.0', server_port=args.port, share=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port',
                        type=int,
                        default=7050)
    parser.add_argument('--model_dir',
                        type=str,
                        default='pretrained_models/CosyVoice2-0.5B',
                        help='local path or modelscope repo id')
    args = parser.parse_args()
    cosyvoice = CosyVoice2(args.model_dir) if 'CosyVoice2' in args.model_dir else CosyVoice(args.model_dir)
    sft_spk = cosyvoice.list_available_spks()
    prompt_sr = 16000
    default_data = np.zeros(cosyvoice.sample_rate)
    main()
