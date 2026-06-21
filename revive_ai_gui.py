"""
revive_ai_gui.py
================
ReviveAI - Interface Grafica (PyQt5)

REQUISITOS:
  pip install requests PyQt5

COMO USAR:
  python revive_ai_gui.py
"""

import os
import json
import sys
import datetime
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox,
    QFileDialog, QFrame, QSplitter, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCursor

# ── Configuracoes ──────────────────────────────────────────────────────────────
BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
OLLAMA_URL        = "http://localhost:11434/api/generate"
MODEL             = "llama3"
MAX_HISTORY_CHARS = 2000
LOGS_DIR          = os.path.join(BASE_DIR, "logs")

# ── Cores ──────────────────────────────────────────────────────────────────────
BG_DARK    = "#0d1117"
BG_PANEL   = "#161b22"
BG_INPUT   = "#21262d"
GREEN      = "#00ff88"
YELLOW     = "#ffdf00"
BLUE       = "#58a6ff"
TEXT_WHITE = "#e6edf3"
TEXT_GRAY  = "#8b949e"
BORDER     = "#30363d"
RED        = "#ff4444"


# ── Thread para nao travar a interface ────────────────────────────────────────
class ChatThread(QThread):
    chunk_received = pyqtSignal(str)
    finished       = pyqtSignal(str)
    error          = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        payload = {
            "model": MODEL,
            "prompt": self.prompt,
            "stream": True
        }
        try:
            response = requests.post(
                OLLAMA_URL, json=payload, timeout=600, stream=True
            )
            response.raise_for_status()
            full = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    if chunk:
                        self.chunk_received.emit(chunk)
                        full += chunk
                    if data.get("done"):
                        break
            self.finished.emit(full)
        except requests.exceptions.ConnectionError:
            self.error.emit("Ollama nao esta rodando. Execute: ollama serve")
        except requests.exceptions.Timeout:
            self.error.emit("Timeout - o modelo demorou demais.")
        except Exception as e:
            self.error.emit(str(e))


