import threading

# ==========================================
# IMPORTAÇÃO DO PYGAME
# ==========================================

try:
    import pygame  # type: ignore[import]

except ImportError:
    raise SystemExit(
        "Pygame é necessário para executar o jogo. "
        "Instale com: pip install pygame"
    )


# ==========================================
# IMPORTAÇÃO DA REDE
# ==========================================

from network import NetworkClient


# ==========================================
# CLASSE GAME
# ==========================================
# Responsável pela parte visual do jogo.
#
# Funções principais:
# - criar a janela
# - receber comandos do teclado
# - desenhar o mapa
# - desenhar jogadores
# - processar mensagens do servidor
# ==========================================


class Game:

    # ======================================
    # CONSTRUTOR
    # ======================================

    def __init__(self):

        # ----------------------------------
        # CONFIGURAÇÕES DA JANELA
        # ----------------------------------

        self.width = 800
        self.height = 600

        self.player_size = 40

        self.fps = 60

        # Intervalo entre comandos de
        # movimentação enviados ao servidor.
        self.move_delay = 100

        self.map_margin = 20


        # ----------------------------------
        # JOGADORES
        # ----------------------------------

        # Exemplo:
        #
        # {
        #     "Math": [300, 300],
        #     "Lucas": [400, 300]
        # }

        self.players = {}


        # Como uma thread recebe mensagens
        # enquanto o Pygame desenha a tela,
        # usamos um Lock para proteger
        # o dicionário.
        self.players_lock = threading.Lock()


        # ----------------------------------
        # NOME DO JOGADOR
        # ----------------------------------

        self.name = input(
            "Digite o nome do jogador: "
        )


        # ----------------------------------
        # REDE
        # ----------------------------------

        self.network = NetworkClient(
            host="127.0.0.1",
            port=5000
        )


        # Define qual função será chamada
        # quando uma mensagem chegar
        # do servidor.
        self.network.set_message_handler(
            self.process_server_message
        )


        # Tenta conectar ao servidor.
        if not self.network.connect():

            raise SystemExit(
                "Não foi possível conectar "
                "ao servidor."
            )


        # Inicia a thread responsável
        # por receber mensagens.
        self.network.start_receiving()


        # Envia o nome ao servidor.
        self.network.send(
            self.name
        )


        # Adiciona nosso próprio jogador
        # na posição inicial.
        self.players[
            self.name
        ] = [
            300,
            300
        ]


        # ----------------------------------
        # INICIALIZAÇÃO DO PYGAME
        # ----------------------------------

        pygame.init()


        self.screen = pygame.display.set_mode(
            (
                self.width,
                self.height
            )
        )


        pygame.display.set_caption(
            "Mini World Multiplayer"
        )


        self.clock = pygame.time.Clock()


        self.font = pygame.font.Font(
            None,
            24
        )


        # Guarda o momento do último
        # movimento enviado.
        self.last_move = 0


        # Controla o loop do jogo.
        self.running = True


    # ======================================
    # PROCESSA MENSAGEM DO SERVIDOR
    # ======================================

    def process_server_message(
        self,
        message
    ):

        # Exemplo:
        #
        # MOVE|Math|310|300
        #
        # vira:
        #
        # [
        #   "MOVE",
        #   "Math",
        #   "310",
        #   "300"
        # ]

        parts = message.split("|")


        if not parts:
            return


        command = parts[0]


        # ----------------------------------
        # JOGADOR JÁ EXISTENTE
        # ----------------------------------

        if command == "PLAYER":

            player_name = parts[1]

            x = int(parts[2])
            y = int(parts[3])


            with self.players_lock:

                self.players[
                    player_name
                ] = [
                    x,
                    y
                ]


        # ----------------------------------
        # NOVO JOGADOR
        # ----------------------------------

        elif command == "ENTER":

            player_name = parts[1]

            x = int(parts[2])
            y = int(parts[3])


            with self.players_lock:

                self.players[
                    player_name
                ] = [
                    x,
                    y
                ]


            print(
                f"{player_name} entrou no mundo!"
            )


        # ----------------------------------
        # MOVIMENTAÇÃO
        # ----------------------------------

        elif command == "MOVE":

            player_name = parts[1]

            x = int(parts[2])
            y = int(parts[3])


            with self.players_lock:

                self.players[
                    player_name
                ] = [
                    x,
                    y
                ]


        # ----------------------------------
        # JOGADOR SAIU
        # ----------------------------------

        elif command == "LEAVE":

            player_name = parts[1]


            with self.players_lock:

                if player_name in self.players:

                    del self.players[
                        player_name
                    ]


            print(
                f"{player_name} saiu do mundo!"
            )


    # ======================================
    # EVENTOS
    # ======================================

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False


    # ======================================
    # TECLADO
    # ======================================

    def handle_input(self):

        keys = pygame.key.get_pressed()


        current_time = (
            pygame.time.get_ticks()
        )


        # Controla a frequência com que
        # mandamos comandos para o servidor.
        if (
            current_time
            - self.last_move
            < self.move_delay
        ):

            return


        command = None


        # CIMA
        if keys[pygame.K_w]:

            command = "MOVE_W"


        # BAIXO
        elif keys[pygame.K_s]:

            command = "MOVE_S"


        # ESQUERDA
        elif keys[pygame.K_a]:

            command = "MOVE_A"


        # DIREITA
        elif keys[pygame.K_d]:

            command = "MOVE_D"


        if command:

            # Apenas envia o comando.
            #
            # O servidor será responsável
            # por validar:
            #
            # - posição
            # - limites
            # - colisões

            self.network.send(
                command
            )


            self.last_move = (
                current_time
            )


    # ======================================
    # DESENHA O MAPA
    # ======================================

    def draw_map(self):

        # Fundo externo
        self.screen.fill(
            (
                210,
                235,
                255
            )
        )


        # ----------------------------------
        # ÁREA PRINCIPAL DO MAPA
        # ----------------------------------

        pygame.draw.rect(
            self.screen,
            (
                230,
                240,
                250
            ),
            (
                self.map_margin,
                self.map_margin,

                self.width
                - self.map_margin * 2,

                self.height
                - self.map_margin * 2
            )
        )


        # ----------------------------------
        # ÁRVORE 1
        # ----------------------------------

        # Tronco
        pygame.draw.rect(
            self.screen,
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


        # Copa
        pygame.draw.circle(
            self.screen,
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


        # ----------------------------------
        # ÁRVORE 2
        # ----------------------------------

        pygame.draw.rect(
            self.screen,
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
            self.screen,
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


        # ----------------------------------
        # CASA
        # ----------------------------------

        # Corpo
        pygame.draw.rect(
            self.screen,
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
            self.screen,
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
            self.screen,
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


    # ======================================
    # DESENHA OS JOGADORES
    # ======================================

    def draw_players(self):

        with self.players_lock:

            for (
                player_name,
                position
            ) in self.players.items():

                x = position[0]
                y = position[1]


                # Jogador local
                if player_name == self.name:

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


                # ----------------------------------
                # PERSONAGEM TEMPORÁRIO
                # ----------------------------------

                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        x,
                        y,
                        self.player_size,
                        self.player_size
                    ),
                    border_radius=8
                )


                # ----------------------------------
                # NOME
                # ----------------------------------

                text = self.font.render(
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
                        + self.player_size // 2,

                        y - 12
                    )
                )


                self.screen.blit(
                    text,
                    text_rect
                )


    # ======================================
    # DESENHA TELA COMPLETA
    # ======================================

    def draw(self):

        # Primeiro desenha o cenário
        self.draw_map()


        # Depois os jogadores
        self.draw_players()


        # Atualiza a janela
        pygame.display.flip()


    # ======================================
    # LOOP PRINCIPAL
    # ======================================

    def run(self):

        while self.running:

            # Eventos da janela
            self.handle_events()


            # Entrada do teclado
            self.handle_input()


            # Desenho
            self.draw()


            # Limita o FPS
            self.clock.tick(
                self.fps
            )


        # ----------------------------------
        # ENCERRAMENTO
        # ----------------------------------

        self.network.disconnect()

        pygame.quit()


# ==========================================
# INÍCIO DO PROGRAMA
# ==========================================
# Este bloco só é executado quando
# game_client.py é iniciado diretamente.
# ==========================================

if __name__ == "__main__":

    game = Game()

    game.run()