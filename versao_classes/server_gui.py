import threading
import tkinter as tk

from tkinter import scrolledtext

from game_server import GameServer


# ============================================================
# INTERFACE GRÁFICA DO SERVIDOR
# ============================================================

class ServerGUI:

    def __init__(self):

        # ====================================================
        # JANELA PRINCIPAL
        # ====================================================

        self.root = tk.Tk()

        self.root.title(
            "Mini World Server"
        )

        self.root.geometry(
            "560x500"
        )

        self.root.resizable(
            False,
            False
        )


        # Se clicar no X da janela,
        # usamos nosso encerramento seguro.
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_program
        )


        # ====================================================
        # TÍTULO
        # ====================================================

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


        # ====================================================
        # STATUS
        # ====================================================

        self.status_label = tk.Label(

            self.root,

            text="● OFFLINE",

            font=(
                "Arial",
                13,
                "bold"
            ),

            fg="red"
        )


        self.status_label.pack(
            pady=5
        )


        # ====================================================
        # INFORMAÇÕES
        # ====================================================

        self.info_frame = tk.Frame(
            self.root
        )


        self.info_frame.pack(
            pady=5
        )


        self.ip_label = tk.Label(

            self.info_frame,

            text="Host: 0.0.0.0"
        )


        self.ip_label.grid(
            row=0,
            column=0,
            padx=15
        )


        self.port_label = tk.Label(

            self.info_frame,

            text="Porta: 5000"
        )


        self.port_label.grid(
            row=0,
            column=1,
            padx=15
        )


        # ====================================================
        # LOG
        # ====================================================

        log_title = tk.Label(

            self.root,

            text="LOG DO SERVIDOR",

            font=(
                "Arial",
                11,
                "bold"
            )
        )


        log_title.pack(
            pady=(
                15,
                5
            )
        )


        self.log_area = (
            scrolledtext.ScrolledText(

                self.root,

                width=65,

                height=16,

                state="disabled",

                font=(
                    "Consolas",
                    9
                )
            )
        )


        self.log_area.pack(
            padx=15,
            pady=5
        )


        # ====================================================
        # BOTÕES
        # ====================================================

        self.button_frame = tk.Frame(
            self.root
        )


        self.button_frame.pack(
            pady=15
        )


        # ----------------------------------------------------
        # INICIAR
        # ----------------------------------------------------

        self.start_button = tk.Button(

            self.button_frame,

            text="INICIAR SERVIDOR",

            width=20,

            command=self.start_server
        )


        self.start_button.grid(
            row=0,
            column=0,
            padx=5
        )


        # ----------------------------------------------------
        # PARAR
        # ----------------------------------------------------

        self.stop_button = tk.Button(

            self.button_frame,

            text="PARAR SERVIDOR",

            width=20,

            state="disabled",

            command=self.stop_server
        )


        self.stop_button.grid(
            row=0,
            column=1,
            padx=5
        )


        # ====================================================
        # SERVIDOR
        # ====================================================

        self.server = None

        self.server_thread = None


    # ========================================================
    # ADICIONAR LOG
    # ========================================================
    #
    # IMPORTANTE:
    #
    # GameServer executa em outra thread.
    # Tkinter deve ser atualizado pela thread
    # principal.
    #
    # Por isso usamos root.after().
    # ========================================================

    def add_log(
        self,
        message
    ):

        self.root.after(
            0,
            self._add_log_safe,
            message
        )


    # ========================================================
    # ADICIONAR LOG NA GUI
    # ========================================================

    def _add_log_safe(
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


        # Faz scroll automático
        self.log_area.see(
            tk.END
        )


        self.log_area.configure(
            state="disabled"
        )


    # ========================================================
    # INICIAR SERVIDOR
    # ========================================================

    def start_server(self):

        # Evita iniciar duas vezes.
        if (
            self.server
            and self.server.running
        ):

            return


        # ====================================================
        # CRIA SERVIDOR
        # ====================================================

        self.server = GameServer(

            host="0.0.0.0",

            port=5000,

            log_callback=self.add_log
        )


        # ====================================================
        # ALTERA INTERFACE
        # ====================================================

        self.status_label.config(

            text="● ONLINE",

            fg="green"
        )


        self.start_button.config(
            state="disabled"
        )


        self.stop_button.config(
            state="normal"
        )


        self.add_log(
            "================================"
        )

        self.add_log(
            "Iniciando Mini World Server..."
        )


        # ====================================================
        # THREAD DO SERVIDOR
        # ====================================================
        #
        # Sem thread, server.start()
        # travaria a janela do Tkinter.
        # ====================================================

        self.server_thread = (
            threading.Thread(

                target=
                self.run_server,

                daemon=True
            )
        )


        self.server_thread.start()


    # ========================================================
    # EXECUTAR SERVIDOR
    # ========================================================

    def run_server(self):

        try:

            self.server.start()


        except Exception as error:

            self.add_log(
                f"Erro inesperado: {error}"
            )


        finally:

            # Quando o servidor parar,
            # atualizamos a interface.
            self.root.after(
                0,
                self.server_stopped
            )


    # ========================================================
    # SERVIDOR PAROU
    # ========================================================

    def server_stopped(self):

        self.status_label.config(

            text="● OFFLINE",

            fg="red"
        )


        self.start_button.config(
            state="normal"
        )


        self.stop_button.config(
            state="disabled"
        )


    # ========================================================
    # PARAR SERVIDOR
    # ========================================================

    def stop_server(self):

        if not self.server:

            return


        self.add_log(
            "Solicitação de encerramento..."
        )


        self.server.stop()


    # ========================================================
    # FECHAR PROGRAMA
    # ========================================================

    def close_program(self):

        # Primeiro encerra servidor.
        if self.server:

            try:

                self.server.stop()

            except Exception:

                pass


        # Depois fecha janela.
        self.root.destroy()


    # ========================================================
    # EXECUTAR GUI
    # ========================================================

    def run(self):

        self.root.mainloop()


# ============================================================
# INÍCIO
# ============================================================

if __name__ == "__main__":

    app = ServerGUI()

    app.run()