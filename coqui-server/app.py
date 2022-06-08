import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter

from pyhocon import ConfigFactory
from sanic import Sanic, response
from sanic.log import logger

from stt_server.engine import SpeechToTextEngine
from stt_server.models import Response, Error

# Load app configs and initialize STT model
conf = ConfigFactory.parse_file("application.conf")
engine = SpeechToTextEngine(
    model_path=Path(conf["stt.model"]).absolute().as_posix(),
    scorer_path=Path(conf["stt.scorer"]).absolute().as_posix(),
)

# Initialze Sanic and ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=conf["server.threadpool.count"])
app = Sanic("stt_server")


@app.route("/", methods=["GET"])
async def healthcheck(_):
    return response.text("Welcome to STT Server!")


@app.websocket("/stt/<scorer>")
async def stt(request, ws, scorer):
    scorer_file=conf["stt.scorer_dir"]+scorer+".scorer"
    #logger.debug("SCORER"+scorer_file)
    logger.debug(f"Received {request.method} request at {request.path}")
    try:
        audio = await ws.recv()
        inference_start = perf_counter()
        text = await app.loop.run_in_executor(executor, lambda: engine.run(audio,scorer_file))
        #text = await app.loop.run_in_executor(executor, lambda: engine.run(audio))
        logger.debug(engine.model._impl)
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
