import socket, os

# Create a socket and bind it to IP address '127.0.0.1' and port '8080'
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('127.0.0.1', 8080))
socket.listen(5)

def get_details(str):
    # Split the string by 'GET ' and take the second element, then split again by ' '
    # and take the first element to get the file name
    file_name = str.split('GET ', 1)[1].split()[0]
    
    # Split the string by 'Connection: ' and take the second element, then split again by '\r\n'
    # and take the first element to get the connection status
    con_status = str.split('Connection: ', 1)[1].split('\r\n')[0]

    if file_name == '/':
        file_name = '/index.html'

    # Return the file name with the leading '/' removed and the connection status
    return file_name[1:], con_status

def get_file_content(path):
    # If the file does not exist or is not a file, return None and False
    if not os.path.exists(path) or not os.path.isfile(path):
        return None, False

    content, is_binary = None, False
    
    # If the file path ends with 'jpg' or 'ico', read the file as binary
    if path.endswith('jpg') or path.endswith('ico'):
        with open(path, 'rb') as file:
            content = file.read()
        is_binary = True
        
    # Otherwise, read the file as text
    else:
        with open(path, 'r') as file:
            content = file.read()

    return content, is_binary

def get_buffer(client_sock):
    # Read data from the socket in 1024-byte chunks until the end
    buffer = ''

    while '\r\n\r\n' not in buffer:
        try:
            buffer += client_sock.recv(1024).decode()
        except:
            break

    return buffer

def handle_client(client_sock):
    while True:
        # Get the request
        buffer = get_buffer(client_sock)

        # Print the request
        print(buffer)

        if not buffer:
            break
        
        # Get the file name and connection status
        file_name, con_status = get_details(buffer)
        content, is_binary = get_file_content(file_name)

        # Redirect
        if file_name == 'redirect':
            client_sock.send(b'HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n')
            break

        # Not found
        if not content:
            client_sock.send(b'HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n')
            client_sock.close()
            break
        
        client_sock.send(('HTTP/1.1 200 OK\r\nConnection: ' + con_status + '\r\nContent-Length: ' + str(len(content)) + '\r\n\r\n').encode())

        # Send content
        if is_binary:
            client_sock.send(content)
        else:
            client_sock.send(content.encode())

        if con_status == 'close':
            break

while True:
    # Accept a connection
    client_sock, client_addr = socket.accept()
    client_sock.settimeout(1)

    # Handle the client
    handle_client(client_sock)
    client_sock.close()