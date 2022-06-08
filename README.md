# lesen-mikroserver
LAN/WAN automatic speech recognition community server running inferences on NVIDIA Xavier Jetson. Client-server communication through websockets.

Runs correct inference in 0.5 sec for an al 

Client-side HTML/JS code to be implemented soon. 

# Benchmark 
Runs correct inference in 3 sec for 10-second WAV with a scorer containg ~ 300 class-sequences.

# Comments
speech recog based on Mozilla's deepspeech

ultra-neat, sanic-based super-fast server is based on https://github.com/coqui-ai/STT-examples/tree/r1.0/python_websocket_server

delegation to Xavier Jetson CUDA / GPU works only when You install the appropriate build from https://github.com/domcross/DeepSpeech-for-Jetson-Nano/releases/

(You will also find the wheel You need in wheels subdirectory, install it with ```pip3 install wheels/deepspeech-0.9.0-cp36-cp36m-linux_aarch64.whl```))

# scorers/
The real stuff begins when You start experimenting with language models / scorers. 

The "added value" of lesen-mikroserver project (as compared to Coqui or Deepspeech) is that You can route Your requests to different scorers stored in ```scorer_dir```.

Use KenLM to create them and deepspeech scorer creation pipeline to create them.


# server-HOWTO
Setup Your server in coqui-server/application.conf.

enter the coqui-server directory and run

```python3.6 app.py```

(Note: You can easily "daemonize" Your newly born ASR system by running it in a tmux session)

# websocket API
For every recognition act, You open a websocket to sanic route

```/stt/<scorer>````

whereby the ```<scorer>``` parameter needs to be the same as the basename of Your .scorer file stored in ```scorer_dir```.

Example: You have a language model for numeric expressions stored in ```/scorers/numbers.scorer``` whereby ```scorers``` is Your ```scorer_dir```. You have to establish websocket to route ```/stt/numbers```.

# client-HOWTO
Enter the client directory, install all necessary requirements (```pip3.6 -r requirements.txt install```)* and and run something like

```python3.6 client.py 127.0.0.1 WAVE_FILE_HERE.wav```

* note that client.py needs pipinstalled websocket-client and not websocket library to run properly.

If You have necessary skills it is highly probably that You are just started an ASR system You always dreamed about. 

Go buy Yourself a beer.

# Acknowledgments & further support
Glory to Ukraine, gerojom slava.

When in doubt, RTFM.

