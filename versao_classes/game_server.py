import socket
import threading

from player import Player


# ============================================================
# CLASSE GAME SERVER
# ============================================================
# Responsável por:
# - aceitar conexões
# - criar jogadores
# - processar login
# - movimentação
# - colisões
# - chat
# - sincronização
# - enviar logs para a interface gráfica do servidor
# ============================================================


class GameServer:

    def __init__(
        self,
        host="0.0.0.0",
        port=5000,
        log_callback=None
    ):

        # ====================================================
        # CONFIGURAÇÕES DE REDE
        # ====================================================

        self.host = host
        self.port = port


        # ====================================================
        # CALLBACK DE LOG
        # ====================================================
        # Se o servidor estiver sendo usado com server_gui.py,
        # essa função envia as mensagens para a janela.
        #
        # Se não houver callback, usa print() normalmente.
        # ====================================================

        self.log_callback = log_callback


        # ====================================================
        # CONFIGURAÇÕES DO JOGO
        # ====================================================

        self.move_speed = 10

        self.map_width = 800
        self.map_height = 600

        self.player_size = 40

        self.map_margin = 20


        # ====================================================
        # CLIENTES E JOGADORES
        # ====================================================

        # Lista de sockets conectados.
        self.clients = []

        # Dicionário:
        # conexão -> Player
        self.players = {}

        # Evita conflitos entre threads.
        self.lock = threading.Lock()


        # ====================================================
        # OBSTÁCULOS DO MAPA
        # ====================================================
        #
        # Formato:
        # (x, y, largura, altura)
        # ====================================================

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


        # ====================================================
        # SOCKET DO SERVIDOR
        # ====================================================

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )


        # Permite reutilizar a porta
        # após reiniciar o servidor.
        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )


        # Controla se o servidor está ativo.
        self.running = False


    # ========================================================
    # LOG
    # ========================================================

    def log(self, message):

        if self.log_callback:

            self.log_callback(
                message
            )

        else:

            print(
                message
            )


    # ========================================================
    # ENVIAR MENSAGEM PARA UM CLIENTE
    # ========================================================

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

            self.log(
                f"Erro ao enviar mensagem: {error}"
            )


    # ========================================================
    # BROADCAST
    # ========================================================
    # Envia uma mensagem para todos os clientes.
    #
    # sender pode ser usado para excluir
    # quem originou a mensagem.
    # ========================================================

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


    # ========================================================
    # ENVIAR JOGADORES EXISTENTES
    # ========================================================
    # Quando um jogador entra, ele precisa saber
    # quem já está conectado.
    #
    # Protocolo:
    #
    # PLAYER|nome|personagem|x|y
    # ========================================================

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
                            f"{player.character}|"
                            f"{player.x}|"
                            f"{player.y}"
                        )
                    )


    # ========================================================
    # VERIFICAR COLISÃO
    # ========================================================

    def is_colliding(
        self,
        x,
        y
    ):

        # Limites do jogador.
        player_left = x
        player_top = y

        player_right = (
            x + self.player_size
        )

        player_bottom = (
            y + self.player_size
        )


        # Verifica cada obstáculo.
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


    # ========================================================
    # PROCESSAR MENSAGEM DO CLIENTE
    # ========================================================

    def process_message(
        self,
        connection,
        message
    ):

        # Só processa jogadores registrados.
        if connection not in self.players:

            return


        player = self.players[
            connection
        ]


        # ====================================================
        # CHAT
        # ====================================================
        #
        # Cliente envia:
        #
        # CHAT|Olá!
        #
        # Servidor envia:
        #
        # CHAT|Math|Olá!
        # ====================================================

        if message.startswith(
            "CHAT|"
        ):

            parts = message.split(
                "|",
                1
            )


            if len(parts) < 2:

                return


            chat_message = parts[1]


            if not chat_message.strip():

                return


            self.log(
                f"[CHAT] "
                f"{player.name}: "
                f"{chat_message}"
            )


            self.broadcast(

                (
                    f"CHAT|"
                    f"{player.name}|"
                    f"{chat_message}"
                )
            )


            return


        # ====================================================
        # MOVIMENTAÇÃO
        # ====================================================

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


        # ====================================================
        # LIMITES DO MAPA
        # ====================================================

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


        # ====================================================
        # COLISÃO
        # ====================================================

        if not self.is_colliding(
            new_x,
            new_y
        ):

            player.set_position(
                new_x,
                new_y
            )


        # Posição oficial.
        x, y = (
            player.get_position()
        )


        # ====================================================
        # SINCRONIZAÇÃO
        # ====================================================

        self.broadcast(

            (
                f"MOVE|"
                f"{player.name}|"
                f"{x}|"
                f"{y}"
            )
        )


    # ========================================================
    # ATENDER CLIENTE
    # ========================================================

    def handle_client(
        self,
        connection,
        address
    ):

        self.log(
            f"Nova conexão: {address}"
        )


        self.clients.append(
            connection
        )


        buffer = ""


        try:

            # =================================================
            # LOGIN
            # =================================================
            #
            # Esperado:
            #
            # LOGIN|Math|character_2
            # =================================================

            login_complete = False


            while not login_complete:

                data = connection.recv(
                    1024
                )


                if not data:

                    return


                buffer += (
                    data.decode()
                )


                if "\n" in buffer:

                    (
                        login_message,
                        buffer
                    ) = buffer.split(
                        "\n",
                        1
                    )


                    parts = (
                        login_message.split(
                            "|",
                            2
                        )
                    )


                    # ==========================================
                    # VALIDA LOGIN
                    # ==========================================

                    if (
                        len(parts) != 3
                        or parts[0] != "LOGIN"
                    ):

                        self.send_message(
                            connection,
                            "ERROR|LOGIN_INVALIDO"
                        )

                        return


                    name = (
                        parts[1].strip()
                    )


                    character = (
                        parts[2].strip()
                    )


                    # Nome obrigatório.
                    if not name:

                        self.send_message(
                            connection,
                            "ERROR|NOME_INVALIDO"
                        )

                        return


                    # ==========================================
                    # PERSONAGENS PERMITIDOS
                    # ==========================================

                    valid_characters = [

                        "character_1",

                        "character_2",

                        "character_3"
                    ]


                    if (
                        character
                        not in valid_characters
                    ):

                        self.send_message(
                            connection,
                            "ERROR|PERSONAGEM_INVALIDO"
                        )

                        return


                    login_complete = True


            # =================================================
            # CRIA PLAYER
            # =================================================

            player = Player(

                name=name,

                character=character,

                x=300,

                y=300
            )


            with self.lock:

                self.players[
                    connection
                ] = player


            # =================================================
            # LOG DE ENTRADA
            # =================================================

            self.log(
                f"{player.name} entrou "
                f"usando {player.character}"
            )


            self.log(
                f"Jogadores online: "
                f"{len(self.players)}"
            )


            # =================================================
            # SINCRONIZAÇÃO INICIAL
            # =================================================

            # Envia jogadores já existentes
            # para quem acabou de entrar.

            self.send_existing_players(
                connection
            )


            # Informa aos outros sobre
            # o novo jogador.

            self.broadcast(

                (
                    f"ENTER|"
                    f"{player.name}|"
                    f"{player.character}|"
                    f"{player.x}|"
                    f"{player.y}"
                ),

                sender=connection
            )


            # =================================================
            # LOOP DO CLIENTE
            # =================================================

            while self.running:

                data = connection.recv(
                    1024
                )


                if not data:

                    break


                buffer += (
                    data.decode()
                )


                while "\n" in buffer:

                    (
                        message,
                        buffer
                    ) = buffer.split(
                        "\n",
                        1
                    )


                    if message:

                        self.process_message(
                            connection,
                            message
                        )


        except Exception as error:

            if self.running:

                self.log(
                    f"Erro com {address}: "
                    f"{error}"
                )


        finally:

            # =================================================
            # REMOVE CLIENTE
            # =================================================

            if connection in self.clients:

                self.clients.remove(
                    connection
                )


            # =================================================
            # REMOVE JOGADOR
            # =================================================

            if connection in self.players:

                player = (
                    self.players[
                        connection
                    ]
                )


                with self.lock:

                    del self.players[
                        connection
                    ]


                # Avisa os outros.
                self.broadcast(
                    f"LEAVE|{player.name}"
                )


                self.log(
                    f"{player.name} "
                    f"saiu do mundo"
                )


                self.log(
                    f"Jogadores online: "
                    f"{len(self.players)}"
                )


            try:

                connection.close()

            except Exception:

                pass


    # ========================================================
    # INICIAR SERVIDOR
    # ========================================================

    def start(self):

        try:

            # Associa IP e porta.
            self.server_socket.bind(
                (
                    self.host,
                    self.port
                )
            )


            # Começa a ouvir conexões.
            self.server_socket.listen()


            self.running = True


            # =================================================
            # LOG DE STATUS
            # =================================================

            self.log(
                "Servidor ONLINE"
            )


            self.log(
                f"Escutando em "
                f"{self.host}:{self.port}"
            )


            self.log(
                "Aguardando jogadores..."
            )


            # =================================================
            # LOOP PRINCIPAL
            # =================================================

            while self.running:

                try:

                    (
                        connection,
                        address
                    ) = (
                        self.server_socket
                        .accept()
                    )


                    # Cada cliente roda
                    # em uma thread separada.

                    thread = (
                        threading.Thread(

                            target=
                            self.handle_client,

                            args=(
                                connection,
                                address
                            ),

                            daemon=True
                        )
                    )


                    thread.start()


                except OSError:

                    # O socket foi fechado
                    # durante stop().
                    break


        except Exception as error:

            self.log(
                f"Erro ao iniciar servidor: "
                f"{error}"
            )


        finally:

            self.running = False


            self.log(
                "Servidor OFFLINE"
            )


    # ========================================================
    # PARAR SERVIDOR
    # ========================================================

    def stop(self):

        # Evita chamar várias vezes.
        if not self.running:

            return


        self.log(
            "Encerrando servidor..."
        )


        self.running = False


        # ====================================================
        # FECHA CLIENTES
        # ====================================================

        for connection in (
            self.clients.copy()
        ):

            try:

                connection.shutdown(
                    socket.SHUT_RDWR
                )

            except Exception:

                pass


            try:

                connection.close()

            except Exception:

                pass


        self.clients.clear()


        # ====================================================
        # FECHA SOCKET PRINCIPAL
        # ====================================================

        try:

            self.server_socket.close()

        except Exception:

            pass