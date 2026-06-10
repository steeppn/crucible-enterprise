import os
import json
import asyncio
import logging
import websockets
from typing import AsyncGenerator, Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crucible.voice")

class VoiceLiveClient:
    """Voice Live API client for STT (speech-to-text) and TTS (text-to-speech).

    Connects to the Voice Live WebSocket endpoint for real-time transcription
    and neural voice synthesis.

    STT Flow:
        1. Connect to WebSocket endpoint
        2. Send audio chunks (PCM 16kHz mono)
        3. Receive incremental transcription results
        4. Receive final transcription when silence detected

    TTS Flow:
        1. Send text to synthesize
        2. Receive audio chunks (PCM)
        3. Play or forward audio to client
    """

    def __init__(self):
        self.stt_endpoint = os.getenv("VOICE_LIVE_STT_ENDPOINT", "wss://voice-live.example.com/stt")
        self.tts_endpoint = os.getenv("VOICE_LIVE_TTS_ENDPOINT", "wss://voice-live.example.com/tts")
        self.api_key = os.getenv("VOICE_LIVE_API_KEY", "")
        self.stt_ws = None
        self.tts_ws = None

    async def connect_stt(self) -> bool:
        """Connect to the STT WebSocket endpoint."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.stt_ws = await websockets.connect(self.stt_endpoint, extra_headers=headers)

            config = {
                "config": {
                    "sample_rate": 16000,
                    "channels": 1,
                    "format": "PCM_16",
                    "language": "en-US",
                    "interim_results": True,
                    "model": "mai-transcribe-1"
                }
            }
            await self.stt_ws.send(json.dumps(config))
            logger.info("STT WebSocket connected")
            return True
        except Exception as e:
            logger.error(f"STT connection failed: {e}")
            return False

    async def connect_tts(self, voice: str = "en-US-Neural-HD") -> bool:
        """Connect to the TTS WebSocket endpoint."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.tts_ws = await websockets.connect(self.tts_endpoint, extra_headers=headers)

            config = {
                "config": {
                    "voice": voice,
                    "sample_rate": 24000,
                    "format": "PCM_16",
                    "model": "neural-hd-voice"
                }
            }
            await self.tts_ws.send(json.dumps(config))
            logger.info(f"TTS WebSocket connected with voice: {voice}")
            return True
        except Exception as e:
            logger.error(f"TTS connection failed: {e}")
            return False

    async def stream_audio(self, audio_chunk: bytes) -> Optional[str]:
        """Send an audio chunk and return interim transcription if available."""
        if not self.stt_ws:
            return None

        try:
            await self.stt_ws.send(audio_chunk)
            response = await asyncio.wait_for(self.stt_ws.recv(), timeout=5.0)
            result = json.loads(response)

            if result.get("type") == "transcript":
                return result.get("text", "")
            elif result.get("type") == "interim":
                return result.get("text", "")
            return None
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"STT stream error: {e}")
            return None

    async def synthesize(self, text: str) -> AsyncGenerator[bytes, None]:
        """Send text for synthesis and yield audio chunks."""
        if not self.tts_ws:
            return

        try:
            await self.tts_ws.send(json.dumps({"text": text}))

            while True:
                response = await asyncio.wait_for(self.tts_ws.recv(), timeout=10.0)

                if isinstance(response, bytes):
                    yield response
                else:
                    result = json.loads(response)
                    if result.get("type") == "complete":
                        break
                    elif result.get("type") == "error":
                        logger.error(f"TTS error: {result.get('detail')}")
                        break
        except asyncio.TimeoutError:
            logger.warning("TTS synthesis timeout")
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")

    async def transcribe_file(self, audio_path: str) -> str:
        """Transcribe a complete audio file (for testing/batch mode)."""
        if not await self.connect_stt():
            return "STT connection failed"

        try:
            with open(audio_path, "rb") as f:
                audio_data = f.read()

            chunk_size = 3200
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                await self.stt_ws.send(chunk)
                await asyncio.sleep(0.05)

            await self.stt_ws.send(json.dumps({"type": "end_of_stream"}))

            final_text = ""
            while True:
                response = await asyncio.wait_for(self.stt_ws.recv(), timeout=10.0)
                result = json.loads(response)
                if result.get("type") == "final":
                    final_text = result.get("text", "")
                    break
                elif result.get("type") == "transcript":
                    final_text = result.get("text", "")

            return final_text
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return f"Error: {e}"
        finally:
            await self.close()

    async def close(self):
        """Close all WebSocket connections."""
        if self.stt_ws:
            await self.stt_ws.close()
            self.stt_ws = None
        if self.tts_ws:
            await self.tts_ws.close()
            self.tts_ws = None
        logger.info("Voice Live connections closed")
