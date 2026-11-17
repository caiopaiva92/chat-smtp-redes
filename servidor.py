# Servidor do chat em grupo
# Cada cliente que conecta ganha uma thread. Quando alguem manda mensagem,
# o servidor repassa pra todos. Se alguem for marcado com @ e estiver
# offline, o servidor manda um email de aviso.

import socket
import threading
import json
from smtp_cliente import enviar_email

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

HOST = config["chat"]["host"]
PORTA = config["chat"]["porta"]

clientes = {}  # nome -> socket do cliente
emails = config["usuarios"]  # nome -> email
trava = threading.Lock()  # pra duas threads nao mexerem no dicionario ao mesmo tempo


def mandar(sock, texto):
    try:
        sock.send((texto + "\n").encode("utf-8"))
    except:
        pass


def mandar_para_todos(texto):
    with trava:
        lista = list(clientes.values())
    for sock in lista:
        mandar(sock, texto)


def avisar_por_email(nome, autor, texto):
    destino = emails[nome]
    assunto = "Chat Redes - " + autor + " te mencionou"
    corpo = "Oi " + nome + "!\n\n"
    corpo += autor + " te mencionou no chat enquanto voce estava offline:\n\n"
    corpo += '"' + texto + '"\n'
    try:
        print("Mandando email para", destino)
        enviar_email(config["smtp"], destino, assunto, corpo)
        mandar_para_todos("INFO " + nome + " esta offline e foi avisado por email")
    except Exception as e:
        print("Erro ao mandar email:", e)


def ver_mencoes(autor, texto):
    for palavra in texto.split():
        if palavra.startswith("@"):
            nome = palavra[1:].strip(".,!?").lower()
            if nome in clientes or nome == autor:
                continue
            if nome in emails:
                # thread separada pra o chat nao travar enquanto manda o email
                threading.Thread(target=avisar_por_email, args=(nome, autor, texto)).start()


def atender_cliente(conn, endereco):
    arq = conn.makefile("r", encoding="utf-8")

    # a primeira mensagem tem que ser: NICK nome
    primeira = arq.readline().strip()
    if not primeira.startswith("NICK "):
        mandar(conn, "ERRO primeiro manda NICK nome")
        conn.close()
        return

    nome = primeira[5:].strip().lower()
    with trava:
        if nome in clientes:
            mandar(conn, "ERRO esse nome ja esta em uso")
            conn.close()
            return
        clientes[nome] = conn

    print(nome, "entrou", endereco)
    mandar(conn, "OK bem-vindo, " + nome + "! Digite /ajuda para ver os comandos")
    mandar_para_todos("INFO " + nome + " entrou no chat")

    try:
        for linha in arq:
            texto = linha.strip()
            if texto == "":
                continue

            if texto == "/sair":
                break
            elif texto == "/online":
                mandar(conn, "INFO online: " + ", ".join(clientes.keys()))
            elif texto.startswith("/email "):
                email = texto[7:].strip()
                emails[nome] = email
                # salva no arquivo pra nao perder
                with open("config.json", "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                mandar(conn, "OK email cadastrado: " + email)
            elif texto == "/ajuda":
                mandar(conn, "INFO comandos: /online, /email seu@email.com, /sair. Use @nome pra marcar alguem")
            else:
                print(nome + ":", texto)
                mandar_para_todos("MSG " + nome + ": " + texto)
                ver_mencoes(nome, texto)
    except:
        pass  # cliente caiu

    with trava:
        del clientes[nome]
    conn.close()
    print(nome, "saiu")
    mandar_para_todos("INFO " + nome + " saiu do chat")


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORTA))
servidor.listen()
print("Servidor rodando na porta", PORTA)

while True:
    conn, endereco = servidor.accept()
    t = threading.Thread(target=atender_cliente, args=(conn, endereco))
    t.daemon = True
    t.start()
