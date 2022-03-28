# lesen-mikroserver
LAN/WAN automatic speech recognition community server running inferences on NVIDIA Xavier Jetson. Client-server communication through websockets.

##Comments
uses python3.6

if You want to also train the model (and not only use a pre-trained model), make sure You have a correct version installed from this repository (when in doubt, use ```apt-cache show nvidia-jetpack``` to find out Your nvidia-jetpack version) 

tflite-runtime wheel is archived from https://google-coral.github.io/py-repo/tflite-runtime/ , haven't tested yet whether it is able to delegate inferences onto Xavier's Teslacores

note that client.py needs pipinstalled websocket-client and not websocket library to run properly


