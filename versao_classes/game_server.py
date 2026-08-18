import socket
import threading

from player import Player


# ============================================================
# GAME SERVER
# ============================================================
# O servidor é responsável por:
#
# - aceitar conexões
# - registrar jogadores
# - guardar personagem escolhido
# - controlar movimentação
# - controlar colisões
# - sincronizar jogadores
# - transmitir mensagens do chat
#
# IMPORTANTE:
# O servidor é a "autoridade" do jogo.
# O cliente pede para se mover, mas quem decide a posição
# verdadeira é o servidor.
# ============================================================


class GameServer:

    def __init__(
        self,
        host="0.0.0.0",
        port=5000
    ):

        # ----------------------------------------------------
        # REDE
        # ----------------------------------------------------

        self.host = host
        self.port = port


        # ----------------------------------------------------
        # CONFIGURAÇÕES DO MUNDO
        # ----------------------------------------------------

        self.move_speed = 10

        self.map_width = 800
        self.map_height = 600

        self.player_size = 40

        self.map_margin = 20


        # ----------------------------------------------------
        # CLIENTES
        # ----------------------------------------------------

        # Lista com as conexões TCP.
        self.clients = []


        # Dicionário:
        #
        # conexão -> objeto Player
        #
        # Exemplo:
        #
        # {
        #     socket_cliente: Player(...)
        # }

        self.players = {}


        # Como cada cliente roda em uma thread,
        # usamos Lock ao modificar self.players.
        self.lock = threading.Lock()


        # ----------------------------------------------------
        # OBSTÁCULOS
        # ----------------------------------------------------
        #
        # Formato:
        #
        # (x, y, largura, altura)
        #
        # Depois podemos mover isso para uma classe Map.
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # SOCKET DO SERVIDOR
        # ----------------------------------------------------

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )


        # Permite reutilizar a porta rapidamente
        # depois que o servidor for encerrado.
        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )


    # ========================================================
    # ENVIAR MENSAGEM
    # ========================================================

    def send_message(
        self,
        connection,
        message
    ):

        try:

            # "\n" marca o final de cada mensagem.
            connection.sendall(
                (message + "\n").encode()
            )

        except Exception as error:

            print(
                f"Erro ao enviar mensagem: {error}"
            )


    # ========================================================
    # BROADCAST
    # ========================================================
    #
    # Envia uma mensagem para vários jogadores.
    #
    # Se sender for informado, esse cliente não recebe.
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
    #
    # Quando Lucas entra e Math já está conectado,
    # Lucas precisa descobrir:
    #
    # - nome de Math
    # - personagem de Math
    # - posição de Math
    #
    # Agora o protocolo é:
    #
    # PLAYER|nome|personagem|x|y
    #
    # Exemplo:
    #
    # PLAYER|Math|character_2|300|300
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
    # COLISÃO
    # ========================================================

    def is_colliding(
        self,
        x,
        y
    ):

        # Retângulo do jogador.

        player_left = x

        player_top = y

        player_right = (
            x + self.player_size
        )

        player_bottom = (
            y + self.player_size
        )


        # Compara o jogador com cada obstáculo.

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
    # PROCESSAR MENSAGEM DO JOGADOR
    # ========================================================

    def process_message(
        self,
        connection,
        message
    ):

        # Segurança:
        # só processamos comandos de jogadores registrados.

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
        # CHAT|Olá pessoal!
        #
        # Servidor envia para todos:
        #
        # CHAT|Math|Olá pessoal!
        # ====================================================

        if message.startswith("CHAT|"):

            parts = message.split(
                "|",
                1
            )


            if len(parts) < 2:

                return


            chat_message = parts[1]


            # Não envia mensagem vazia.

            if not chat_message.strip():

                return


            print(
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


        # W
        if message == "MOVE_W":

            new_y -= self.move_speed


        # S
        elif message == "MOVE_S":

            new_y += self.move_speed


        # A
        elif message == "MOVE_A":

            new_x -= self.move_speed


        # D
        elif message == "MOVE_D":

            new_x += self.move_speed


        # Comando desconhecido
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
        #
        # Só atualizamos a posição se ela for válida.
        # ====================================================

        if not self.is_colliding(
            new_x,
            new_y
        ):

            player.set_position(
                new_x,
                new_y
            )


        # Posição oficial depois da validação.

        x, y = player.get_position()


        print(
            f"{player.name} está em "
            f"X={x}, Y={y}"
        )


        # ====================================================
        # SINCRONIZAÇÃO
        # ====================================================
        #
        # Todos recebem a posição oficial.
        #
        # MOVE|Math|310|300
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

        print(
            f"Cliente conectado: {address}"
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
            # ANTES:
            #
            # Math
            #
            # AGORA:
            #
            # LOGIN|Math|character_2
            #
            # Isso permite que o servidor saiba qual
            # personagem foi escolhido.
            # =================================================

            login_complete = False


            while not login_complete:

                data = connection.recv(
                    1024
                )


                if not data:

                    return


                buffer += data.decode()


                # Espera uma mensagem completa.

                if "\n" in buffer:

                    login_message, buffer = (
                        buffer.split(
                            "\n",
                            1
                        )
                    )


                    # Divide:
                    #
                    # LOGIN
                    # Math
                    # character_2

                    parts = login_message.split(
                        "|",
                        2
                    )


                    # Verifica protocolo.

                    if (
                        len(parts) != 3
                        or parts[0] != "LOGIN"
                    ):

                        self.send_message(
                            connection,
                            "ERROR|LOGIN_INVALIDO"
                        )

                        return


                    name = parts[1].strip()

                    character = parts[2].strip()


                    # Nome não pode ser vazio.

                    if not name:

                        self.send_message(
                            connection,
                            "ERROR|NOME_INVALIDO"
                        )

                        return


                    # =================================================
                    # VALIDA PERSONAGEM
                    # =================================================
                    #
                    # O cliente não pode inventar:
                    #
                    # character_999
                    #
                    # Só aceitamos personagens conhecidos.
                    # =================================================

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


            # Adiciona ao servidor.

            with self.lock:

                self.players[
                    connection
                ] = player


            print(
                f"{player.name} entrou no mundo "
                f"usando {player.character}!"
            )


            # =================================================
            # SINCRONIZAÇÃO INICIAL
            # =================================================


            # Primeiro enviamos para o novo jogador
            # quem já estava no servidor.

            self.send_existing_players(
                connection
            )


            # Depois avisamos os outros sobre
            # quem acabou de entrar.
            #
            # ENTER|nome|personagem|x|y

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
            # LOOP PRINCIPAL DO CLIENTE
            # =================================================

            while True:

                data = connection.recv(
                    1024
                )


                if not data:

                    break


                buffer += data.decode()


                # Pode chegar mais de uma mensagem
                # no mesmo pacote TCP.

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
                f"Erro com {address}: {error}"
            )


        finally:

            # =================================================
            # DESCONEXÃO
            # =================================================

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


                # Avisa os outros.

                self.broadcast(
                    f"LEAVE|{player.name}"
                )


                print(
                    f"{player.name} saiu do mundo!"
                )


            try:

                connection.close()

            except Exception:

                pass


    # ========================================================
    # INICIAR SERVIDOR
    # ========================================================

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


                # Cada jogador fica em uma
                # thread independente.

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