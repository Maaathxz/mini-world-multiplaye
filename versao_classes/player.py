# ==========================================
# CLASSE PLAYER
# ==========================================
# Representa um jogador dentro do jogo.
#
# Agora cada jogador possui:
# - nome
# - personagem escolhido
# - posição X
# - posição Y
# ==========================================


class Player:

    def __init__(
        self,
        name,
        character="character_1",
        x=300,
        y=300
    ):

        # Nome do jogador
        self.name = name

        # Identificador visual do personagem
        self.character = character

        # Posição
        self.x = x
        self.y = y


    def move(self, dx, dy):
        self.x += dx
        self.y += dy


    def set_position(self, x, y):
        self.x = x
        self.y = y


    def get_position(self):
        return self.x, self.y