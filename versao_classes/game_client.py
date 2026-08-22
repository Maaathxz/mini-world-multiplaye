import os
import sys
import json
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
# IMPORTAÇÕES DO PROJETO
# ==========================================

from network import NetworkClient
from login_screen import LoginScreen


# ==========================================
# CAMINHO BASE
# ==========================================
# Permite encontrar config.json tanto
# executando pelo Python quanto pelo .exe.
# ==========================================

def get_base_path():

    if getattr(
        sys,
        "frozen",
        False
    ):

        return os.path.dirname(
            sys.executable
        )


    return os.path.dirname(
        os.path.abspath(
            __file__
        )
    )


# ==========================================
# CARREGAR CONFIGURAÇÃO
# ==========================================

def load_config():

    base_path = get_base_path()


    config_path = os.path.join(
        base_path,
        "config.json"
    )


    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


# ==========================================
# CLASSE GAME
# ==========================================

class Game:

    def __init__(self):

        # ==================================
        # CONFIGURAÇÕES DA JANELA
        # ==================================

        self.width = 800

        self.height = 600

        self.player_size = 40

        self.fps = 60

        self.move_delay = 100

        self.map_margin = 20


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


        self.clock = (
            pygame.time.Clock()
        )


        self.font = (
            pygame.font.Font(
                None,
                24
            )
        )


        self.chat_font = (
            pygame.font.Font(
                None,
                22
            )
        )


        self.small_font = (
            pygame.font.Font(
                None,
                18
            )
        )


        # ==================================
        # TELA DE LOGIN
        # ==================================

        self.login_screen = LoginScreen(
            self.screen,
            self.width,
            self.height
        )


        # ==================================
        # DADOS DO JOGADOR
        # ==================================

        self.name = None

        self.character = None


        # ==================================
        # JOGADORES ONLINE
        # ==================================

        self.players = {}


        self.players_lock = (
            threading.Lock()
        )


        # ==================================
        # REDE
        # ==================================

        self.network = None

        self.connected = False


        # ==================================
        # CONFIGURAÇÃO
        # ==================================

        try:

            self.config = load_config()


        except FileNotFoundError:

            raise SystemExit(
                "Arquivo config.json não encontrado.\n"
                "Coloque o config.json na mesma pasta "
                "do game_client.exe."
            )


        except json.JSONDecodeError:

            raise SystemExit(
                "O arquivo config.json possui "
                "um formato inválido."
            )


        # ==================================
        # CHAT
        # ==================================

        self.chat_messages = []

        self.chat_input = ""

        self.chat_active = False

        self.max_chat_messages = 5

        self.max_chat_length = 60


        self.chat_rect = pygame.Rect(
            20,
            415,
            340,
            165
        )


        self.chat_input_rect = (
            pygame.Rect(
                30,
                540,
                320,
                30
            )
        )


        # ==================================
        # CONTROLE
        # ==================================

        self.last_move = 0

        self.running = True

        self.state = "login"


    # ======================================
    # SERVIDOR DESCONECTOU
    # ======================================
    # Esta função é chamada automaticamente
    # pelo NetworkClient quando o servidor
    # fecha ou a conexão é perdida.
    # ======================================

    def server_disconnected(self):

        # Se o próprio jogo já estiver
        # fechando, não precisamos repetir.
        if not self.running:

            return


        print(
            "Conexão com o servidor "
            "foi encerrada."
        )


        self.connected = False


        # Encerra o loop principal
        # do Pygame.
        self.running = False


    # ======================================
    # CONECTAR AO SERVIDOR
    # ======================================

    def connect_to_server(self):

        server_ip = (
            self.config[
                "server_ip"
            ]
        )


        server_port = (
            self.config[
                "server_port"
            ]
        )


        # ==================================
        # CRIA CLIENTE DE REDE
        # ==================================

        self.network = (
            NetworkClient(
                host=server_ip,
                port=server_port
            )
        )


        # Mensagens recebidas
        self.network.set_message_handler(
            self.process_server_message
        )


        # ==================================
        # CALLBACK DE DESCONEXÃO
        # ==================================
        # Quando o servidor fechar,
        # NetworkClient chama:
        #
        # self.server_disconnected()
        # ==================================

        self.network.set_disconnect_handler(
            self.server_disconnected
        )


        # ==================================
        # CONECTAR
        # ==================================

        if not self.network.connect():

            print(
                "Não foi possível conectar "
                "ao servidor."
            )

            return False


        # Thread de recebimento
        self.network.start_receiving()


        # ==================================
        # LOGIN
        # ==================================

        self.network.send(

            (
                f"LOGIN|"
                f"{self.name}|"
                f"{self.character}"
            )
        )


        self.connected = True


        # ==================================
        # JOGADOR LOCAL
        # ==================================

        self.players[
            self.name
        ] = {

            "x": 300,

            "y": 300,

            "character":
            self.character
        }


        print(
            f"{self.name} entrou como "
            f"{self.character}"
        )


        return True


    # ======================================
    # PROCESSAR MENSAGEM DO SERVIDOR
    # ======================================

    def process_server_message(
        self,
        message
    ):

        parts = message.split(
            "|"
        )


        if not parts:

            return


        command = parts[0]


        # ==================================
        # PLAYER
        # ==================================

        if command == "PLAYER":

            if len(parts) < 5:

                return


            player_name = parts[1]

            character = parts[2]

            x = int(parts[3])

            y = int(parts[4])


            with self.players_lock:

                self.players[
                    player_name
                ] = {

                    "x": x,

                    "y": y,

                    "character":
                    character
                }


        # ==================================
        # ENTER
        # ==================================

        elif command == "ENTER":

            if len(parts) < 5:

                return


            player_name = parts[1]

            character = parts[2]

            x = int(parts[3])

            y = int(parts[4])


            with self.players_lock:

                self.players[
                    player_name
                ] = {

                    "x": x,

                    "y": y,

                    "character":
                    character
                }


            self.add_chat_message(
                f"{player_name} "
                f"entrou no mundo."
            )


        # ==================================
        # MOVE
        # ==================================

        elif command == "MOVE":

            if len(parts) < 4:

                return


            player_name = parts[1]

            x = int(parts[2])

            y = int(parts[3])


            with self.players_lock:

                if (
                    player_name
                    in self.players
                ):

                    self.players[
                        player_name
                    ]["x"] = x


                    self.players[
                        player_name
                    ]["y"] = y


        # ==================================
        # CHAT
        # ==================================

        elif command == "CHAT":

            chat_parts = (
                message.split(
                    "|",
                    2
                )
            )


            if (
                len(chat_parts)
                < 3
            ):

                return


            player_name = (
                chat_parts[1]
            )


            text = (
                chat_parts[2]
            )


            self.add_chat_message(
                f"{player_name}: "
                f"{text}"
            )


        # ==================================
        # LEAVE
        # ==================================

        elif command == "LEAVE":

            if len(parts) < 2:

                return


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
                f"{player_name} "
                f"saiu do mundo."
            )


        # ==================================
        # ERROR
        # ==================================

        elif command == "ERROR":

            error_message = (

                parts[1]

                if len(parts) > 1

                else "ERRO_DESCONHECIDO"
            )


            print(
                f"Erro do servidor: "
                f"{error_message}"
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


        if (
            self.network
            and self.connected
        ):

            self.network.send(
                f"CHAT|{message}"
            )


        self.chat_input = ""


    # ======================================
    # EVENTOS DA TELA DE LOGIN
    # ======================================

    def handle_login_events(
        self,
        event
    ):

        self.login_screen.handle_event(
            event
        )


        if self.login_screen.finished:

            self.name = (

                self.login_screen
                .player_name
                .strip()
            )


            self.character = (

                self.login_screen
                .selected_character
            )


            if self.connect_to_server():

                self.state = "game"


            else:

                self.login_screen.finished = (
                    False
                )


    # ======================================
    # EVENTOS DO JOGO
    # ======================================

    def handle_game_events(
        self,
        event
    ):

        # ==================================
        # MOUSE
        # ==================================

        if (
            event.type
            == pygame.MOUSEBUTTONDOWN
        ):

            if event.button == 1:

                if (
                    self.chat_input_rect
                    .collidepoint(
                        event.pos
                    )
                ):

                    self.chat_active = True


                else:

                    self.chat_active = False


        # ==================================
        # TECLADO DO CHAT
        # ==================================

        elif (
            event.type
            == pygame.KEYDOWN
        ):

            if self.chat_active:

                # ENTER
                if (
                    event.key
                    == pygame.K_RETURN
                ):

                    self.send_chat_message()


                # BACKSPACE
                elif (
                    event.key
                    == pygame.K_BACKSPACE
                ):

                    self.chat_input = (
                        self.chat_input[:-1]
                    )


                # ESC
                elif (
                    event.key
                    == pygame.K_ESCAPE
                ):

                    self.chat_input = ""

                    self.chat_active = False


                else:

                    if (
                        len(self.chat_input)
                        < self.max_chat_length
                    ):

                        self.chat_input += (
                            event.unicode
                        )


    # ======================================
    # EVENTOS GERAIS
    # ======================================

    def handle_events(self):

        for event in pygame.event.get():

            # ==================================
            # FECHAR JANELA
            # ==================================

            if event.type == pygame.QUIT:

                self.running = False

                continue


            # ==================================
            # LOGIN
            # ==================================

            if self.state == "login":

                self.handle_login_events(
                    event
                )


            # ==================================
            # JOGO
            # ==================================

            elif self.state == "game":

                self.handle_game_events(
                    event
                )


    # ======================================
    # MOVIMENTAÇÃO
    # ======================================

    def handle_input(self):

        if self.state != "game":

            return


        # Enquanto escreve no chat,
        # não movimenta.
        if self.chat_active:

            return


        if (
            not self.network
            or not self.connected
        ):

            return


        keys = (
            pygame.key.get_pressed()
        )


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

        self.screen.fill(
            (
                210,
                235,
                255
            )
        )


        # Área jogável
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
    # DESENHAR JOGADORES
    # ======================================

    def draw_players(self):

        character_colors = {

            "character_1": (
                60,
                120,
                230
            ),

            "character_2": (
                220,
                80,
                90
            ),

            "character_3": (
                70,
                180,
                110
            )
        }


        with self.players_lock:

            for (
                player_name,
                player_data
            ) in self.players.items():


                x = (
                    player_data["x"]
                )


                y = (
                    player_data["y"]
                )


                character = (
                    player_data[
                        "character"
                    ]
                )


                color = (
                    character_colors.get(
                        character,
                        (
                            100,
                            100,
                            100
                        )
                    )
                )


                # Personagem temporário
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


                # Nome
                text = (
                    self.font.render(
                        player_name,
                        True,
                        (
                            20,
                            20,
                            20
                        )
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
    # CHAT
    # ======================================

    def draw_chat(self):

        # Fundo
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


        # Borda
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


        # Título
        title = (
            self.chat_font.render(
                "Chat",
                True,
                (
                    30,
                    30,
                    30
                )
            )
        )


        self.screen.blit(
            title,
            (
                self.chat_rect.x + 10,
                self.chat_rect.y + 8
            )
        )


        # Histórico
        start_y = (
            self.chat_rect.y + 35
        )


        for (
            index,
            message
        ) in enumerate(
            self.chat_messages
        ):

            text = (
                self.small_font.render(
                    message,
                    True,
                    (
                        30,
                        30,
                        30
                    )
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


        # ==================================
        # CAMPO DE DIGITAÇÃO
        # ==================================

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


        # Texto ou placeholder
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
    # DESENHAR JOGO
    # ======================================

    def draw_game(self):

        self.draw_map()

        self.draw_players()

        self.draw_chat()


    # ======================================
    # DESENHAR TELA
    # ======================================

    def draw(self):

        if self.state == "login":

            self.login_screen.draw()


        elif self.state == "game":

            self.draw_game()


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


        # ==================================
        # ENCERRAMENTO
        # ==================================

        if self.network:

            self.network.disconnect()


        pygame.quit()


# ==========================================
# INÍCIO
# ==========================================

if __name__ == "__main__":

    game = Game()

    game.run()