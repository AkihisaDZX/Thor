"""FTP文件服务器 server"""

import socket
import os, sys
from threading import Thread
from time import sleep

# 全局变量
ADDR = ('0.0.0.0', 6657)
FTP = "/home/tarena/FTP/"  # 文件库路径


# 将客户端请求封装为类
class FtpServer:
    def __init__(self, connfd, FTP_PATH):
        self.connfd = connfd
        self.path = FTP_PATH

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.path)
        if not files:
            self.connfd.send('该文件夹为空'.encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)

        info = ''
        for f in files:
            if f[0] != '.' and os.path.isfile(self.path + f):
                info += f + '\n'
        self.connfd.send(info.encode())

    def do_get(self, file_name):
        try:
            fd = open(self.path + file_name, 'rb')
        except IOError:
            self.connfd.send('该文件不存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)

        while True:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

        fd.close()

    def do_put(self,file_name):
        if os.path.exists(self.path+file_name):
            self.connfd.send('该文件已存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
            fd = open(self.path + file_name, 'wb')
            # 接收文件
            while True:
                data = self.connfd.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()




def request(connfd):
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP + cls + '/'
    ftp = FtpServer(connfd, FTP_PATH)
    while True:
        data = connfd.recv(1024).decode()
        # 如果客户端断开，返回data为空
        if not data or data[0] == 'Q':
            return
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            file_name = data.strip().split(' ')[-1]
            ftp.do_get(file_name)
        elif data[0] == 'P':
            file_name = data.strip().split(' ')[-1]
            ftp.do_put(file_name)


# 网络搭建
def main():
    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_fd.bind(ADDR)
    server_fd.listen(5)
    print("Listen the port 6657...")
    while True:
        try:
            cfd, addr = server_fd.accept()
        except KeyboardInterrupt:
            sys.exit("退出服务程序")
        except Exception as e:
            print(e)
            continue
        print('客户端：', addr)

        # 创建线程处理请求
        client = Thread(target=request, args=(cfd,))
        client.daemon = True
        client.start()


if __name__ == '__main__':
    main()
