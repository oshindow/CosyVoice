curl -X POST "http://localhost:8081/stream_audio" \
    -H "Content-Type: application/json" \
    -d '{
        "tts_text": "让我想想[breath]<strong>loona</strong>修复版本发布了[laughter]。",
        "spk_id": "fffr",
        "instruct_text": "高兴"
    }' --output output.pcm

sox -t raw -r 22050 -e signed -b 16 -c 1 output.pcm output.wav
