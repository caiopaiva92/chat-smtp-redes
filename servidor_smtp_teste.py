# Servidor SMTP simples so pra teste (sem senha e sem criptografia)
# Ele finge ser um servidor de email e mostra no terminal o que chegou.
# Usamos ele na apresentacao e pra capturar o SMTP no Wireshark (porta 2525)

import socket
import threading

PORTA = 2525


def atender(conn):
    arq = conn.makefile("rb")
    conn.send(b"220 servidor de teste pronto\r\n")
    lendo_email = False
    email = []

    while True:
        linha = arq.readline().decode("utf-8").rstrip("\r\n")
        if linha == "" and not lendo_email:
            break

        if lendo_email:
            if linha == ".":
                lendo_email = False
                print("========== EMAIL RECEBIDO ==========")
                print("\n".join(email))
                print("====================================")
                email = []
                conn.send(b"250 OK email recebido\r\n")
            else:
                email.append(linha)
            continue

        cmd = linha.upper()
        if cmd.startswith("EHLO") or cmd.startswith("HELO"):
            conn.send(b"250 ola\r\n")
        elif cmd.startswith("MAIL FROM") or cmd.startswith("RCPT TO"):
            conn.send(b"250 OK\r\n")
        elif cmd == "DATA":
            lendo_email = True
            conn.send(b"354 pode mandar, termine com um ponto\r\n")
        elif cmd == "QUIT":
            conn.send(b"221 tchau\r\n")
            break
        else:
            conn.send(b"502 comando nao suportado\r\n")

    conn.close()


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind(("0.0.0.0", PORTA))
servidor.listen()
print("Servidor SMTP de teste na porta", PORTA)

while True:
    conn, endereco = servidor.accept()
    threading.Thread(target=atender, args=(conn,), daemon=True).start()
