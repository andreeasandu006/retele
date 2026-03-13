import socket
import threading
import pickle
import io

HOST = "127.0.0.1"  
PORT = 3333  
BUFFER_SIZE = 1024 # Am mărit buffer-ul pentru a suporta LIST

class Response:
  def __init__(self, payload):
    self.payload = payload

class Request:
  def __init__(self, command, key, resource=None):
    self.command = command
    self.key = key
    self.resource = resource

class State:
  def __init__(self):
    self.resources = {}
    self.lock = threading.Lock()

  def add(self, key, resource):
    with self.lock:
      self.resources[key] = resource
      return "OK - record add"

  def get(self, key):
    with self.lock:
      return self.resources.get(key)

  def remove(self, key):
    with self.lock:
      if key in self.resources:
        val = self.resources.pop(key)
        return f"OK {val} deleted"
      return "ERROR invalid key"

  def update(self, key, new_value):
    with self.lock:
      if key in self.resources:
        self.resources[key] = new_value
        return "Data updated"
      return "ERROR invalid key"

  def list_all(self):
    with self.lock:
      items = [f"{k}={v}" for k, v in self.resources.items()]
      return "DATA|" + ",".join(items)

  def count(self):
    with self.lock:
      return f"DATA {len(self.resources)}"

  def clear(self):
    with self.lock:
      self.resources.clear()
      return "all data deleted"

  def pop(self, key):
    with self.lock:
      if key in self.resources:
        val = self.resources.pop(key)
        return f"DATA {val}"
      return "ERROR invalid key"

state = State()

def process_command(data):
  try:
    payload = data[1:]
    stream = io.BytesIO(payload)  
    request = pickle.load(stream)
    
    response_text = "ERROR command not recognized" 
    cmd = request.command.upper() # 

    if cmd == 'ADD':
      response_text = state.add(request.key, request.resource)
    elif cmd == 'GET':
      val = state.get(request.key)
      response_text = f"DATA {val}" if val else "ERROR invalid key"
    elif cmd == 'REMOVE':
      response_text = state.remove(request.key)
    elif cmd == 'UPDATE':
      response_text = state.update(request.key, request.resource)
    elif cmd == 'LIST':
      response_text = state.list_all()
    elif cmd == 'COUNT':
      response_text = state.count()
    elif cmd == 'CLEAR':
      response_text = state.clear()
    elif cmd == 'POP':
      response_text = state.pop(request.key)
    elif cmd == 'QUIT':
      response_text = "Shutting down..."

    stream = io.BytesIO()
    pickle.dump(Response(response_text), stream)
    serialized_payload = stream.getvalue()
    payload_length = len(serialized_payload) + 1
    return payload_length.to_bytes(1, byteorder='big') + serialized_payload
  except Exception as e:
    return b'\x00' # Eroare generică

def handle_client(client):
  with client:
    while True:
      data = client.recv(BUFFER_SIZE)
      if not data: break
      
      message_length = data[0]
      full_data = data
      while len(full_data) < message_length:
        data = client.recv(BUFFER_SIZE)
        full_data += data
      
      response = process_command(full_data)
      client.send(response)

def main():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((HOST, PORT))
  server.listen()
  print(f"Server pornit pe {HOST}:{PORT}")
  try:
    while True:
      client, addr = server.accept()
      print(f"Conectat: {addr}")
      threading.Thread(target=handle_client, args=(client,)).start()
  finally:
    server.close()

if __name__ == '__main__':
  main()