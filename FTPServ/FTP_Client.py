import socket
import sys
from time import sleep


class FTPClient:
    def __init__(self,connfd):
        self.sockfd = connfd

    def do_list(self):
        self.sockfd.send(b'L')
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            data = self.sockfd.recv(4096).decode()
            print(data)
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit('谢谢使用')

    def do_put(self,file_name):
        # 判断文件是否存在
        try:
            fd = open(file_name, 'rb')
        except FileNotFoundError:
            print('文件不存在')
            return

        file_name = file_name.split('/')[-1]
        self.sockfd.send(('P ' + file_name).encode())
        data = self.sockfd.recv(128).decode()
        if data == 'OK':

            while True:
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)

    def do_get(self,file_name):
        self.sockfd.send(('G '+file_name).encode())
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            fd = open(file_name,'wb')
            while True:
                data = self.sockfd.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)


def request(connfd):
    ftp = FTPClient(connfd)
    while True:
        print("\n++++++++命令选项++++++++")
        print("********* list *********")
        print("******* get file *******")
        print("******* put file *******")
        print("********* quit *********")
        print("************************")
        cmd = input("命令：")
        if cmd == 'list':
            ftp.do_list()
        elif cmd == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'put':
            file_name = cmd.strip().split(' ')[-1]
            ftp.do_put(file_name)
        elif cmd[:3] == 'get':
            file_name = cmd.strip().split(' ')[-1]
            ftp.do_get(file_name)


def main():
    ADDR = ('127.0.0.1', 8080)
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print('连接服务器失败')
        return
    else:
        print("""
        ***********************
        * Data   File   Image *
        ***********************
        """)
        cls = input('文件类别：')
        if cls not in ('Data', 'File', 'Image'):
            print('Sorry, input Error')
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)  # 发送具体请求



if __name__ == '__main__':
    main()