import socket
import threading

from player import Player


# ==========================================
# CLASSE GAME SERVER
# ==========================================
# Esta classe representa o servidor principal
# do jogo multiplayer.
#
# Responsabilidades:
# - Criar e iniciar o servidor TCP
# - Aceitar conexões de clientes
# - Criar jogadores
# - Receber comandos
# - Processar movimentação
# - Validar colisões
# - Sincronizar posições
# - Avisar entrada e saída de jogadores
# ==========================================


class GameServer:

    # ======================================
    # CONSTRUTOR
    # ======================================
    # Define as configurações iniciais do
    # servidor e cria as estruturas usadas
    # durante a execução.
    # ======================================

    def __init__(
        self,
        host="0.0.0.0",
        port=5000
    ):

        # Endereço em que o servidor
        # aceitará conexões.
        self.host = host

        # Porta utilizada pelo servidor.
        self.port = port


        # ==================================
        # CONFIGURAÇÕES DO JOGO
        # ==================================

        # Quantidade de pixels movimentados
        # a cada comando recebido.
        self.move_speed = 10

        # Dimensões do mapa.
        self.map_width = 800
        self.map_height = 600

        # Tamanho atual do personagem.
        self.player_size = 40

        # Distância mínima das bordas.
        self.map_margin = 20


        # ==================================
        # CLIENTES E JOGADORES
        # ==================================

        # Guarda os sockets dos clientes
        # atualmente conectados.
        self.clients = []

        # Associa cada conexão a um objeto
        # Player.
        #
        # Exemplo:
        #
        # {
        #     conexao_1: Player("Math"),
        #     conexao_2: Player("Lucas")
        # }
        self.players = {}


        # ==================================
        # LOCK
        # ==================================
        # Como várias threads podem acessar
        # self.players ao mesmo tempo,
        # utilizamos um Lock para evitar
        # alterações simultâneas perigosas.
        # ==================================

        self.lock = threading.Lock()


        # ==================================
        # OBSTÁCULOS DO MAPA
        # ==================================
        # Cada obstáculo possui:
        #
        # (x, y, largura, altura)
        #
        # Posteriormente isso pode ser
        # movido para uma classe Map.
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


        # Lista geral das áreas que possuem
        # colisão.
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


        # Permite reutilizar a porta
        # rapidamente após reiniciar
        # o servidor.
        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )


    # ======================================
    # ENVIA UMA MENSAGEM
    # ======================================
    # Toda mensagem termina com "\n".
    #
    # Isso é importante porque TCP trabalha
    # com um fluxo contínuo de bytes.
    #
    # O "\n" funciona como nosso separador
    # de mensagens.
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
    # Envia uma mensagem para vários
    # clientes conectados.
    #
    # O parâmetro sender pode ser usado
    # para não enviar novamente ao cliente
    # que originou a mensagem.
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
    # Quando um novo jogador entra,
    # precisamos informar a ele quem já
    # estava conectado e onde cada pessoa
    # está no mapa.
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
    # Retorna True se o jogador estiver
    # tentando ocupar uma região bloqueada.
    # ======================================

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


        # Verifica todos os obstáculos.
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


            # Verificação de sobreposição
            # entre dois retângulos.
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
    # PROCESSA MOVIMENTAÇÃO
    # ======================================
    # Recebe um comando enviado pelo
    # cliente e calcula a nova posição.
    #
    # O servidor é a autoridade.
    #
    # O cliente não decide oficialmente
    # onde está.
    # ======================================

    def process_message(
        self,
        connection,
        message
    ):

        # Verifica se existe jogador
        # associado à conexão.
        if connection not in self.players:

            return


        player = self.players[
            connection
        ]


        # Guarda a posição atual.
        old_x = player.x
        old_y = player.y


        # Começamos assumindo que a
        # posição continuará igual.
        new_x = old_x
        new_y = old_y


        # ==================================
        # COMANDOS DE MOVIMENTO
        # ==================================

        if message == "MOVE_W":

            new_y -= self.move_speed


        elif message == "MOVE_S":

            new_y += self.move_speed


        elif message == "MOVE_A":

            new_x -= self.move_speed


        elif message == "MOVE_D":

            new_x += self.move_speed


        else:

            # Se ainda não for um comando
            # conhecido, não fazemos nada.
            #
            # Futuramente aqui entrarão:
            #
            # CHAT
            # COIN
            # INTERACT
            # etc.
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
        # COLISÃO
        # ==================================

        if not self.is_colliding(
            new_x,
            new_y
        ):

            # Utilizamos o método da classe
            # Player para alterar a posição.
            player.set_position(
                new_x,
                new_y
            )


        # ==================================
        # POSIÇÃO OFICIAL
        # ==================================

        x, y = player.get_position()


        print(
            f"{player.name} está em "
            f"X={x}, Y={y}"
        )


        # ==================================
        # SINCRONIZAÇÃO
        # ==================================
        # Enviamos a posição oficial
        # para TODOS os clientes.
        #
        # Inclusive para o próprio jogador,
        # porque é o servidor que determina
        # a posição válida.
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
    # ATENDE UM CLIENTE
    # ======================================
    # Cada jogador conectado executará
    # esta função em sua própria thread.
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


        # Adiciona a conexão.
        self.clients.append(
            connection
        )


        # Buffer utilizado para separar
        # mensagens TCP.
        buffer = ""


        name = None


        try:

            # ==================================
            # RECEBE O NOME
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
            # CRIA OBJETO PLAYER
            # ==================================

            player = Player(
                name=name,
                x=300,
                y=300
            )


            # Associa conexão → jogador.
            with self.lock:

                self.players[
                    connection
                ] = player


            print(
                f"{player.name} "
                f"entrou no mundo!"
            )


            # ==================================
            # INFORMA JOGADORES EXISTENTES
            # ==================================

            self.send_existing_players(
                connection
            )


            # ==================================
            # AVISA A ENTRADA
            # ==================================

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


                # Pode haver mais de uma
                # mensagem no mesmo recv().
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

            # ==================================
            # REMOVE CLIENTE
            # ==================================

            if connection in self.clients:

                self.clients.remove(
                    connection
                )


            # ==================================
            # REMOVE JOGADOR
            # ==================================

            if connection in self.players:

                player = self.players[
                    connection
                ]


                with self.lock:

                    del self.players[
                        connection
                    ]


                # Avisa os demais.
                self.broadcast(
                    f"LEAVE|{player.name}"
                )


                print(
                    f"{player.name} "
                    f"saiu do mundo!"
                )


            # Fecha a conexão.
            connection.close()


    # ======================================
    # INICIA O SERVIDOR
    # ======================================
    # Configura IP/porta, inicia o listen()
    # e fica continuamente aceitando novos
    # jogadores.
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


        # ==================================
        # LOOP PRINCIPAL DO SERVIDOR
        # ==================================

        while True:

            try:

                # Aguarda um cliente.
                connection, address = (
                    self.server_socket.accept()
                )


                # Cria uma thread exclusiva
                # para atender esse cliente.
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

                break


            except Exception as error:

                print(
                    f"Erro no servidor: "
                    f"{error}"
                )


        # Fecha o socket principal.
        self.server_socket.close()