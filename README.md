# lesen-mikroserver
LAN/WAN automatic speech recognition community server running inferences on NVIDIA Xavier Jetson. Client-server communication through websockets.

Runs correct inference in 0.5 sec for an almost 2-second WAV 

Client-side HTML/JS code to be implemented soon. 

# Benchmark 
Runs correct inference in 0.5 sec for an almost 2-second WAV with a scorer containg ~ 300 class-sequences.

# Comments

based around wonderful coqui-stt ( https://github.com/coqui-ai/STT/ )

uses python3.6

if You want to also train the model (and not only use a pre-trained model), make sure You have a correct version installed from this repository (when in doubt, use ```apt-cache show nvidia-jetpack``` to find out Your nvidia-jetpack version) 

tflite-runtime wheel is archived from https://google-coral.github.io/py-repo/tflite-runtime/ , it seems it is able to delegate inferences onto Xavier's Teslacores (c.f.benchmark info above) 

note that client.py needs pipinstalled websocket-client and not websocket library to run properly

# scorers/
The real stuff begins when You start experimenting with scorers. Use KenLM to create them and deepspeech scorer creation pipeline to create them.

de_bothLexicons.scorer user canonic list of substantives/verbs used in fibel.digital project (c.f. https://fibel.digital/kleinesLexicon )
