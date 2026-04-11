import io
import math
import wave


class LocalTTSProvider:
    def synthesize(self, text: str, audio_format: str) -> bytes:
        # Local deterministic wav generation used for development-phase modality plumbing.
        sample_rate = 16000
        duration_seconds = max(1, min(6, len(text) // 80 + 1))
        frames = int(sample_rate * duration_seconds)
        frequency = 440.0
        amplitude = 12000

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for i in range(frames):
                value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                wav_file.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))

        return buffer.getvalue()

