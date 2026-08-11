# ==========================================
# CLASSE PLAYER
# ==========================================
# Esta classe representa um jogador dentro
# do jogo multiplayer.
#
# Cada jogador possui:
# - nome
# - posição X
# - posição Y
#
# Futuramente podemos adicionar:
# - moedas
# - XP
# - nível
# - inventário
# - direção
# - sprite
# ==========================================


class Player:

    # ======================================
    # MÉTODO CONSTRUTOR
    # ======================================
    # O __init__ é executado automaticamente
    # quando criamos um novo objeto Player.
    #
    # Exemplo:
    #
    # player = Player("Math")
    #
    # Nesse caso:
    # name = "Math"
    # x = 300
    # y = 300
    # ======================================

    def __init__(self, name, x=300, y=300):

        # Nome do jogador
        self.name = name

        # Posição horizontal do jogador
        self.x = x

        # Posição vertical do jogador
        self.y = y


    # ======================================
    # MOVIMENTAÇÃO
    # ======================================
    # Move o jogador somando valores
    # às coordenadas atuais.
    #
    # Exemplos:
    #
    # player.move(10, 0)
    # Move 10 pixels para a direita.
    #
    # player.move(-10, 0)
    # Move 10 pixels para a esquerda.
    #
    # player.move(0, -10)
    # Move 10 pixels para cima.
    # ======================================

    def move(self, dx, dy):

        self.x += dx
        self.y += dy


    # ======================================
    # DEFINIR POSIÇÃO
    # ======================================
    # Permite substituir diretamente
    # as coordenadas atuais do jogador.
    #
    # Exemplo:
    #
    # player.set_position(150, 200)
    # ======================================

    def set_position(self, x, y):

        self.x = x
        self.y = y


    # ======================================
    # OBTER POSIÇÃO
    # ======================================
    # Retorna as coordenadas atuais
    # do jogador.
    #
    # Exemplo:
    #
    # x, y = player.get_position()
    # ======================================

    def get_position(self):

        return self.x, self.y