# Cliente SMTP feito com socket (sem usar smtplib)
# A ideia e mandar cada comando do protocolo na mao pra ver no Wireshark

import socket
import ssl
import base64


def ler_resposta(arq):
    # a resposta pode ter varias linhas, tipo "250-..." e a ultima e "250 ..."
    while True:
        linha = arq.readline().decode("utf-8").strip()
        print("S:", linha)
        if len(linha) < 4 or linha[3] != "-":
            return int(linha[:3])


def comando(sock, arq, texto, codigo_esperado, mostrar=True):
    if mostrar:
        print("C:", texto)
    else:
        print("C: ****")
    sock.send((texto + "\r\n").encode("utf-8"))
    codigo = ler_resposta(arq)
    if codigo != codigo_esperado:
        raise Exception("Erro no comando " + texto.split()[0] + ": " + str(codigo))


def enviar_email(config, destino, assunto, texto):
    host = config["host"]
    porta = config["porta"]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((host, porta))
    arq = sock.makefile("rb")

    # servidor manda 220 quando conecta
    if ler_resposta(arq) != 220:
        raise Exception("Servidor SMTP nao respondeu 220")

    comando(sock, arq, "EHLO cliente", 250)

    # Gmail usa porta 587 com STARTTLS (criptografia)
    if config["usar_starttls"]:
        comando(sock, arq, "STARTTLS", 220)
        contexto = ssl.create_default_context()
        sock = contexto.wrap_socket(sock, server_hostname=host)
        arq = sock.makefile("rb")
        comando(sock, arq, "EHLO cliente", 250)

    # login (usuario e senha vao em base64)
    if config["usuario"] != "":
        usuario = base64.b64encode(config["usuario"].encode()).decode()
        senha = base64.b64encode(config["senha"].encode()).decode()
        comando(sock, arq, "AUTH LOGIN", 334)
        comando(sock, arq, usuario, 334, mostrar=False)
        comando(sock, arq, senha, 235, mostrar=False)

    comando(sock, arq, "MAIL FROM:<" + config["remetente"] + ">", 250)
    comando(sock, arq, "RCPT TO:<" + destino + ">", 250)
    comando(sock, arq, "DATA", 354)

    # cabecalho + linha em branco + corpo, e termina com um ponto sozinho
    msg = "From: " + config["remetente"] + "\r\n"
    msg += "To: " + destino + "\r\n"
    msg += "Subject: " + assunto + "\r\n"
    msg += "Content-Type: text/plain; charset=utf-8\r\n"
    msg += "\r\n"
    msg += texto.replace("\n", "\r\n") + "\r\n"
    print("C: (corpo do email)")
    sock.send(msg.encode("utf-8"))
    comando(sock, arq, ".", 250)

    comando(sock, arq, "QUIT", 221)
    sock.close()


# pra testar so o email: python smtp_cliente.py email@destino.com
if __name__ == "__main__":
    import json
    import sys

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    destino = "teste@exemplo.com"
    if len(sys.argv) > 1:
        destino = sys.argv[1]

    enviar_email(config["smtp"], destino, "Teste SMTP", "Teste do cliente SMTP do projeto de Redes")
    print("Email enviado!")
