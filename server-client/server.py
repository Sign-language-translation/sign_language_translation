import socket
import json
from multiprocessing import Pool
import struct
from predictor import classify_json_file

HOST = '0.0.0.0'
PORT = 5002
BUFFER_SIZE = 4096
MODEL_FILE_PATH = f'model-5_14000_vpw.keras'
LABEL_ENCODER_FILE_PATH = f'label_encoder_model-5_14000_vpw.pkl'

# Simulated model function (replace this with your real model)
def model_predict(json_data, MODEL_FILE_PATH, LABEL_ENCODER_FILE_PATH):
    # Simulate some processing (like model inference)
    return classify_json_file(json_data, MODEL_FILE_PATH, LABEL_ENCODER_FILE_PATH)

# Helper to receive an exact number of bytes
def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# Receive a list of JSONs from client
def receive_jsons(conn):
    # First 4 bytes: number of JSONs (as integer)
    count_data = recvall(conn, 4)
    num_jsons = struct.unpack('!I', count_data)[0]

    json_list = []
    for _ in range(num_jsons):
        # Next 4 bytes: length of JSON string
        length_data = recvall(conn, 4)
        json_len = struct.unpack('!I', length_data)[0]

        # Receive the JSON string
        json_bytes = recvall(conn, json_len)
        json_obj = json.loads(json_bytes.decode('utf-8'))
        json_list.append(json_obj)

    return json_list

def handle_client(conn):
    try:
        json_list = receive_jsons(conn)
        print(f"Received {len(json_list)} JSON objects.")

        with Pool() as pool:
            results = pool.map(model_predict, json_list)

        response = json.dumps(results).encode('utf-8')
        conn.sendall(struct.pack('!I', len(response)))  # send response length
        conn.sendall(response)
        print("Sent results to client.")

    except Exception as e:
        print("Error:", e)
        conn.sendall(b"Error")
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            handle_client(conn)

if __name__ == "__main__":
    start_server()
