import socket
import threading


# ==============================
# PYGAME
# ==============================

try:

    import pygame  # type: ignore

except ImportError:

    raise SystemExit(
        "Pygame é necessário. "
        "Instale com: pip install pygame"
    )


# ==============================
# REDE
# ==============================

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


# ==============================
# JOGO
# ==============================

WIDTH = 800
HEIGHT = 600

PLAYER_SIZE = 40

FPS = 60

MOVE_DELAY = 100

MAP_MARGIN = 20


# ==============================
# JOGADORES
# ==============================

players = {}

players_lock = threading.Lock()


# ==============================
# SOCKET
# ==============================

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


client.connect(
    (
        SERVER_IP,
        SERVER_PORT
    )
)


# ==============================
# NOME
# ==============================

name = input(
    "Digite o nome do jogador: "
)


client.sendall(
    (name + "\n").encode()
)


# Posição inicial
players[name] = [
    300,
    300
]


# ==============================
# ENVIA COMANDO
# ==============================

def send_command(command):

    try:

        client.sendall(
            (command + "\n").encode()
        )

    except:

        pass


# ==============================
# PROCESSA MENSAGENS
# ==============================

def process_server_message(
    message
):

    parts = message.split("|")

    command = parts[0]


    # ==============================
    # JOGADOR EXISTENTE
    # ==============================

    if command == "PLAYER":

        player_name = parts[1]

        x = int(parts[2])
        y = int(parts[3])


        with players_lock:

            players[
                player_name
            ] = [
                x,
                y
            ]


    # ==============================
    # NOVO JOGADOR
    # ==============================

    elif command == "ENTER":

        player_name = parts[1]

        x = int(parts[2])
        y = int(parts[3])


        with players_lock:

            players[
                player_name
            ] = [
                x,
                y
            ]


        print(
            f"{player_name} entrou no mundo!"
        )


    # ==============================
    # MOVIMENTO
    # ==============================

    elif command == "MOVE":

        player_name = parts[1]

        x = int(parts[2])
        y = int(parts[3])


        with players_lock:

            players[
                player_name
            ] = [
                x,
                y
            ]


    # ==============================
    # SAÍDA
    # ==============================

    elif command == "LEAVE":

        player_name = parts[1]


        with players_lock:

            if player_name in players:

                del players[
                    player_name
                ]


        print(
            f"{player_name} saiu do mundo!"
        )


# ==============================
# RECEBE DADOS
# ==============================

def receive_messages():

    buffer = ""


    while True:

        try:

            data = client.recv(1024)


            if not data:
                break


            buffer += data.decode()


            while "\n" in buffer:

                message, buffer = (
                    buffer.split(
                        "\n",
                        1
                    )
                )


                if message:

                    process_server_message(
                        message
                    )


        except:

            break


# ==============================
# THREAD DA REDE
# ==============================

receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)


receive_thread.start()


# ==============================
# INICIALIZAÇÃO DO PYGAME
# ==============================

pygame.init()


screen = pygame.display.set_mode(
    (
        WIDTH,
        HEIGHT
    )
)


pygame.display.set_caption(
    "Mini World Multiplayer"
)


clock = pygame.time.Clock()


font = pygame.font.Font(
    None,
    24
)


last_move = 0


# ==============================
# LOOP PRINCIPAL
# ==============================

running = True


while running:

    # ==============================
    # EVENTOS
    # ==============================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


    # ==============================
    # TECLADO
    # ==============================

    keys = pygame.key.get_pressed()


    current_time = (
        pygame.time.get_ticks()
    )


    if (
        current_time
        - last_move
        >= MOVE_DELAY
    ):

        command = None


        if keys[pygame.K_w]:

            command = "MOVE_W"


        elif keys[pygame.K_s]:

            command = "MOVE_S"


        elif keys[pygame.K_a]:

            command = "MOVE_A"


        elif keys[pygame.K_d]:

            command = "MOVE_D"


        if command:

            # IMPORTANTE:
            # não movemos localmente.
            # O servidor decide a posição.
            send_command(
                command
            )


            last_move = (
                current_time
            )


    # ==============================
    # FUNDO
    # ==============================

    screen.fill(
        (
            210,
            235,
            255
        )
    )


    # ==============================
    # MAPA
    # ==============================

    pygame.draw.rect(
        screen,
        (
            230,
            240,
            250
        ),
        (
            MAP_MARGIN,
            MAP_MARGIN,
            WIDTH - MAP_MARGIN * 2,
            HEIGHT - MAP_MARGIN * 2
        )
    )


    # ==============================
    # ÁRVORE 1
    # ==============================

    pygame.draw.rect(
        screen,
        (
            120,
            80,
            50
        ),
        (
            110,
            120,
            20,
            45
        )
    )


    pygame.draw.circle(
        screen,
        (
            60,
            160,
            80
        ),
        (
            120,
            110
        ),
        35
    )


    # ==============================
    # ÁRVORE 2
    # ==============================

    pygame.draw.rect(
        screen,
        (
            120,
            80,
            50
        ),
        (
            640,
            160,
            20,
            45
        )
    )


    pygame.draw.circle(
        screen,
        (
            60,
            160,
            80
        ),
        (
            650,
            150
        ),
        35
    )


    # ==============================
    # CASA
    # ==============================

    pygame.draw.rect(
        screen,
        (
            180,
            120,
            80
        ),
        (
            600,
            400,
            120,
            100
        )
    )


    # Telhado
    pygame.draw.polygon(
        screen,
        (
            150,
            70,
            60
        ),
        [
            (
                580,
                400
            ),
            (
                660,
                340
            ),
            (
                740,
                400
            )
        ]
    )


    # Porta
    pygame.draw.rect(
        screen,
        (
            100,
            60,
            40
        ),
        (
            645,
            450,
            30,
            50
        )
    )


    # ==============================
    # JOGADORES
    # ==============================

    with players_lock:

        for (
            player_name,
            position
        ) in players.items():

            x = position[0]
            y = position[1]


            # Jogador local
            if player_name == name:

                color = (
                    50,
                    100,
                    230
                )


            # Outros jogadores
            else:

                color = (
                    230,
                    70,
                    70
                )


            # ==============================
            # PERSONAGEM
            # ==============================

            pygame.draw.rect(
                screen,
                color,
                (
                    x,
                    y,
                    PLAYER_SIZE,
                    PLAYER_SIZE
                ),
                border_radius=8
            )


            # ==============================
            # NOME
            # ==============================

            text = font.render(
                player_name,
                True,
                (
                    20,
                    20,
                    20
                )
            )


            text_rect = text.get_rect(
                center=(
                    x
                    + PLAYER_SIZE // 2,

                    y - 12
                )
            )


            screen.blit(
                text,
                text_rect
            )


    # ==============================
    # ATUALIZA TELA
    # ==============================

    pygame.display.flip()


    clock.tick(
        FPS
    )


# ==============================
# ENCERRAMENTO
# ==============================

client.close()

pygame.quit()