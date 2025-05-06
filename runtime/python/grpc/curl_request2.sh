curl -X POST "http://localhost:8080/stream_audio" \
    -H "Content-Type: application/json" \
    -d '{
        "tts_text": "哇咔咔，哇咔咔，瓦库，瓦库，阿尼亚，马上要凑够一百字了！让我想想[breath]<strong>loona</strong>修复版本发布了[laughter]。",
        "spk_id": "fffr",
        "instruct_text": "高兴"
    }' --output output.pcm

sox -t raw -r 22050 -e signed -b 16 -c 1 output.pcm output.wav
