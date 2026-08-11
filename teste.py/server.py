import socket
import threading

# ==============================
# CONFIGURAÇÕES DO SERVIDOR
# ==============================

HOST = "0.0.0.0"
PORT = 5000

MOVE_SPEED = 10

MAP_WIDTH = 800
MAP_HEIGHT = 600

PLAYER_SIZE = 40
MAP_MARGIN = 20

clients = []
players = {}

lock = threading.Lock()


# ==============================
# ÁREAS DE COLISÃO
# ==============================

# Casa
HOUSE = (
    600,
    400,
    120,
    100
)

# Árvores
TREE_1 = (
    85,
    75,
    70,
    90
)

TREE_2 = (
    615,
    115,
    70,
    90
)

obstacles = [
    HOUSE,
    TREE_1,
    TREE_2
]


# ==============================
# VERIFICA COLISÃO
# ==============================

def is_colliding(x, y):

    player_left = x
    player_top = y
    player_right = x + PLAYER_SIZE
    player_bottom = y + PLAYER_SIZE

    for obstacle in obstacles:

        obstacle_x = obstacle[0]
        obstacle_y = obstacle[1]
        obstacle_width = obstacle[2]
        obstacle_height = obstacle[3]

        obstacle_left = obstacle_x
        obstacle_top = obstacle_y
        obstacle_right = obstacle_x + obstacle_width
        obstacle_bottom = obstacle_y + obstacle_height

        collision = (
            player_right > obstacle_left
            and player_left < obstacle_right
            and player_bottom > obstacle_top
            and player_top < obstacle_bottom
        )

        if collision:
            return True

    return False


# ==============================
# ENVIA UMA MENSAGEM
# ==============================

def send_message(connection, message):

    try:
        connection.sendall(
            (message + "\n").encode()
        )

    except:
        pass


# ==============================
# BROADCAST
# ==============================

def broadcast(message, sender=None):

    for client in clients:

        if client != sender:

            send_message(
                client,
                message
            )


# ==============================
# ENVIA JOGADORES EXISTENTES
# ==============================

def send_existing_players(connection):

    with lock:

        for player_connection, player in players.items():

            if player_connection != connection:

                send_message(
                    connection,
                    f"PLAYER|{player['name']}|{player['x']}|{player['y']}"
                )


# ==============================
# PROCESSA MOVIMENTO
# ==============================

def process_message(connection, message):

    player = players[connection]

    name = player["name"]

    old_x = player["x"]
    old_y = player["y"]

    new_x = old_x
    new_y = old_y


    # ==============================
    # MOVIMENTAÇÃO
    # ==============================

    if message == "MOVE_W":

        new_y -= MOVE_SPEED


    elif message == "MOVE_S":

        new_y += MOVE_SPEED


    elif message == "MOVE_A":

        new_x -= MOVE_SPEED


    elif message == "MOVE_D":

        new_x += MOVE_SPEED


    else:

        return


    # ==============================
    # LIMITES DO MAPA
    # ==============================

    new_x = max(
        MAP_MARGIN,
        min(
            new_x,
            MAP_WIDTH
            - PLAYER_SIZE
            - MAP_MARGIN
        )
    )


    new_y = max(
        MAP_MARGIN,
        min(
            new_y,
            MAP_HEIGHT
            - PLAYER_SIZE
            - MAP_MARGIN
        )
    )


    # ==============================
    # COLISÃO
    # ==============================

    if not is_colliding(
        new_x,
        new_y
    ):

        player["x"] = new_x
        player["y"] = new_y


    x = player["x"]
    y = player["y"]


    print(
        f"{name} está em X={x}, Y={y}"
    )


    # Envia posição oficial
    # para TODOS os jogadores
    broadcast(
        f"MOVE|{name}|{x}|{y}"
    )


# ==============================
# ATENDE CLIENTE
# ==============================

def handle_client(
    connection,
    address
):

    print(
        f"Cliente conectado: {address}"
    )

    clients.append(connection)

    buffer = ""

    name = None


    try:

        # ==============================
        # RECEBE NOME
        # ==============================

        while name is None:

            data = connection.recv(1024)

            if not data:
                return

            buffer += data.decode()


            if "\n" in buffer:

                name, buffer = buffer.split(
                    "\n",
                    1
                )


        # ==============================
        # CRIA JOGADOR
        # ==============================

        with lock:

            players[connection] = {
                "name": name,
                "x": 300,
                "y": 300
            }


        print(
            f"{name} entrou no mundo!"
        )


        # Envia jogadores existentes
        send_existing_players(
            connection
        )


        # Avisa os demais
        broadcast(
            f"ENTER|{name}|300|300",
            connection
        )


        # ==============================
        # LOOP DE COMUNICAÇÃO
        # ==============================

        while True:

            data = connection.recv(1024)

            if not data:
                break


            buffer += data.decode()


            while "\n" in buffer:

                message, buffer = buffer.split(
                    "\n",
                    1
                )


                if message:

                    process_message(
                        connection,
                        message
                    )


    except Exception as error:

        print(
            f"Erro com {address}: {error}"
        )


    finally:

        # Remove cliente
        if connection in clients:

            clients.remove(
                connection
            )


        # Remove jogador
        if connection in players:

            name = players[
                connection
            ]["name"]


            with lock:

                del players[
                    connection
                ]


            broadcast(
                f"LEAVE|{name}"
            )


            print(
                f"{name} saiu do mundo!"
            )


        connection.close()


# ==============================
# CRIA SERVIDOR
# ==============================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)


server.bind(
    (
        HOST,
        PORT
    )
)


server.listen()


print(
    f"Servidor iniciado na porta {PORT}"
)

print(
    "Aguardando conexões..."
)


# ==============================
# LOOP PRINCIPAL
# ==============================

while True:

    connection, address = (
        server.accept()
    )


    thread = threading.Thread(
        target=handle_client,
        args=(
            connection,
            address
        ),
        daemon=True
    )


    thread.start()