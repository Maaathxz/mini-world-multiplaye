import socket
import threading


# ==========================================
# CLASSE NETWORK CLIENT
# ==========================================
# Esta classe cuida de toda a comunicação
# entre o cliente do jogo e o servidor.
#
# Responsabilidades:
# - conectar ao servidor
# - enviar mensagens
# - receber mensagens
# - manter uma thread de recebimento
# - encerrar a conexão
# ==========================================


class NetworkClient:

    # ======================================
    # CONSTRUTOR
    # ======================================
    # Define o IP e a porta do servidor.
    # ======================================

    def __init__(
        self,
        host="127.0.0.1",
        port=5000
    ):

        # Endereço IP do servidor.
        self.host = host

        # Porta do servidor.
        self.port = port

        # Cria um socket IPv4 utilizando TCP.
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        # Controla se a conexão está ativa.
        self.connected = False

        # Função que será chamada quando
        # uma mensagem chegar do servidor.
        self.message_handler = None


    # ======================================
    # CONECTAR AO SERVIDOR
    # ======================================

    def connect(self):

        try:

            # Tenta estabelecer conexão
            # com o servidor.
            self.socket.connect(
                (
                    self.host,
                    self.port
                )
            )

            self.connected = True

            print(
                f"Conectado ao servidor "
                f"{self.host}:{self.port}"
            )

            return True


        except Exception as error:

            print(
                f"Erro ao conectar ao servidor: "
                f"{error}"
            )

            return False


    # ======================================
    # DEFINIR TRATADOR DE MENSAGENS
    # ======================================
    # Essa função recebe outra função como
    # parâmetro.
    #
    # No game_client.py usaremos:
    #
    # self.network.set_message_handler(
    #     self.process_server_message
    # )
    #
    # Assim, quando uma mensagem chegar,
    # NetworkClient chama automaticamente
    # process_server_message().
    # ======================================

    def set_message_handler(
        self,
        handler
    ):

        self.message_handler = handler


    # ======================================
    # ENVIAR MENSAGEM
    # ======================================

    def send(
        self,
        message
    ):

        # Se não estiver conectado,
        # não tenta enviar.
        if not self.connected:

            return


        try:

            # Adicionamos "\n" no final.
            #
            # Isso permite separar mensagens
            # dentro do fluxo TCP.
            self.socket.sendall(
                (
                    message + "\n"
                ).encode()
            )


        except Exception as error:

            print(
                f"Erro ao enviar mensagem: "
                f"{error}"
            )


    # ======================================
    # LOOP DE RECEBIMENTO
    # ======================================
    # Esta função ficará executando
    # constantemente em uma thread.
    #
    # Ela recebe dados do servidor e
    # separa as mensagens usando "\n".
    # ======================================

    def receive_loop(self):

        # Buffer temporário utilizado
        # para armazenar dados recebidos.
        buffer = ""


        while self.connected:

            try:

                # Aguarda dados do servidor.
                data = self.socket.recv(
                    1024
                )


                # Se recv() retornar vazio,
                # significa que o servidor
                # encerrou a conexão.
                if not data:

                    print(
                        "Servidor encerrou "
                        "a conexão."
                    )

                    break


                # Converte bytes para texto
                # e adiciona ao buffer.
                buffer += data.decode()


                # Pode haver várias mensagens
                # dentro de um único recv().
                while "\n" in buffer:

                    message, buffer = (
                        buffer.split(
                            "\n",
                            1
                        )
                    )


                    # Ignora mensagens vazias.
                    if not message:

                        continue


                    # Se existir uma função
                    # configurada para receber
                    # mensagens...
                    if self.message_handler:

                        self.message_handler(
                            message
                        )


            except Exception as error:

                if self.connected:

                    print(
                        f"Erro ao receber dados: "
                        f"{error}"
                    )

                break


        # Se saiu do loop, considera
        # a conexão encerrada.
        self.connected = False


    # ======================================
    # INICIAR THREAD DE RECEBIMENTO
    # ======================================

    def start_receiving(self):

        # Cria uma thread responsável
        # exclusivamente por receber dados
        # do servidor.
        receive_thread = threading.Thread(
            target=self.receive_loop,
            daemon=True
        )

        # Inicia a thread.
        receive_thread.start()


    # ======================================
    # DESCONECTAR
    # ======================================

    def disconnect(self):

        self.connected = False


        try:

            # Fecha o socket.
            self.socket.close()


        except Exception:

            pass


        print(
            "Conexão encerrada."
        )