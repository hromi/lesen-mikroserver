import json,os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter

from pyhocon import ConfigFactory
from sanic import Sanic, response
from sanic.log import logger

from stt_server.engine import SpeechToTextEngine
from stt_server.models import Response, Error
from os.path import exists
from re import match
import subprocess

# Load app configs and initialize STT model
conf = ConfigFactory.parse_file("application.conf")
engine = SpeechToTextEngine(
    model_path=Path(conf["stt.model"]).absolute().as_posix(),
    scorer_path=Path(conf["stt.default_scorer"]).absolute().as_posix(),
)

# Initialze Sanic and ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=conf["server.threadpool.count"])
app = Sanic("stt_server")


@app.route("/", methods=["GET"])
async def healthcheck(_):
    return response.text("Welcome to STT Server!")


@app.websocket("/hmpl/<scorer>/<token>/<voice>/<iteration>/<phase>/<feedback>")
async def hmpl(request, ws, scorer, token, voice, iteration, phase, feedback):
    token=token.lower()
    scorer="22078"
    logger.debug(voice+" "+token+" PHASE "+phase)
    scorer_file=conf["stt.scorer_dir"]+scorer+".scorer"
    #logger.debug("SCORER"+scorer_file)
    #if not exists(scorer_file):
    #    logger.debug(scorer_file+" does not exist");
    #    if match("^\d+$",scorer):
    #        logger.debug("scorer id numeric. executing"+conf["utils.scorer_creator"])
    #        subprocess.run([conf["utils.scorer_creator"],scorer])
    #logger.debug(f"Received {request.method} request at {request.path}")
    try:
        audio = await ws.recv()
        inference_start = perf_counter()
        datadir=conf["hmpl.data_dir"]+voice+'/'+phase+'/'
        #try:


        f,text = await app.loop.run_in_executor(executor, lambda: engine.run(audio,scorer_file,token,datadir))
        #except:
        #    1
        #text = await app.loop.run_in_executor(executor, lambda: engine.run(audio))
        #logger.debug(engine.model._impl)
        inference_end = perf_counter() - inference_start
        await ws.send(json.dumps(Response(text, inference_end).__dict__,ensure_ascii=False))
        logger.debug(f"Completed {request.method} request at {request.path} in {inference_end} seconds")
        
        feedback_prefix='feedback_' if feedback=='ON' else ''
        
        if token==text:
          csv=open(datadir+feedback_prefix+'same.'+iteration+'.csv','a')
        else:
          csv=open(datadir+feedback_prefix+'different.'+iteration+'.csv','a')

        all_file=datadir+feedback_prefix+'all.'+iteration+'.csv'

        if not exists(all_file):
          csv_all=open(all_file,'w')
          csv_all.write('"wav_filename","wav_filesize","transcript","prediction"\n')
        else:
          csv_all=open(all_file,'a')

        csv_all.write('"'+f+'",'+str(os.stat(f).st_size)+',"'+token+'","'+text+'"\n')
        csv.write('"'+f+'",'+str(os.stat(f).st_size)+',"'+token+'","'+text+'"\n')

        csv.close()
    except Exception as e:  # pylint: disable=broad-except
        logger.debug(f"Failed to process {request.method} request at {request.path}. The exception is: {str(e)}.")
        await ws.send(json.dumps(Error("Something went wrong").__dict__))
    await ws.close()


@app.websocket("/stt/<scorer>/<token>")
async def stt(request, ws, scorer, token):
    scorer_file=conf["stt.scorer_dir"]+scorer+".scorer"
    #logger.debug("SCORER"+scorer_file)
    if not exists(scorer_file):
        logger.debug(scorer_file+" does not exist");
        if match("^\d+$",scorer):
            logger.debug("scorer id numeric. executing"+conf["utils.scorer_creator"])
            subprocess.run([conf["utils.scorer_creator"],scorer])
    logger.debug(f"Received {request.method} request at {request.path}")
    try:
        audio = await ws.recv()
        inference_start = perf_counter()
        try:
            f,text = await app.loop.run_in_executor(executor, lambda: engine.run(audio,scorer_file,token))
        except:
            1
        #text = await app.loop.run_in_executor(executor, lambda: engine.run(audio))
        logger.debug(engine.model._impl)
        inference_end = perf_counter() - inference_start
        await ws.send(json.dumps(Response(text, inference_end).__dict__,ensure_ascii=False))
        logger.debug(f"Completed {request.method} request at {request.path} in {inference_end} seconds")
        logger.debug([f,text])
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
