import asyncio
import websockets
import pyaudio

async def audio_stream(websocket, path):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=22050, output=True)

    try:
        async for chunk in websocket:
            stream.write(chunk)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

start_server = websockets.serve(audio_stream, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()