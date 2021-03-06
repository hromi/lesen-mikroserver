import wave,sys
from io import BytesIO

import ffmpeg
import numpy as np
from deepspeech import Model


def normalize_audio(audio):
    out, err = (
        #ffmpeg.input("pipe:0")
        ffmpeg.input(audio)
        .output(
            "pipe:1",
            f="WAV",
            acodec="pcm_s16le",
            ac=1,
            ar="16k",
            loglevel="error",
            hide_banner=None,
        )
        #.run(input=audio, capture_stdout=True, capture_stderr=True)
        .run(capture_stdout=True)
    )
    if err:
        raise Exception(err)
    return out


class SpeechToTextEngine:
    def __init__(self, model_path, scorer_path):
        self.model = Model(model_path)
        self.model.enableExternalScorer(scorer_path)

    def run(self, audio):
        audio = normalize_audio(audio)
        audio = BytesIO(audio)
        with wave.Wave_read(audio) as wav:
            audio = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)
        result = self.model.stt(audio)
        return result



stt=SpeechToTextEngine(sys.argv[1],sys.argv[2])

for wav in sys.stdin:
    prediction=stt.run(wav.rstrip('\n'))
    print(prediction,wav)
