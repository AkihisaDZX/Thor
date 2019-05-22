"""
基于Process的多进程网络并发
"""


from multiprocessing import Process
import socket
import sys


def handle(c):
    print('客户端：',c.getpeername())
    while True:
        data = c.recv(1024)
        if not data:
            break
        print(data.decode())
        c.send(b'OK')
    c.close()



# 创建监听套接字
ADDR = ('127.0.0.1',6657)

server_fd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_fd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server_fd.bind(ADDR)
server_fd.listen(3)

# 循环等待客户端连接
while True:
    try:
        cfd, addr = server_fd.accept()
    except KeyboardInterrupt:
        sys.exit('退出服务器')
    except Exception as e:
        print(e)
        continue

    # 创建新的进程处理客户端请求
    p = Process(target=handle,args=(cfd,))
    p.daemon = True
    p.start()
