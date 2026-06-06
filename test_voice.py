import asyncio
import logging

from araxon.ai.brain import ARAXONBrain
from araxon.voice.synthesizer import KokoroSynthesizer
from araxon.voice.audio_player import AudioPlayer

logging.basicConfig(level=logging.INFO)

async def main():
    brain = ARAXONBrain()
    await brain.warmup()

    user_prompt = "Hello, ARAXON. Please introduce yourself briefly for a test."
    print("User prompt:", user_prompt)
    response = await brain.think(user_prompt)
    print("ARAXON response:", response)

    synth = KokoroSynthesizer()
    audio = await synth.synthesize(response)

    player = AudioPlayer()
    player.begin_session(total_chunks=1)
    await player.enqueue(audio)

    playback_task = asyncio.create_task(player.start_playback_loop())
    await player.wait_until_idle()
    await player.stop()
    playback_task.cancel()

if __name__ == '__main__':
    asyncio.run(main())
