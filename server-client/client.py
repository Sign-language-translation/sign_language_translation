import socket
import json
import struct

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5002

def load_jsons_from_files(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

        # Ensure both are lists of JSON objects
        if not isinstance(data1, list):
            data1 = [data1]
        if not isinstance(data2, list):
            data2 = [data2]
        
        return data1 + data2  # Combine them

def send_jsons(json_list):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))

        # Send number of JSONs (4 bytes)
        s.sendall(struct.pack('!I', len(json_list)))

        for obj in json_list:
            json_str = json.dumps(obj).encode('utf-8')
            s.sendall(struct.pack('!I', len(json_str)))  # length of this JSON
            s.sendall(json_str)

        # Get response length
        response_len_bytes = s.recv(4)
        response_len = struct.unpack('!I', response_len_bytes)[0]
        response_data = b''
        while len(response_data) < response_len:
            packet = s.recv(4096)
            if not packet:
                break
            response_data += packet

        results = json.loads(response_data.decode('utf-8'))
        print("Server Results:")
        for r in results:
            print(r)

if __name__ == "__main__":
    json_list = load_jsons_from_files('3a5a019e-c54a-4a24-ac7d-ac519984dcff_go.json', '78f9a12a-df1f-4b47-94a5-f0849a5c9b5c_go_fresh.json')
    send_jsons(json_list)