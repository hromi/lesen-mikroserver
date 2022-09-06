import os,time,wave
from io import BytesIO

import ffmpeg
import numpy as np
from deepspeech import Model

from sanic.log import logger
def normalize_audio(audio,outfile):
    logger.debug("NORM")
    logger.debug(outfile)
    try:
        out, err = (
            ffmpeg.input("pipe:0")
            .output(
                outfile,
                f="WAV",
                acodec="pcm_s16le",
                ac=1,
                ar="16k",
                loglevel="error",
                hide_banner=None,
            )
            #.run(input=audio, capture_stdout=True, capture_stderr=True)
            .run(input=audio, capture_stdout=True)
            #.run(input=audio)
        )
    except ffmpeg.Error as e:
        logger.debug(e.stdout)
        logger.debug(e.stderr)

    #logger.debug("WTF")
    if err:
        logger.debug(err)
        print(er)
        raise Exception(err)
    return out


class SpeechToTextEngine:
    def __init__(self, model_path, scorer_path):
        self.model = Model(model_path)
        #self.model.enableExternalScorer(scorer_path)

    def run(self, audio, scorer="", token="", hmpl=""):
        if (hmpl):
            if not os.path.isdir(hmpl):
               from pathlib import Path
               Path(hmpl).mkdir(parents=True, exist_ok=True)
            f = hmpl+token+"-"+str(time.time())+".wav"
        else:
            f = "/tmp/"+str(time.time())+".wav"
        try:
            audio = normalize_audio(audio,f)
        except:
            logger.debug("EXCEPT") 
        #with wave.Wave_read(/audio) as wav:
        with wave.Wave_read(f) as wav:
            logger.debug(str(wav.getnframes())+"FRAMES")
            audio = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)
        if (scorer):
            self.model.enableExternalScorer(scorer)
        try:
            result = self.model.stt(audio)
        except BaseException as err:
            #print("OH WEYA"+e)
            raise
        return f,result

