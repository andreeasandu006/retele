import socket
import pickle
import io

HOST = "127.0.0.1"  
PORT = 3333  
BUFFER_SIZE = 1024

class Response:
  def __init__(self, payload):
    self.payload = payload

class Request:
  def __init__(self, command, key, resource=None):
    self.command = command
    self.key = key
    self.resource = resource

def get_command(command_input):
    parts = command_input.strip().split(' ', 2)
    cmd = parts[0]
    key = parts[1] if len(parts) > 1 else ""
    res = parts[2] if len(parts) > 2 else ""
    
    request = Request(cmd, key, res)
    stream = io.BytesIO()
    pickle.dump(request, stream)
    serialized = stream.getvalue()
    return (len(serialized) + 1).to_bytes(1, byteorder='big') + serialized

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Comenzi disponibile: ADD, GET, REMOVE, LIST, COUNT, CLEAR, UPDATE, POP, QUIT")
    while True:
        command = input('connected>')
        if not command: continue
        
        s.send(get_command(command))
        
        if command.upper() == 'QUIT': # 
            break
            
        data = s.recv(BUFFER_SIZE)
        if not data: break
        
        message_length = data[0]
        full_data = data
        while len(full_data) < message_length:
            data = s.recv(BUFFER_SIZE)
            full_data += data
            
        stream = io.BytesIO(full_data[1:])  
        response = pickle.load(stream)
        print(response.payload)