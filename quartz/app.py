import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter

from pyhocon import ConfigFactory
from sanic import Sanic, response
from sanic.log import logger

import ffmpeg
#from stt_server.engine import SpeechToTextEngine
#from stt_server.models import Response, Error

import numpy as np
#import soundfile as sf
import tflite_runtime.interpreter as tflite


from io import BytesIO
import wave

from coqui_stt_ctcdecoder import Alphabet, Scorer, ctc_beam_search_decoder

# Load app configs and initialize STT model
conf = ConfigFactory.parse_file("application.conf")
#engine = SpeechToTextEngine(
model_path=Path(conf["mikroserver.model"]).absolute().as_posix()
#ds_scorer_path=Path(conf["mikroserver.scorer"]).absolute().as_posix()
alphabet_path=Path(conf["mikroserver.alphabet"]).absolute().as_posix()
ds_alphabet_path=Path(conf["mikroserver.ds_alphabet"]).absolute().as_posix()
#labels_path=Path(conf["mikroserver.labels"]).absolute().as_posix()

with open(alphabet_path, "r", encoding="utf-8") as file:
    alphabet = json.load(file)

def normalize_audio(audio):
    out, err = (
        ffmpeg.input("pipe:0")
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
        .run(input=audio, capture_stdout=True)
    )
    if err:
        raise Exception(err)
    return out


#ds_alphabet = Alphabet(Path(conf["mikroserver.ds_alphabet"]).absolute().as_posix())
ds_scorer = Scorer(
    alpha=conf["mikroserver.alpha"],
    beta=conf["mikroserver.beta"],
    scorer_path=Path(conf["mikroserver.scorer"]).absolute().as_posix(),
    alphabet=Alphabet(Path(conf["mikroserver.ds_alphabet"]).absolute().as_posix())
)

interpreter = tflite.Interpreter(model_path=model_path)

def predict(interpreter, audio):
    """Feed an audio signal with shape [1, len_signal] into the network and get the predictions"""

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Enable dynamic shape inputs
    interpreter.resize_tensor_input(input_details[0]["index"], audio.shape)
    interpreter.allocate_tensors()
    logger.debug("tensors allocated")
    # Feed audio
    interpreter.set_tensor(input_details[0]["index"], audio)
    logger.debug("tensors set")
    interpreter.invoke()
    logger.debug("tensors invoked")
    output_data = interpreter.get_tensor(output_details[0]["index"])
    return output_data

def get_predicted_text(prediction):
    """Decode the network's prediction with an additional language model"""
    global beam_size, ds_alphabet, ds_scorer

    ldecoded = ctc_beam_search_decoder(
        prediction.tolist(),
        alphabet=ds_alphabet,
        beam_size=beam_size,
        cutoff_prob=1.0,
        cutoff_top_n=512,
        scorer=ds_scorer,
        hot_words=dict(),
        num_results=1,
    )
    lm_text = ldecoded[0][1]
    return lm_text


#executor = ThreadPoolExecutor(max_workers=conf["server.threadpool.count"])
app = Sanic("lesen_mikroserver")


@app.route("/", methods=["GET"])
async def healthcheck(_):
    return response.text("Welcome to lesen-mikroserver!")


@app.websocket("/api/v1/stt")
async def stt(request, ws):
    logger.debug(f"Received {request.method} request at {request.path}")
    try:
        audio = await ws.recv()
        inference_start = perf_counter()
        audio = normalize_audio(audio)
        audio = BytesIO(audio)
        with wave.Wave_read(audio) as wav:
            audio = np.frombuffer(wav.readframes(wav.getnframes()), np.float32)
        logger.debug("running inference")
        prediction = predict(interpreter, audio)
        logger.debug("beam search")
        text=get_predicted_text(prediction[0])
        #text = await app.loop.run_in_executor(executor, lambda: engine.run(audio,"/home/user/Speech/lesen-mikroserver/scorers/zahlen.scorer"))
        #logger.debug(engine.model._impl)
        inference_end = perf_counter() - inference_start
        await ws.send(json.dumps(Response(text, inference_end).__dict__))
        logger.debug(f"Completed {request.method} request at {request.path} in {inference_end} seconds")
        logger.debug(text)
    except Exception as e:  # pylint: disable=broad-except
        logger.debug(f"Failed to process {request.method} request at {request.path}. The exception is: {str(e)}.")
        await ws.send(json.dumps(Error("Something went wrong").__dict__))
    await ws.close()


if __name__ == "__main__":
    app.run(
        host=conf["server.http.host"],
        port=conf["server.http.port"],
        ssl=dict(
            cert=conf["server.http.cert_path"],
            key=conf["server.http.key_path"]
        ),
        access_log=True,
        debug=True,
    )
