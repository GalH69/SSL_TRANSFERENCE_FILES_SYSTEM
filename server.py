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
                        file_name = conn.recv(1024).decode().strip()
                        
                        if not file_name.strip():
                            conn.sendall(b"illegal")
                        else:
                            conn.sendall(b"Good name!")
                            break
                        
                    target_file_name = f"received_{file_name}"
                    with open(target_file_name, "wb") as rf:
                        # buffer = b""
                        # while True:
                        #     chunk = conn.recv(1024)
                        #     if not chunk:
                        #         break
                        #     buffer += chunk
                        #     if b"__END__\n" in buffer:
                        #         parts = buffer.split(b"__END__\n", 1)
                        #         rf.write(parts[0])
                        #         break
                        file_size_bytes = conn.recv(4)
                        file_size = int.from_bytes(file_size_bytes, byteorder='big')

                        received = 0
                        with open(target_file_name, "wb") as rf:
                            while received < file_size:
                                chunk = conn.recv(min(1024, file_size - received))
                                if not chunk:
                                    break
                                rf.write(chunk)
                                received += len(chunk)
                        
                        
                    
                    try:
                        shutil.move(target_file_name, folder)
                        conn.sendall(b"Success! the file was uploaded!\n")
                    except Exception as e:
                        conn.sendall(b"Failed to move file\n")
                
                elif operation == "download":
                    conn.sendall(b"\npick a file for download from the following files:\n")

                    files = os.listdir(folder)
                    files_str = "\n".join(files)
                    conn.sendall(files_str.encode())
                    
                    file_name = conn.recv(1024).decode()
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