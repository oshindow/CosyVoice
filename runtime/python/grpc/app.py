from fastapi import FastAPI, Query
from fastapi.responses import Response, StreamingResponse
import grpc
import cosyvoice_pb2
import cosyvoice_pb2_grpc
import logging
import torch
import argparse
import torchaudio
# from cosyvoice.utils.file_utils import load_wav
import numpy as np
from pydantic import BaseModel
app = FastAPI()
import os

GRPC_SERVER = os.environ.get("GRPC_SERVER", "localhost:50000")


class SynthesizeRequest(BaseModel):
    tts_text: str
    # mode: str
    spk_id: str = None
    # prompt_text: str = None
    # prompt_audio: str = None
    instruct_text: str = None
    
def load_wav(wav, target_sr):
    speech, sample_rate = torchaudio.load(wav)
    speech = speech.mean(dim=0, keepdim=True)
    if sample_rate != target_sr:
        assert sample_rate > target_sr, 'wav sample rate {} must be greater than {}'.format(sample_rate, target_sr)
        speech = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)(speech)
    return speech

def get_speech_audio(tts_text, spk_id,  instruct_text):
    with grpc.insecure_channel(GRPC_SERVER) as channel:
        stub = cosyvoice_pb2_grpc.CosyVoiceStub(channel)
        request = cosyvoice_pb2.Request()
        
        logging.info('send instruct request')
        instruct_request = cosyvoice_pb2.instructRequest()
        instruct_request.tts_text = tts_text
        instruct_request.spk_id = spk_id
        instruct_request.instruct_text = instruct_text
        # prompt_speech = load_wav(prompt_audio, 16000)
        # instruct_request.prompt_audio = (prompt_speech.numpy() * (2**15)).astype(np.int16).tobytes()
        # instruct_request.prompt_text = prompt_text
        request.instruct_request.CopyFrom(instruct_request)

        response = stub.Inference(request)
        tts_audio = b''
        for r in response:
            tts_audio += r.tts_audio
        
        return tts_audio

@app.post("/synthesize_audio")
async def synthesize_audio(request: SynthesizeRequest):
    audio_data = get_speech_audio(
        request.tts_text,
    
        request.spk_id,
        # request.prompt_text,
        # request.prompt_audio,
        request.instruct_text
    )
    return Response(content=audio_data, media_type="audio/wav")


@app.post("/stream_audio")
def stream_audio(request: SynthesizeRequest):
    def grpc_generator(input_request):
        with grpc.insecure_channel(GRPC_SERVER) as channel:
            stub = cosyvoice_pb2_grpc.CosyVoiceStub(channel)
            request = cosyvoice_pb2.Request()
            
            logging.info('send instruct request')
            instruct_request = cosyvoice_pb2.instructRequest()
            instruct_request.tts_text = input_request.tts_text
            instruct_request.spk_id = input_request.spk_id
            instruct_request.instruct_text = input_request.instruct_text
            # prompt_speech = load_wav(prompt_audio, 16000)
            # instruct_request.prompt_audio = (prompt_speech.numpy() * (2**15)).astype(np.int16).tobytes()
            # instruct_request.prompt_text = prompt_text
            request.instruct_request.CopyFrom(instruct_request)

            for response in stub.Inference(request):
                yield response.tts_audio # bytes

    return StreamingResponse(grpc_generator(request), media_type="audio/wav")