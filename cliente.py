# Cliente do chat
# uma thread fica recebendo as mensagens e o programa principal le o teclado
# como usar: python cliente.py nome [ip] [porta]

import socket
import threading
import sys


def receber(sock):
    arq = sock.makefile("r", encoding="utf-8")
    for linha in arq:
        linha = linha.strip()
        if linha.startswith("MSG "):
            print(linha[4:])
        elif linha.startswith("INFO ") or linha.startswith("OK "):
            print("  *", linha.split(" ", 1)[1])
        elif linha.startswith("ERRO "):
            print("  ERRO:", linha[5:])
        else:
            print(linha)
    print("Conexao encerrada")


if len(sys.argv) < 2:
    print("Uso: python cliente.py nome [ip] [porta]")
    sys.exit()

nome = sys.argv[1]
ip = "127.0.0.1"
porta = 5000
if len(sys.argv) > 2:
    ip = sys.argv[2]
if len(sys.argv) > 3:
    porta = int(sys.argv[3])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, porta))
sock.send(("NICK " + nome + "\n").encode("utf-8"))

t = threading.Thread(target=receber, args=(sock,))
t.daemon = True
t.start()

try:
    while True:
        msg = input()
        sock.send((msg + "\n").encode("utf-8"))
        if msg == "/sair":
            break
except:
    pass

sock.close()