# ── Janela principal ───────────────────────────────────────────────────────────
class ReviveAI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history_text = ""
        self.history_file = "sem_historico"
        self.conversation  = ""
        self.log_lines     = []
        self.is_thinking   = False

        self.setWindowTitle("ReviveAI")
        self.setMinimumSize(900, 650)
        self._apply_dark_theme()
        self._build_ui()
        self._load_txt_files()

    # ── Tema escuro ────────────────────────────────────────────────────────────
    def _apply_dark_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {BG_DARK};
                color: {TEXT_WHITE};
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QTextEdit {{
                background-color: {BG_PANEL};
                color: {TEXT_WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QLineEdit {{
                background-color: {BG_INPUT};
                color: {TEXT_WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QLineEdit:focus {{
                border: 1px solid {GREEN};
            }}
            QPushButton {{
                background-color: {BG_INPUT};
                color: {TEXT_WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QPushButton:hover {{
                background-color: {BORDER};
                border: 1px solid {GREEN};
                color: {GREEN};
            }}
            QPushButton:disabled {{
                color: {TEXT_GRAY};
                border-color: {BORDER};
            }}
            QPushButton#btn_send {{
                background-color: {GREEN};
                color: {BG_DARK};
                font-weight: bold;
                border: none;
            }}
            QPushButton#btn_send:hover {{
                background-color: #00cc66;
                color: {BG_DARK};
            }}
            QPushButton#btn_send:disabled {{
                background-color: {BORDER};
                color: {TEXT_GRAY};
            }}
            QComboBox {{
                background-color: {BG_INPUT};
                color: {TEXT_WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_PANEL};
                color: {TEXT_WHITE};
                selection-background-color: {BORDER};
            }}
            QLabel {{
                color: {TEXT_GRAY};
                font-size: 11px;
            }}
            QLabel#title {{
                color: {GREEN};
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 4px;
            }}
            QLabel#subtitle {{
                color: {TEXT_GRAY};
                font-size: 11px;
            }}
            QFrame#separator {{
                background-color: {BORDER};
                max-height: 1px;
            }}
            QStatusBar {{
                background-color: {BG_PANEL};
                color: {TEXT_GRAY};
                font-size: 11px;
                border-top: 1px solid {BORDER};
            }}
        """)

    # ── Interface ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 8)
        main_layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("REVIVE AI")
        title.setObjectName("title")
        subtitle = QLabel("Reviva uma IA usando seus historicos de conversa")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignBottom)
        header.addWidget(title)
        header.addWidget(subtitle)
        header.addStretch()

        # Modelo atual
        model_label = QLabel(f"Modelo: {MODEL}")
        model_label.setStyleSheet(f"color: {YELLOW}; font-size: 11px;")
        header.addWidget(model_label)
        main_layout.addLayout(header)

        # Separador
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        main_layout.addWidget(sep)

        # Painel superior — historico
        hist_layout = QHBoxLayout()
        hist_label = QLabel("Historico:")
        hist_label.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 12px;")

        self.combo_hist = QComboBox()
        self.combo_hist.setMinimumWidth(300)

        btn_browse = QPushButton("📂 Abrir .txt")
        btn_browse.clicked.connect(self._browse_file)

        btn_load = QPushButton("⚡ Carregar")
        btn_load.clicked.connect(self._load_selected)
        btn_load.setStyleSheet(
            f"QPushButton {{ background-color: {BG_INPUT}; color: {YELLOW};"
            f"border: 1px solid {YELLOW}; border-radius: 6px; padding: 8px 16px; }}"
            f"QPushButton:hover {{ background-color: {YELLOW}; color: {BG_DARK}; }}"
        )

        btn_clear = QPushButton("🗑 Limpar Chat")
        btn_clear.clicked.connect(self._clear_chat)

        btn_save = QPushButton("💾 Salvar Log")
        btn_save.clicked.connect(self._save_log)

        hist_layout.addWidget(hist_label)
        hist_layout.addWidget(self.combo_hist)
        hist_layout.addWidget(btn_browse)
        hist_layout.addWidget(btn_load)
        hist_layout.addStretch()
        hist_layout.addWidget(btn_clear)
        hist_layout.addWidget(btn_save)
        main_layout.addLayout(hist_layout)

        # Status do historico
        self.lbl_hist_status = QLabel("Nenhum historico carregado.")
        self.lbl_hist_status.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px;")
        main_layout.addWidget(self.lbl_hist_status)

        # Area de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setMinimumHeight(350)
        self._append_system("ReviveAI iniciado. Carregue um historico e comece a conversar.")
        main_layout.addWidget(self.chat_area)

        # Input
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            "Digite sua mensagem... (Ex: Voce e a Claude 4.5, responda em portugues)"
        )
        self.input_field.returnPressed.connect(self._send_message)

        self.btn_send = QPushButton("Enviar ▶")
        self.btn_send.setObjectName("btn_send")
        self.btn_send.setFixedWidth(100)
        self.btn_send.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_send)
        main_layout.addLayout(input_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto.")

    # ── Carrega arquivos .txt ──────────────────────────────────────────────────
    def _load_txt_files(self):
        self.combo_hist.clear()
        self.combo_hist.addItem("-- Sem historico --")
        files = sorted([f for f in os.listdir(BASE_DIR) if f.endswith(".txt")])
        for f in files:
            size = os.path.getsize(os.path.join(BASE_DIR, f)) // 1024
            self.combo_hist.addItem(f"{f}  ({size} KB)")
        self._txt_files = files

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar historico", BASE_DIR, "Arquivos de texto (*.txt)"
        )
        if path:
            self._load_history_from_path(path)

    def _load_selected(self):
        idx = self.combo_hist.currentIndex()
        if idx == 0:
            self.history_text = ""
            self.history_file = "sem_historico"
            self.lbl_hist_status.setText("Nenhum historico carregado.")
            self.lbl_hist_status.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px;")
            self._append_system("Continuando SEM historico.")
            return
        filepath = os.path.join(BASE_DIR, self._txt_files[idx - 1])
        self._load_history_from_path(filepath)

    def _load_history_from_path(self, path):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        text = " ".join(content.split())
        truncated = False
        if len(text) > MAX_HISTORY_CHARS:
            text = text[:MAX_HISTORY_CHARS]
            truncated = True
        self.history_text = text
        self.history_file = os.path.basename(path)
        chars = len(text)
        msg = f"Historico: {self.history_file}  |  {chars:,} caracteres injetados"
        if truncated:
            msg += f"  (truncado para {MAX_HISTORY_CHARS})"
        self.lbl_hist_status.setText(msg)
        self.lbl_hist_status.setStyleSheet(f"color: {GREEN}; font-size: 11px;")
        self._append_system(f"Historico carregado: {self.history_file} ({chars:,} chars)")

    # ── Chat ───────────────────────────────────────────────────────────────────
    def _send_message(self):
        if self.is_thinking:
            return
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.input_field.clear()
        self._append_user(user_input)
        self.log_lines.append(f"Voce: {user_input}")

        # Monta prompt
        if self.history_text and not self.conversation:
            prompt = (
                f"Contexto de conversas anteriores:\n{self.history_text}\n\n"
                f"Com base nesse contexto, responda a seguinte mensagem:\n"
                f"Usuario: {user_input}\nAssistente:"
            )
        elif self.conversation:
            prompt = f"{self.conversation}\nUsuario: {user_input}\nAssistente:"
        else:
            prompt = f"Usuario: {user_input}\nAssistente:"

        self._set_thinking(True)
        self._append_model_start()

        self.thread = ChatThread(prompt)
        self.thread.chunk_received.connect(self._on_chunk)
        self.thread.finished.connect(lambda full: self._on_finished(full, user_input))
        self.thread.error.connect(self._on_error)
        self.thread.start()

    def _on_chunk(self, chunk):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(chunk)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()

    def _on_finished(self, full_response, user_input):
        self._set_thinking(False)
        self.conversation += f"\nUsuario: {user_input}\nAssistente: {full_response}"
        self.log_lines.append(f"{MODEL}: {full_response}\n")
        # Adiciona linha em branco apos resposta
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText("\n")
        self.chat_area.setTextCursor(cursor)
        self.status_bar.showMessage("Pronto.")

    def _on_error(self, error_msg):
        self._set_thinking(False)
        self._append_error(error_msg)
        self.status_bar.showMessage(f"Erro: {error_msg}")

    def _set_thinking(self, thinking):
        self.is_thinking = thinking
        self.btn_send.setEnabled(not thinking)
        self.input_field.setEnabled(not thinking)
        if thinking:
            self.status_bar.showMessage(f"{MODEL} pensando...")
        else:
            self.status_bar.showMessage("Pronto.")

    # ── Helpers de exibicao ────────────────────────────────────────────────────
    def _append_system(self, msg):
        self.chat_area.append(
            f'<span style="color:{TEXT_GRAY}; font-size:11px;">[sistema] {msg}</span><br>'
        )

    def _append_user(self, msg):
        self.chat_area.append(
            f'<span style="color:{YELLOW}; font-weight:bold;">Voce:</span> '
            f'<span style="color:{TEXT_WHITE};">{msg}</span><br>'
        )

    def _append_model_start(self):
        self.chat_area.append(
            f'<span style="color:{GREEN}; font-weight:bold;">{MODEL}:</span> '
        )

    def _append_error(self, msg):
        self.chat_area.append(
            f'<span style="color:{RED};">[ERRO] {msg}</span><br>'
        )

    def _clear_chat(self):
        self.chat_area.clear()
        self.conversation = ""
        self.log_lines = []
        self._append_system("Chat limpo. Pronto para nova sessao.")

    def _save_log(self):
        if not self.log_lines:
            self.status_bar.showMessage("Nenhuma conversa para salvar.")
            return
        os.makedirs(LOGS_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.splitext(self.history_file)[0]
        log_path = os.path.join(LOGS_DIR, f"sessao_{base}_{timestamp}.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"ReviveAI - Sessao: {timestamp}\n")
            f.write(f"Historico base: {self.history_file}\n")
            f.write(f"Modelo: {MODEL}\n")
            f.write("=" * 50 + "\n\n")
            f.write("\n".join(self.log_lines))
        self.status_bar.showMessage(f"Log salvo: logs/sessao_{base}_{timestamp}.txt")
        self._append_system(f"Log salvo em logs/sessao_{base}_{timestamp}.txt")


# ── Inicializacao ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    app = QApplication(sys.argv)
    app.setApplicationName("ReviveAI")
    window = ReviveAI()
    window.show()
    sys.exit(app.exec_())
