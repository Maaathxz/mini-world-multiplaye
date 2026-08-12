import threading


# ==========================================
# PYGAME
# ==========================================

try:

    import pygame


except ImportError:

    raise SystemExit(
        "Pygame é necessário para executar "
        "o jogo. Instale com: "
        "pip install pygame"
    )


# ==========================================
# REDE
# ==========================================

from network import NetworkClient


# ==========================================
# CLASSE GAME
# ==========================================

class Game:

    def __init__(self):

        # ==================================
        # JANELA
        # ==================================

        self.width = 800
        self.height = 600

        self.player_size = 40

        self.fps = 60

        self.move_delay = 100

        self.map_margin = 20


        # ==================================
        # JOGADORES
        # ==================================

        self.players = {}

        self.players_lock = (
            threading.Lock()
        )


        # ==================================
        # CHAT
        # ==================================

        # Histórico das mensagens.
        self.chat_messages = []


        # Texto que está sendo digitado.
        self.chat_input = ""


        # Indica se a caixa está ativa.
        self.chat_active = False


        # Máximo de mensagens exibidas.
        self.max_chat_messages = 5


        # Máximo aproximado de caracteres
        # na mensagem.
        self.max_chat_length = 60


        # ==================================
        # NOME DO JOGADOR
        # ==================================

        self.name = input(
            "Digite o nome do jogador: "
        )


        # ==================================
        # REDE
        # ==================================

        self.network = NetworkClient(
            host="127.0.0.1",
            port=5000
        )


        self.network.set_message_handler(
            self.process_server_message
        )


        if not self.network.connect():

            raise SystemExit(
                "Não foi possível conectar "
                "ao servidor."
            )


        self.network.start_receiving()


        # Envia nome para o servidor
        self.network.send(
            self.name
        )


        # Posição inicial
        self.players[
            self.name
        ] = [
            300,
            300
        ]


        # ==================================
        # PYGAME
        # ==================================

        pygame.init()


        self.screen = (
            pygame.display.set_mode(
                (
                    self.width,
                    self.height
                )
            )
        )


        pygame.display.set_caption(
            "Mini World Multiplayer"
        )


        self.clock = pygame.time.Clock()


        # Fonte dos nomes
        self.font = pygame.font.Font(
            None,
            24
        )


        # Fonte do chat
        self.chat_font = pygame.font.Font(
            None,
            22
        )


        # Fonte menor para instruções
        self.small_font = pygame.font.Font(
            None,
            18
        )


        # ==================================
        # RETÂNGULO DO CHAT
        # ==================================
        # Canto inferior esquerdo.
        # ==================================

        self.chat_rect = pygame.Rect(
            20,
            415,
            340,
            165
        )


        # Área específica onde digitamos.
        self.chat_input_rect = pygame.Rect(
            30,
            540,
            320,
            30
        )


        self.last_move = 0

        self.running = True


    # ======================================
    # PROCESSA MENSAGENS DO SERVIDOR
    # ======================================

    def process_server_message(
        self,
        message
    ):

        parts = message.split("|")


        if not parts:

            return


        command = parts[0]


        # ==================================
        # JOGADOR EXISTENTE
        # ==================================

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


        # ==================================
        # ENTRADA
        # ==================================

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


            self.add_chat_message(
                f"{player_name} entrou no mundo."
            )


        # ==================================
        # MOVIMENTO
        # ==================================

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


        # ==================================
        # CHAT
        # ==================================

        elif command == "CHAT":

            # Usamos maxsplit=2 porque
            # a própria mensagem pode conter
            # outros caracteres "|".
            chat_parts = message.split(
                "|",
                2
            )


            if len(chat_parts) < 3:

                return


            player_name = chat_parts[1]

            text = chat_parts[2]


            self.add_chat_message(
                f"{player_name}: {text}"
            )


        # ==================================
        # SAÍDA
        # ==================================

        elif command == "LEAVE":

            player_name = parts[1]


            with self.players_lock:

                if (
                    player_name
                    in self.players
                ):

                    del self.players[
                        player_name
                    ]


            self.add_chat_message(
                f"{player_name} saiu do mundo."
            )


    # ======================================
    # ADICIONAR MENSAGEM AO CHAT
    # ======================================

    def add_chat_message(
        self,
        message
    ):

        self.chat_messages.append(
            message
        )


        # Mantém apenas as últimas
        # mensagens.
        if (
            len(self.chat_messages)
            > self.max_chat_messages
        ):

            self.chat_messages = (
                self.chat_messages[
                    -self.max_chat_messages:
                ]
            )


    # ======================================
    # ENVIAR CHAT
    # ======================================

    def send_chat_message(self):

        message = (
            self.chat_input.strip()
        )


        if not message:

            return


        self.network.send(
            f"CHAT|{message}"
        )


        # Limpa a caixa depois de enviar.
        self.chat_input = ""


    # ======================================
    # EVENTOS
    # ======================================

    def handle_events(self):

        for event in pygame.event.get():

            # ----------------------------------
            # FECHAR JANELA
            # ----------------------------------

            if event.type == pygame.QUIT:

                self.running = False


            # ----------------------------------
            # CLIQUE DO MOUSE
            # ----------------------------------

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                # Clique esquerdo
                if event.button == 1:

                    # Se clicou na área
                    # de entrada do chat...
                    if (
                        self.chat_input_rect
                        .collidepoint(
                            event.pos
                        )
                    ):

                        self.chat_active = True


                    else:

                        # Clicou fora
                        self.chat_active = False


            # ----------------------------------
            # DIGITAÇÃO
            # ----------------------------------

            elif (
                event.type
                == pygame.KEYDOWN
            ):

                # Só captura texto se
                # o chat estiver ativo.
                if self.chat_active:

                    # ENTER envia
                    if (
                        event.key
                        == pygame.K_RETURN
                    ):

                        self.send_chat_message()


                    # BACKSPACE apaga
                    elif (
                        event.key
                        == pygame.K_BACKSPACE
                    ):

                        self.chat_input = (
                            self.chat_input[:-1]
                        )


                    # ESC cancela
                    elif (
                        event.key
                        == pygame.K_ESCAPE
                    ):

                        self.chat_input = ""

                        self.chat_active = False


                    else:

                        # Adiciona caractere
                        # digitado.
                        if (
                            len(self.chat_input)
                            < self.max_chat_length
                        ):

                            self.chat_input += (
                                event.unicode
                            )


    # ======================================
    # MOVIMENTAÇÃO
    # ======================================

    def handle_input(self):

        # Se o chat estiver ativo,
        # NÃO movimenta o personagem.
        if self.chat_active:

            return


        keys = pygame.key.get_pressed()


        current_time = (
            pygame.time.get_ticks()
        )


        if (
            current_time
            - self.last_move
            < self.move_delay
        ):

            return


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

            self.network.send(
                command
            )


            self.last_move = (
                current_time
            )


    # ======================================
    # MAPA
    # ======================================

    def draw_map(self):

        # Fundo
        self.screen.fill(
            (
                210,
                235,
                255
            )
        )


        # Área principal
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


        # ==================================
        # ÁRVORE 1
        # ==================================

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


        # ==================================
        # ÁRVORE 2
        # ==================================

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


        # ==================================
        # CASA
        # ==================================

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
    # JOGADORES
    # ======================================

    def draw_players(self):

        with self.players_lock:

            for (
                player_name,
                position
            ) in self.players.items():

                x = position[0]
                y = position[1]


                if (
                    player_name
                    == self.name
                ):

                    color = (
                        50,
                        100,
                        230
                    )

                else:

                    color = (
                        230,
                        70,
                        70
                    )


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


                text = self.font.render(
                    player_name,
                    True,
                    (
                        20,
                        20,
                        20
                    )
                )


                text_rect = (
                    text.get_rect(
                        center=(
                            x
                            + self.player_size
                            // 2,

                            y - 12
                        )
                    )
                )


                self.screen.blit(
                    text,
                    text_rect
                )


    # ======================================
    # DESENHA CHAT
    # ======================================

    def draw_chat(self):

        # ----------------------------------
        # FUNDO DO CHAT
        # ----------------------------------

        pygame.draw.rect(
            self.screen,
            (
                245,
                245,
                245
            ),
            self.chat_rect,
            border_radius=10
        )


        # ----------------------------------
        # BORDA
        # ----------------------------------

        pygame.draw.rect(
            self.screen,
            (
                100,
                100,
                100
            ),
            self.chat_rect,
            width=2,
            border_radius=10
        )


        # ----------------------------------
        # TÍTULO
        # ----------------------------------

        title = self.chat_font.render(
            "Chat",
            True,
            (
                30,
                30,
                30
            )
        )


        self.screen.blit(
            title,
            (
                self.chat_rect.x + 10,
                self.chat_rect.y + 8
            )
        )


        # ----------------------------------
        # HISTÓRICO
        # ----------------------------------

        start_y = (
            self.chat_rect.y + 35
        )


        for index, message in enumerate(
            self.chat_messages
        ):

            text = self.small_font.render(
                message,
                True,
                (
                    30,
                    30,
                    30
                )
            )


            self.screen.blit(
                text,
                (
                    self.chat_rect.x + 10,

                    start_y
                    + index * 18
                )
            )


        # ----------------------------------
        # CAIXA DE DIGITAÇÃO
        # ----------------------------------

        # Cor muda quando ativa
        if self.chat_active:

            input_color = (
                255,
                255,
                255
            )

            border_color = (
                50,
                120,
                220
            )


        else:

            input_color = (
                225,
                225,
                225
            )

            border_color = (
                150,
                150,
                150
            )


        pygame.draw.rect(
            self.screen,
            input_color,
            self.chat_input_rect,
            border_radius=5
        )


        pygame.draw.rect(
            self.screen,
            border_color,
            self.chat_input_rect,
            width=2,
            border_radius=5
        )


        # ----------------------------------
        # TEXTO DE ENTRADA
        # ----------------------------------

        if self.chat_input:

            display_text = (
                self.chat_input
            )

            text_color = (
                20,
                20,
                20
            )


        else:

            display_text = (
                "Clique aqui para conversar..."
            )

            text_color = (
                120,
                120,
                120
            )


        input_text = (
            self.small_font.render(
                display_text,
                True,
                text_color
            )
        )


        self.screen.blit(
            input_text,
            (
                self.chat_input_rect.x + 7,
                self.chat_input_rect.y + 7
            )
        )


    # ======================================
    # DESENHAR FRAME
    # ======================================

    def draw(self):

        self.draw_map()

        self.draw_players()

        # Chat por último,
        # para ficar por cima do cenário.
        self.draw_chat()

        pygame.display.flip()


    # ======================================
    # LOOP PRINCIPAL
    # ======================================

    def run(self):

        while self.running:

            self.handle_events()

            self.handle_input()

            self.draw()

            self.clock.tick(
                self.fps
            )


        self.network.disconnect()

        pygame.quit()


# ==========================================
# INÍCIO
# ==========================================

if __name__ == "__main__":

    game = Game()

    game.run()