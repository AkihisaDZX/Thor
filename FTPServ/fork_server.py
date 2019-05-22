"""
基于fork的多进程网络并发模型
"""

import os, sys
import socket
import signal


def handle(c):
    print('客户端：', c.getpeername())
    while True:
        data = c.recv(1024)
        if not data:
            break
        print(data.decode())
        c.send(b'copy it')
    c.close()


# 处理僵尸进程
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

# 创建监听套接字
ADDR = ('127.0.0.1', 6657)

server_fd = socket.socket()
server_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_fd.bind(ADDR)
server_fd.listen(5)

while True:
    try:
        cfd, addr = server_fd.accept()
    except KeyboardInterrupt:
        sys.exit('退出服务器')
    except Exception as e:
        print(e)
        continue

    # 创建子进程处理客户端请求
    pid = os.fork()

    if pid == 0:
        server_fd.close()
        handle(cfd)  # 具体处理客户端请求
        os._exit(0)  # 处理完毕后销毁子进程
    else:
        cfd.close()
        pass
