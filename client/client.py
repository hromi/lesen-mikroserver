import websocket,sys
    
ws = websocket.WebSocket()
ws.connect("wss://"+sys.argv[1]+":12345/stt/numbers")

with open(sys.argv[2], mode='rb') as file:  # b is important -> binary
    audio = file.read()
    ws.send_binary(audio)
    result =  ws.recv()
    print(result) 

