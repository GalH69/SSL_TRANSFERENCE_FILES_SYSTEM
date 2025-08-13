import socket
import os
import ssl

def send_with_length(sock, data_bytes):
    sock.sendall(len(data_bytes).to_bytes(4, byteorder='big'))
    sock.sendall(data_bytes)

def recv_with_length(sock):
    length_bytes = sock.recv(4)
    length = int.from_bytes(length_bytes, byteorder='big')
    received = b""
    while len(received) < length:
        chunk = sock.recv(min(1024, length - len(received)))
        if not chunk:
            break
        received += chunk
    return received

HOST = input("Enter the IP address of the device you want to connect to:    ") # תכתוב את הכתובת איי פי של המחשב שאתה רוצה שיהיה השרת
PORT = 65432

# context = ssl.create_default_context()
# context.check_hostname = False # עושה שלא שהלקוח לא יאמת את השם של השרת עם רשות האישורים
# context.verify_mode = ssl.CERT_NONE # עושה שהלקוח לא יאמת את התעודה עם רשות האישורים

context = ssl._create_unverified_context()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    with context.wrap_socket(s, server_hostname="anything") as secure_sock:
        
        secure_sock.connect((HOST, PORT))
        while True:

            operation = input("Enter download to downloading a file from the server\nEnter upload for uploading a file to the server\nEnter exit to quit\n")
            
            if operation == "upload":
                secure_sock.sendall(b"upload")
                
                file_name = input("Enter file name, make sure to include the file extension: ")
                folder_path = input("Enter the path of the folder where the file is located:    ")                
                full_path = os.path.join(folder_path, file_name)
                
                while  not os.path.isfile(full_path):
                    print("\nPath illegal!\nEnter a path of a the file you want to upload")
                    full_path = input("Try again, Enter file path you want to upload: ")

                
                if os.path.exists(full_path):

                    secure_sock.sendall((file_name.strip() + "\n").encode())
                    feedback = secure_sock.recv(1024).decode()
                    
                    while feedback == "illegal":
                        file_name = input("Illegal name\nEnter file name:   ").strip()
                        secure_sock.sendall((file_name + "\n").encode())
                        feedback = secure_sock.recv(1024).decode()
                    
                    try:
                        with open(full_path, "rb") as f:
                            data = f.read()
                    except Exception as e:
                        print(f"[ERROR] Failed to open or read file: {e}")
                        secure_sock.sendall((0).to_bytes(4, byteorder='big'))  # שלח לשרת אורך אפס
                        feedback = secure_sock.recv(1024).decode()
                        print(feedback)
                        continue
                    
                    file_size = len(data)
                    secure_sock.sendall(file_size.to_bytes(4, byteorder='big'))
                    secure_sock.sendall(data)
                    
                    
                    feedback = secure_sock.recv(1024).decode()
                    print(feedback)

                else:
                    print("you enter a file that does not exist\n")
            
            elif operation == "download":
                secure_sock.sendall(b"download")
                
                
                
                feedback = secure_sock.recv(1024).decode()
                print(feedback)
                
                files_str = recv_with_length(secure_sock).decode()
                
                files_lst = files_str.split("\n")
                
                print(f"{files_str}\n")
                
                chosen_file_name = input()
                found = chosen_file_name in files_lst
                
                while not found:
                    
                    print("Failed! you pick file which does not exist")
                    print("pick the file from this list:")
                    print(f"{files_str}\n") 
                    
                    chosen_file_name = input()
                    found = chosen_file_name in files_lst
                    
                dl_file_path = input("\nEnter location for the file:")
                file_name = input(f"\nEnter name for the file\nNote: this is the name of the file you pick:   {chosen_file_name}\n")
                full_path = os.path.join(dl_file_path, file_name)
                
                secure_sock.sendall(chosen_file_name.encode())
                
                
                # file_size_bytes = secure_sock.recv(4)
                # file_size = int.from_bytes(file_size_bytes, byteorder='big')
                
                # if file_size == 0:
                #     print("Server reports: file does not exist.")
                #     continue

                # received = 0
                # with open(full_path, "wb") as f:
                #     while received < file_size:
                #         chunk = secure_sock.recv(min(1024, file_size - received))
                #         if not chunk:
                #             break
                #         f.write(chunk)
                #         received += len(chunk)
                
                file_data = recv_with_length(secure_sock)

                if not file_data:
                    print("Server reports: file does not exist.")
                    continue

                with open(full_path, "wb") as f:
                    f.write(file_data)
                
                print(recv_with_length(secure_sock).decode())
                
                
            elif operation == "exit":
                secure_sock.sendall(b"exit")
                break
            
            else:
                print("your operation is not allow")

print("Disconnected")