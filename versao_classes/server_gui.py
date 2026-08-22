import threading
import tkinter as tk
from tkinter import scrolledtext

from game_server import GameServer


class ServerGUI:

    def __init__(self):

        # ==================================
        # JANELA PRINCIPAL
        # ==================================

        self.root = tk.Tk()

        self.root.title(
            "Mini World Server"
        )

        self.root.geometry(
            "520x420"
        )

        self.root.resizable(
            False,
            False
        )


        # ==================================
        # TÍTULO
        # ==================================

        title = tk.Label(
            self.root,
            text="MINI WORLD SERVER",
            font=(
                "Arial",
                20,
                "bold"
            )
        )

        title.pack(
            pady=15
        )


        # ==================================
        # STATUS
        # ==================================

        self.status_label = tk.Label(
            self.root,
            text="Status: OFFLINE",
            font=(
                "Arial",
                12,
                "bold"
            )
        )

        self.status_label.pack(
            pady=5
        )


        # ==================================
        # PORTA
        # ==================================

        self.port_label = tk.Label(
            self.root,
            text="Porta: 5000"
        )

        self.port_label.pack()


        # ==================================
        # LOG
        # ==================================

        self.log_area = scrolledtext.ScrolledText(
            self.root,
            width=58,
            height=14,
            state="disabled"
        )

        self.log_area.pack(
            pady=15
        )


        # ==================================
        # BOTÕES
        # ==================================

        self.start_button = tk.Button(
            self.root,
            text="INICIAR SERVIDOR",
            width=20,
            command=self.start_server
        )

        self.start_button.pack(
            pady=5
        )


        self.close_button = tk.Button(
            self.root,
            text="ENCERRAR",
            width=20,
            command=self.close_program
        )

        self.close_button.pack(
            pady=5
        )


        # ==================================
        # SERVIDOR
        # ==================================

        self.server = None

        self.server_thread = None

        self.server_started = False


    # ======================================
    # ADICIONAR LOG
    # ======================================

    def add_log(
        self,
        message
    ):

        self.log_area.configure(
            state="normal"
        )

        self.log_area.insert(
            tk.END,
            message + "\n"
        )

        self.log_area.see(
            tk.END
        )

        self.log_area.configure(
            state="disabled"
        )


    # ======================================
    # INICIAR SERVIDOR
    # ======================================

    def start_server(self):

        if self.server_started:

            return


        self.server_started = True


        self.status_label.config(
            text="Status: ONLINE"
        )


        self.start_button.config(
            state="disabled"
        )


        self.add_log(
            "Servidor iniciado."
        )

        self.add_log(
            "Aguardando conexões..."
        )


        # Cria o servidor normal
        self.server = GameServer()


        # Executa em thread para não
        # travar a interface.
        self.server_thread = threading.Thread(
            target=self.run_server,
            daemon=True
        )


        self.server_thread.start()


    # ======================================
    # EXECUTAR SERVIDOR
    # ======================================

    def run_server(self):

        try:

            self.server.start()

        except Exception as error:

            self.add_log(
                f"Erro no servidor: {error}"
            )

            self.status_label.config(
                text="Status: ERRO"
            )


    # ======================================
    # FECHAR PROGRAMA
    # ======================================

    def close_program(self):

        self.add_log(
            "Encerrando servidor..."
        )


        try:

            if self.server:

                self.server.server_socket.close()

        except:

            pass


        self.root.destroy()


    # ======================================
    # EXECUTAR INTERFACE
    # ======================================

    def run(self):

        self.root.mainloop()


# ==========================================
# INÍCIO
# ==========================================

if __name__ == "__main__":

    app = ServerGUI()

    app.run()