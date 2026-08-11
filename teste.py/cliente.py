import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


def receive_messages():
    while True:
        try:
            data = client.recv(1024)

            if not data:
                break

            message = data.decode()

            parts = message.split("|")

            # Outro jogador se movimentou
            if parts[0] == "MOVE":
                name = parts[1]
                x = parts[2]
                y = parts[3]

                print(
                    f"\n{name} está em X={x}, Y={y}"
                )

            # Outro jogador entrou
            elif parts[0] == "ENTER":
                name = parts[1]

                print(
                    f"\n{name} entrou no mundo!"
                )

            # Outro jogador saiu
            elif parts[0] == "LEAVE":
                name = parts[1]

                print(
                    f"\n{name} saiu do mundo!"
                )

            # Mensagem de chat
            elif parts[0] == "CHAT":
                name = parts[1]
                text = parts[2]

                print(
                    f"\n{name}: {text}"
                )

        except:
            break


client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect(
    (SERVER_IP, SERVER_PORT)
)

print("==============================")
print("       MINI WORLD")
print("==============================")

name = input("Digite seu nome: ")

# Envia o nome ao servidor
client.sendall(
    name.encode()
)

print()
print("Controles:")
print("W = cima")
print("A = esquerda")
print("S = baixo")
print("D = direita")
print("sair = encerrar")
print()
print("Qualquer outro texto será enviado no chat.")


receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

receive_thread.start()


while True:
    command = input("> ")

    if command.lower() == "sair":
        break

    command_lower = command.lower()

    if command_lower == "w":
        client.sendall(
            "MOVE_W".encode()
        )

    elif command_lower == "s":
        client.sendall(
            "MOVE_S".encode()
        )

    elif command_lower == "a":
        client.sendall(
            "MOVE_A".encode()
        )

    elif command_lower == "d":
        client.sendall(
            "MOVE_D".encode()
        )

    else:
        client.sendall(
            command.encode()
        )


client.close()

print("Conexão encerrada.")