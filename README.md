# Chat com alerta por e-mail (SMTP)

Projeto final da disciplina de Redes de Computadores.

**Tema:** Camada de Aplicação - Sockets TCP e protocolo SMTP

**Equipe:** Álefe Brito Monteiro, Antônio José Batista Salazar e Caio Cezar Monteiro Paiva

## Sobre o projeto

É um chat em grupo feito em Python usando sockets TCP. O servidor recebe as mensagens dos clientes e repassa para todo mundo que está conectado.

Se alguém marcar outro usuário com `@nome` e ele estiver offline, o servidor manda um e-mail avisando. O envio do e-mail é feito pelo nosso próprio cliente SMTP, que manda os comandos do protocolo direto pelo socket (sem usar a biblioteca smtplib).

Também usamos o Wireshark para analisar o tráfego do chat e do SMTP.

## Arquivos

- `servidor.py` - servidor do chat (porta 5000)
- `cliente.py` - cliente do chat que roda no terminal
- `smtp_cliente.py` - nosso cliente SMTP
- `servidor_smtp_teste.py` - servidor de e-mail falso, só para testar (porta 2525)
- `config.exemplo.json` - exemplo de configuração

## Como rodar

Precisa ter o Python 3 instalado. Não precisa instalar nenhuma biblioteca.

1. Copie o `config.exemplo.json` e renomeie a cópia para `config.json`

2. Abra 4 terminais na pasta do projeto e rode um comando em cada:

```
python servidor_smtp_teste.py
python servidor.py
python cliente.py caio
python cliente.py alefe
```

3. No terminal do caio, mande uma mensagem marcando alguém que não está online, por exemplo:

```
Oi @antonio, tudo certo?
```

O e-mail de aviso vai aparecer no terminal do `servidor_smtp_teste.py`.

Para conectar de outro computador da rede: `python cliente.py nome IP_DO_SERVIDOR 5000`

## Comandos do chat

- `@nome` - marca alguém (se estiver offline, recebe e-mail)
- `/online` - mostra quem está conectado
- `/email seu@email.com` - cadastra seu e-mail
- `/ajuda` - mostra os comandos
- `/sair` - sai do chat

## Usando o Gmail de verdade

1. Ative a verificação em duas etapas na conta Google e crie uma **senha de app**
2. No `config.json`, mude a parte do `smtp` para:

```json
"smtp": {
  "host": "smtp.gmail.com",
  "porta": 587,
  "usar_starttls": true,
  "usuario": "seuemail@gmail.com",
  "senha": "sua senha de app",
  "remetente": "seuemail@gmail.com"
}
```

3. Coloque e-mails reais na parte `usuarios`

Obs: o `config.json` está no `.gitignore` para a senha não ir para o GitHub.

## Wireshark

Filtros que usamos:

- `tcp.port == 5000` - mensagens do chat e o handshake TCP
- `tcp.port == 2525` - SMTP com o servidor de teste (dá para ver todos os comandos)
- `tcp.port == 587` - SMTP com o Gmail (depois do STARTTLS fica tudo criptografado)

Quando testar tudo no mesmo PC, capture na interface de loopback. Para ver a conversa inteira: botão direito no pacote > Follow > TCP Stream.
