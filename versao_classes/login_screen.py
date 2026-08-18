import pygame


# ==========================================
# CLASSE LOGIN SCREEN
# ==========================================
# Tela inicial responsável por:
# - receber nome do jogador
# - selecionar personagem
# - confirmar entrada no jogo
# ==========================================


class LoginScreen:

    def __init__(
        self,
        screen,
        width,
        height
    ):

        self.screen = screen

        self.width = width
        self.height = height


        # ==================================
        # FONTES
        # ==================================

        self.title_font = pygame.font.Font(
            None,
            52
        )

        self.font = pygame.font.Font(
            None,
            30
        )

        self.small_font = pygame.font.Font(
            None,
            22
        )


        # ==================================
        # NOME
        # ==================================

        self.player_name = ""

        self.name_active = False


        self.name_rect = pygame.Rect(
            220,
            150,
            360,
            45
        )


        # ==================================
        # PERSONAGENS
        # ==================================

        self.characters = [
            "character_1",
            "character_2",
            "character_3"
        ]


        self.selected_character = (
            "character_1"
        )


        # Retângulos clicáveis
        self.character_rects = []


        start_x = 180

        gap = 140


        for index in range(
            len(self.characters)
        ):

            rect = pygame.Rect(

                start_x
                + index * gap,

                280,

                100,
                120
            )


            self.character_rects.append(
                rect
            )


        # ==================================
        # BOTÃO ENTRAR
        # ==================================

        self.enter_button = pygame.Rect(
            280,
            470,
            240,
            55
        )


        self.finished = False


    # ======================================
    # EVENTOS
    # ======================================

    def handle_event(
        self,
        event
    ):

        # ----------------------------------
        # CLIQUE
        # ----------------------------------

        if (
            event.type
            == pygame.MOUSEBUTTONDOWN
        ):

            if event.button == 1:

                # Campo do nome
                if self.name_rect.collidepoint(
                    event.pos
                ):

                    self.name_active = True


                else:

                    self.name_active = False


                # Seleção de personagem
                for index, rect in enumerate(
                    self.character_rects
                ):

                    if rect.collidepoint(
                        event.pos
                    ):

                        self.selected_character = (
                            self.characters[
                                index
                            ]
                        )


                # Botão entrar
                if self.enter_button.collidepoint(
                    event.pos
                ):

                    if self.player_name.strip():

                        self.finished = True


        # ----------------------------------
        # TECLADO
        # ----------------------------------

        elif (
            event.type
            == pygame.KEYDOWN
        ):

            if self.name_active:

                if (
                    event.key
                    == pygame.K_BACKSPACE
                ):

                    self.player_name = (
                        self.player_name[:-1]
                    )


                elif (
                    event.key
                    == pygame.K_RETURN
                ):

                    if self.player_name.strip():

                        self.finished = True


                else:

                    if (
                        len(self.player_name)
                        < 16
                    ):

                        self.player_name += (
                            event.unicode
                        )


    # ======================================
    # DESENHO
    # ======================================

    def draw(self):

        # Fundo
        self.screen.fill(
            (
                215,
                235,
                250
            )
        )


        # ==================================
        # TÍTULO
        # ==================================

        title = self.title_font.render(
            "MINI WORLD",
            True,
            (
                30,
                60,
                90
            )
        )


        title_rect = title.get_rect(
            center=(
                self.width // 2,
                70
            )
        )


        self.screen.blit(
            title,
            title_rect
        )


        # ==================================
        # CAMPO DO NOME
        # ==================================

        label = self.font.render(
            "Nome do jogador",
            True,
            (
                30,
                30,
                30
            )
        )


        self.screen.blit(
            label,
            (
                self.name_rect.x,
                115
            )
        )


        if self.name_active:

            border_color = (
                50,
                120,
                220
            )

        else:

            border_color = (
                120,
                120,
                120
            )


        pygame.draw.rect(
            self.screen,
            (
                255,
                255,
                255
            ),
            self.name_rect,
            border_radius=8
        )


        pygame.draw.rect(
            self.screen,
            border_color,
            self.name_rect,
            width=2,
            border_radius=8
        )


        if self.player_name:

            name_text = self.font.render(
                self.player_name,
                True,
                (
                    20,
                    20,
                    20
                )
            )

        else:

            name_text = (
                self.small_font.render(
                    "Clique aqui e digite seu nome...",
                    True,
                    (
                        140,
                        140,
                        140
                    )
                )
            )


        self.screen.blit(
            name_text,
            (
                self.name_rect.x + 10,
                self.name_rect.y + 10
            )
        )


        # ==================================
        # TEXTO DE SELEÇÃO
        # ==================================

        select_text = self.font.render(
            "Escolha seu personagem",
            True,
            (
                30,
                30,
                30
            )
        )


        self.screen.blit(
            select_text,
            (
                270,
                230
            )
        )


        # ==================================
        # CARDS
        # ==================================

        colors = [

            (
                70,
                130,
                230
            ),

            (
                220,
                80,
                90
            ),

            (
                80,
                180,
                110
            )
        ]


        for index, rect in enumerate(
            self.character_rects
        ):

            character = (
                self.characters[
                    index
                ]
            )


            # Selecionado
            if (
                character
                == self.selected_character
            ):

                border_color = (
                    255,
                    190,
                    40
                )

                border_width = 5


            else:

                border_color = (
                    100,
                    100,
                    100
                )

                border_width = 2


            pygame.draw.rect(
                self.screen,
                (
                    245,
                    245,
                    245
                ),
                rect,
                border_radius=10
            )


            pygame.draw.rect(
                self.screen,
                border_color,
                rect,
                width=border_width,
                border_radius=10
            )


            # Placeholder visual
            pygame.draw.circle(

                self.screen,

                colors[index],

                (
                    rect.centerx,
                    rect.y + 45
                ),

                25
            )


            # Corpo
            pygame.draw.rect(

                self.screen,

                colors[index],

                (
                    rect.centerx - 20,
                    rect.y + 65,
                    40,
                    35
                ),

                border_radius=8
            )


            # Nome temporário
            text = self.small_font.render(
                f"Personagem {index + 1}",
                True,
                (
                    30,
                    30,
                    30
                )
            )


            text_rect = text.get_rect(
                center=(
                    rect.centerx,
                    rect.bottom - 12
                )
            )


            self.screen.blit(
                text,
                text_rect
            )


        # ==================================
        # BOTÃO ENTRAR
        # ==================================

        can_enter = bool(
            self.player_name.strip()
        )


        if can_enter:

            button_color = (
                60,
                150,
                90
            )


        else:

            button_color = (
                150,
                150,
                150
            )


        pygame.draw.rect(
            self.screen,
            button_color,
            self.enter_button,
            border_radius=12
        )


        button_text = self.font.render(
            "ENTRAR NO MUNDO",
            True,
            (
                255,
                255,
                255
            )
        )


        button_rect = (
            button_text.get_rect(
                center=self.enter_button.center
            )
        )


        self.screen.blit(
            button_text,
            button_rect
        )


        # ==================================
        # PERSONAGEM SELECIONADO
        # ==================================

        selected_text = (
            self.small_font.render(
                (
                    "Selecionado: "
                    f"{self.selected_character}"
                ),
                True,
                (
                    70,
                    70,
                    70
                )
            )
        )


        selected_rect = (
            selected_text.get_rect(
                center=(
                    self.width // 2,
                    430
                )
            )
        )


        self.screen.blit(
            selected_text,
            selected_rect
        )