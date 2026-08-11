# ==========================================
# ARQUIVO PRINCIPAL DO SERVIDOR
# ==========================================
# Este arquivo apenas cria uma instância
# de GameServer e inicia o servidor.
# ==========================================

from game_server import GameServer


# Cria o objeto servidor
server = GameServer()


# Inicia o servidor
server.start()