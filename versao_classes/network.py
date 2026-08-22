import socket
import threading


# ==========================================
# CLASSE NETWORK CLIENT
# ==========================================
# Responsável pela comunicação de rede
# entre o cliente e o servidor.
#
# Agora também avisa o jogo quando
# a conexão com o servidor for encerrada.
# ==========================================


class NetworkClient:

    # ======================================
    # CONSTRUTOR
    # ======================================

    def __init__(
        self,
        host="127.0.0.1",
        port=5000
    ):

        # IP do servidor
        self.host = host

        # Porta do servidor
        self.port = port


        # Cria socket TCP IPv4
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )


        # Estado da conexão
        self.connected = False


        # Função chamada quando
        # uma mensagem chega.
        self.message_handler = None


        # Função chamada quando
        # o servidor desconecta.
        self.disconnect_handler = None


    # ======================================
    # CONECTAR
    # ======================================

    def connect(self):

        try:

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
                f"Erro ao conectar: {error}"
            )

            return False


    # ======================================
    # CONFIGURAR TRATADOR DE MENSAGENS
    # ======================================

    def set_message_handler(
        self,
        handler
    ):

        self.message_handler = handler


    # ======================================
    # CONFIGURAR TRATADOR DE DESCONEXÃO
    # ======================================
    # Recebe uma função que será chamada
    # quando o servidor encerrar a conexão.
    # ======================================

    def set_disconnect_handler(
        self,
        handler
    ):

        self.disconnect_handler = handler


    # ======================================
    # ENVIAR MENSAGEM
    # ======================================

    def send(
        self,
        message
    ):

        if not self.connected:

            return


        try:

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
    # RECEBER MENSAGENS
    # ======================================

    def receive_loop(self):

        buffer = ""


        while self.connected:

            try:

                data = self.socket.recv(
                    1024
                )


                # Se não vier nenhum dado,
                # o servidor encerrou a conexão.
                if not data:

                    print(
                        "Servidor encerrou "
                        "a conexão."
                    )

                    break


                buffer += (
                    data.decode()
                )


                # TCP é um fluxo contínuo.
                # O "\n" separa mensagens.
                while "\n" in buffer:

                    (
                        message,
                        buffer
                    ) = buffer.split(
                        "\n",
                        1
                    )


                    if (
                        message
                        and self.message_handler
                    ):

                        self.message_handler(
                            message
                        )


            except Exception as error:

                if self.connected:

                    print(
                        f"Erro ao receber: "
                        f"{error}"
                    )


                break


        # ==================================
        # CONEXÃO ENCERRADA
        # ==================================

        self.connected = False


        # Avisa o jogo.
        if self.disconnect_handler:

            self.disconnect_handler()


    # ======================================
    # THREAD DE RECEBIMENTO
    # ======================================

    def start_receiving(self):

        thread = threading.Thread(
            target=self.receive_loop,
            daemon=True
        )


        thread.start()


    # ======================================
    # DESCONECTAR MANUALMENTE
    # ======================================

    def disconnect(self):

        # Marca como desconectado antes
        # de fechar o socket.
        self.connected = False


        try:

            self.socket.shutdown(
                socket.SHUT_RDWR
            )

        except Exception:

            pass


        try:

            self.socket.close()

        except Exception:

            pass


        print(
            "Conexão encerrada."
        )