import socket
import threading

from player import Player


# ==========================================
# CLASSE GAME SERVER
# ==========================================
# Responsável pelo servidor multiplayer.
#
# Agora ele processa:
# - Movimento
# - Entrada e saída de jogadores
# - Chat
# - Colisões
# - Sincronização
# ==========================================


class GameServer:

    def __init__(
        self,
        host="0.0.0.0",
        port=5000
    ):

        # ==================================
        # REDE
        # ==================================

        self.host = host
        self.port = port


        # ==================================
        # CONFIGURAÇÕES DO JOGO
        # ==================================

        self.move_speed = 10

        self.map_width = 800
        self.map_height = 600

        self.player_size = 40

        self.map_margin = 20


        # ==================================
        # CLIENTES E JOGADORES
        # ==================================

        self.clients = []

        self.players = {}

        self.lock = threading.Lock()


        # ==================================
        # OBSTÁCULOS
        # ==================================

        self.house_body = (
            600,
            400,
            120,
            100
        )

        self.house_roof = (
            580,
            340,
            160,
            60
        )

        self.tree_1 = (
            85,
            75,
            70,
            90
        )

        self.tree_2 = (
            615,
            115,
            70,
            90
        )

        self.obstacles = [
            self.house_body,
            self.house_roof,
            self.tree_1,
            self.tree_2
        ]


        # ==================================
        # SOCKET DO SERVIDOR
        # ==================================

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )


    # ======================================
    # ENVIA UMA MENSAGEM
    # ======================================

    def send_message(
        self,
        connection,
        message
    ):

        try:

            connection.sendall(
                (message + "\n").encode()
            )

        except Exception as error:

            print(
                f"Erro ao enviar mensagem: "
                f"{error}"
            )


    # ======================================
    # BROADCAST
    # ======================================

    def broadcast(
        self,
        message,
        sender=None
    ):

        for client in self.clients.copy():

            if client != sender:

                self.send_message(
                    client,
                    message
                )


    # ======================================
    # ENVIA JOGADORES EXISTENTES
    # ======================================

    def send_existing_players(
        self,
        connection
    ):

        with self.lock:

            for (
                player_connection,
                player
            ) in self.players.items():

                if (
                    player_connection
                    != connection
                ):

                    self.send_message(

                        connection,

                        (
                            f"PLAYER|"
                            f"{player.name}|"
                            f"{player.x}|"
                            f"{player.y}"
                        )
                    )


    # ======================================
    # VERIFICA COLISÃO
    # ======================================

    def is_colliding(
        self,
        x,
        y
    ):

        player_left = x
        player_top = y

        player_right = (
            x + self.player_size
        )

        player_bottom = (
            y + self.player_size
        )


        for obstacle in self.obstacles:

            obstacle_x = obstacle[0]
            obstacle_y = obstacle[1]

            obstacle_width = obstacle[2]
            obstacle_height = obstacle[3]


            obstacle_left = obstacle_x
            obstacle_top = obstacle_y

            obstacle_right = (
                obstacle_x
                + obstacle_width
            )

            obstacle_bottom = (
                obstacle_y
                + obstacle_height
            )


            collision = (

                player_right
                > obstacle_left

                and player_left
                < obstacle_right

                and player_bottom
                > obstacle_top

                and player_top
                < obstacle_bottom
            )


            if collision:

                return True


        return False


    # ======================================
    # PROCESSA MENSAGEM
    # ======================================

    def process_message(
        self,
        connection,
        message
    ):

        if connection not in self.players:

            return


        player = self.players[
            connection
        ]


        # ==================================
        # CHAT
        # ==================================

        if message.startswith("CHAT|"):

            # Divide apenas uma vez.
            #
            # CHAT|Olá pessoal
            #
            # vira:
            #
            # ["CHAT", "Olá pessoal"]
            parts = message.split(
                "|",
                1
            )


            if len(parts) < 2:

                return


            chat_message = parts[1]


            # Ignora mensagens vazias
            if not chat_message.strip():

                return


            print(
                f"[CHAT] "
                f"{player.name}: "
                f"{chat_message}"
            )


            # Envia para TODOS,
            # inclusive para quem escreveu.
            self.broadcast(

                (
                    f"CHAT|"
                    f"{player.name}|"
                    f"{chat_message}"
                )
            )


            return


        # ==================================
        # MOVIMENTAÇÃO
        # ==================================

        new_x = player.x
        new_y = player.y


        if message == "MOVE_W":

            new_y -= self.move_speed


        elif message == "MOVE_S":

            new_y += self.move_speed


        elif message == "MOVE_A":

            new_x -= self.move_speed


        elif message == "MOVE_D":

            new_x += self.move_speed


        else:

            return


        # ==================================
        # LIMITES DO MAPA
        # ==================================

        new_x = max(

            self.map_margin,

            min(

                new_x,

                self.map_width
                - self.player_size
                - self.map_margin
            )
        )


        new_y = max(

            self.map_margin,

            min(

                new_y,

                self.map_height
                - self.player_size
                - self.map_margin
            )
        )


        # ==================================
        # COLISÕES
        # ==================================

        if not self.is_colliding(
            new_x,
            new_y
        ):

            player.set_position(
                new_x,
                new_y
            )


        x, y = player.get_position()


        print(
            f"{player.name} está em "
            f"X={x}, Y={y}"
        )


        # ==================================
        # SINCRONIZAÇÃO
        # ==================================

        self.broadcast(

            (
                f"MOVE|"
                f"{player.name}|"
                f"{x}|"
                f"{y}"
            )
        )


    # ======================================
    # ATENDE CLIENTE
    # ======================================

    def handle_client(
        self,
        connection,
        address
    ):

        print(
            f"Cliente conectado: "
            f"{address}"
        )


        self.clients.append(
            connection
        )


        buffer = ""

        name = None


        try:

            # ==================================
            # RECEBE NOME
            # ==================================

            while name is None:

                data = connection.recv(
                    1024
                )


                if not data:

                    return


                buffer += data.decode()


                if "\n" in buffer:

                    name, buffer = (
                        buffer.split(
                            "\n",
                            1
                        )
                    )


            # ==================================
            # CRIA JOGADOR
            # ==================================

            player = Player(
                name=name,
                x=300,
                y=300
            )


            with self.lock:

                self.players[
                    connection
                ] = player


            print(
                f"{player.name} "
                f"entrou no mundo!"
            )


            self.send_existing_players(
                connection
            )


            self.broadcast(

                (
                    f"ENTER|"
                    f"{player.name}|"
                    f"{player.x}|"
                    f"{player.y}"
                ),

                sender=connection
            )


            # ==================================
            # LOOP DO CLIENTE
            # ==================================

            while True:

                data = connection.recv(
                    1024
                )


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

                        self.process_message(
                            connection,
                            message
                        )


        except Exception as error:

            print(
                f"Erro com {address}: "
                f"{error}"
            )


        finally:

            if connection in self.clients:

                self.clients.remove(
                    connection
                )


            if connection in self.players:

                player = self.players[
                    connection
                ]


                with self.lock:

                    del self.players[
                        connection
                    ]


                self.broadcast(
                    f"LEAVE|{player.name}"
                )


                print(
                    f"{player.name} "
                    f"saiu do mundo!"
                )


            connection.close()


    # ======================================
    # INICIA SERVIDOR
    # ======================================

    def start(self):

        self.server_socket.bind(
            (
                self.host,
                self.port
            )
        )


        self.server_socket.listen()


        print(
            "=============================="
        )

        print(
            "      MINI WORLD SERVER"
        )

        print(
            "=============================="
        )


        print(
            f"Servidor iniciado em "
            f"{self.host}:{self.port}"
        )


        print(
            "Aguardando conexões..."
        )


        try:

            while True:

                connection, address = (
                    self.server_socket.accept()
                )


                thread = threading.Thread(

                    target=self.handle_client,

                    args=(
                        connection,
                        address
                    ),

                    daemon=True
                )


                thread.start()


        except KeyboardInterrupt:

            print(
                "\nServidor encerrado."
            )


        finally:

            self.server_socket.close()