import socket
import shutil
import os
import ssl

HOST = "0.0.0.0"
PORT = 65432

base_dir = "D:\\python_programmers_clab\\SSL_transference_filses_system"
cert_pem = os.path.join(base_dir, "cert.pem")
key_pem = os.path.join(base_dir, "key.pem")


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=cert_pem, keyfile=key_pem)

folder = os.path.join(base_dir, "files_of_server_for_test")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    
    with context.wrap_socket(s, server_side=True) as secure_sock:
        
        conn, addr = secure_sock.accept()
        
        with conn:
            print(f"Got connection from {addr}\nthe connection is using TLS")
            
            while True:
                operation = conn.recv(1024).decode()
                
                if operation == "upload":
                    
                    while True:
                        
                        file_name = ""
                        while True:
                            char = conn.recv(1).decode()
                            if char == "\n":
                                break
                            file_name += char
                        file_name = file_name.strip()
                        
                        
                        if not file_name.strip():
                            conn.sendall(b"illegal")
                        else:
                            conn.sendall(b"Good name!")
                            break
                        
                    base_name = f"received_{file_name}"
                    target_file_name = os.path.join(folder, base_name)
                    i = 1
                    
                    while os.path.exists(target_file_name):
                        base_name = f"received_{i}_{file_name}"
                        target_file_name = os.path.join(folder,base_name)
                        i += 1
                    
                    
                    with open(target_file_name, "wb") as rf:

                        file_size_bytes = conn.recv(4)
                        file_size = int.from_bytes(file_size_bytes, byteorder='big')

                        


                        received = 0
                        while received < file_size:
                            chunk = conn.recv(min(1024, file_size - received))
                            if not chunk:
                                break
                            rf.write(chunk)
                            received += len(chunk)
                
                elif operation == "download":
                    conn.sendall(b"\npick a file for download from the following files:\n")

                    files = os.listdir(folder)
                    files_str = "\n".join(files)
                    conn.sendall(files_str.encode())
                    
                    file_name = conn.recv(1024).decode().strip()
                    file_path = os.path.join(folder, file_name)
                    
                    if not os.path.exists(file_path):
                        conn.sendall((0).to_bytes(4, byteorder='big'))
                        continue
                    
                    
                    file_size = os.path.getsize(file_path)
                    conn.sendall(file_size.to_bytes(4, byteorder='big'))
                    
                    with open(file_path, "rb") as f:
                        while True:
                            chunk = f.read(1024)
                            if not chunk:
                                break
                            conn.sendall(chunk)
                    conn.sendall(b"\nThe download was successful!\n")
                    
                elif operation == "exit":
                    print("The client has terminated the connection.")
                    break
                
                else:
                    print("operation not allowed")
        print("Disconnected")