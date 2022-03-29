# lesen-mikroserver
LAN/WAN automatic speech recognition community server running inferences on NVIDIA Xavier Jetson. Client-server communication through websockets.

Runs correct inference in 0.5 sec for an almost 2-second WAV 

Client-side HTML/JS code to be implemented soon. 

# Benchmark 
Runs correct inference in 0.5 sec for an almost 2-second WAV with a scorer containg ~ 300 class-sequences.

# Comments
speech recog based around wonderful coqui-stt ( https://github.com/coqui-ai/STT/ )

ultra-neat, sanic-based super-fast server is based on https://github.com/coqui-ai/STT-examples/tree/r1.0/python_websocket_server

delegation to non-CPU processing units seems only to work when You install tflite_runtime from Google's Coral Repository: https://google-coral.github.io/py-repo/tflite-runtime/

(You will also find the python3.6 version of the tflite_runtime wheel in the wheels subdirectory)

# scorers/
The real stuff begins when You start experimenting with scorers. 

Use KenLM to create them and deepspeech scorer creation pipeline to create them.

de_bothLexicons.scorer user canonic list of substantives/verbs used in fibel.digital project (c.f. https://fibel.digital/kleinesLexicon )

# server-HOWTO
Setup Your server in coqui-server/application.conf.

enter the coqui-server directory and run
```python3.6 app.py```

(Note: You can easily "daemonize" Your newly born ASR system by running it in a tmux session)

# client-HOWTO
Enter the client directory, install all necessary requirements (```pip3.6 -r requirements.txt install```)* and and run something like

```python3.6 app.py 127.0.0.1 WAVE_FILE_HERE.wav```

* note that client.py needs pipinstalled websocket-client and not websocket library to run properly.

If You have necessary skills it is highly probably that You are just started an ASR system You always dreamed about. Go buy Yourself a beer.

# Acknowledgments & further support
Glory to Ukraine, gerojom slava.

When in doubt, RTFM.
