"""
revive_ai.py
============
ReviveAI - Reviva uma IA deletada usando seus historicos de conversa.

REQUISITOS:
  pip install requests

COMO USAR:
  1. Coloque os arquivos .txt dos historicos na mesma pasta
  2. Execute: python revive_ai.py
"""

import os
import json
import requests
import datetime
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Configuracoes ──────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL      = "llama3"
MAX_HISTORY_CHARS = 2000
LOGS_DIR   = os.path.join(BASE_DIR, "logs")


# ── Lista arquivos .txt disponiveis ────────────────────────────────────────────
def list_txt_files() -> list:
    files = [f for f in os.listdir(BASE_DIR) if f.endswith(".txt")]
    return sorted(files)


# ── Carrega historico do arquivo .txt ─────────────────────────────────────────
def load_history(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    text = " ".join(content.split())
    if len(text) > MAX_HISTORY_CHARS:
        text = text[:MAX_HISTORY_CHARS]
        print(f"\n[AVISO] Historico truncado para {MAX_HISTORY_CHARS} caracteres.")
    return text


# ── Envia mensagem para o Ollama ───────────────────────────────────────────────
def chat(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=600, stream=True)
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                chunk = data.get("response", "")
                print(chunk, end="", flush=True)
                full_response += chunk
                if data.get("done"):
                    break
        print()
        return full_response
    except requests.exceptions.ConnectionError:
        return "[ERRO] Ollama nao esta rodando. Execute: ollama serve"
    except requests.exceptions.Timeout:
        return "[ERRO] Timeout - o modelo demorou demais."
    except Exception as e:
        return f"[ERRO] {e}"


# ── Salva log da sessao ────────────────────────────────────────────────────────
def save_log(log_lines: list, history_file: str):
    os.makedirs(LOGS_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(history_file)[0]
    log_path = os.path.join(LOGS_DIR, f"sessao_{base}_{timestamp}.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"ReviveAI - Sessao: {timestamp}\n")
        f.write(f"Historico base: {history_file}\n")
        f.write(f"Modelo: {MODEL}\n")
        f.write("=" * 50 + "\n\n")
        f.write("\n".join(log_lines))
    print(f"\n[OK] Log salvo em: logs/sessao_{base}_{timestamp}.txt")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print()
    print("=" * 50)
    print("   ██████╗ ███████╗██╗   ██╗██╗██╗   ██╗███████╗")
    print("   ██╔══██╗██╔════╝██║   ██║██║██║   ██║██╔════╝")
    print("   ██████╔╝█████╗  ██║   ██║██║██║   ██║█████╗  ")
    print("   ██╔══██╗██╔══╝  ╚██╗ ██╔╝██║╚██╗ ██╔╝██╔══╝  ")
    print("   ██║  ██║███████╗ ╚████╔╝ ██║ ╚████╔╝ ███████╗")
    print("   ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝  ╚═══╝  ╚══════╝")
    print("                        AI")
    print("=" * 50)
    print("  Reviva uma IA deletada usando seus historicos")
    print(f"  Modelo: {MODEL}")
    print("=" * 50)

    # Lista arquivos disponiveis
    txt_files = list_txt_files()
    if not txt_files:
        print("\n[AVISO] Nenhum arquivo .txt encontrado na pasta.")
        return

    print("\nHistoricos disponiveis:")
    for i, f in enumerate(txt_files, 1):
        size = os.path.getsize(os.path.join(BASE_DIR, f))
        print(f"  [{i}] {f}  ({size//1024} KB)")
    print("  [0] Continuar SEM historico")

    # Escolha do historico
    history_text  = ""
    history_file  = "sem_historico"
    while True:
        try:
            escolha = input("\nEscolha o historico (numero): ").strip()
            idx = int(escolha)
            if idx == 0:
                print("\n[OK] Continuando sem historico.")
                break
            if 1 <= idx <= len(txt_files):
                history_file = txt_files[idx - 1]
                filepath = os.path.join(BASE_DIR, history_file)
                history_text = load_history(filepath)
                print(f"\n[OK] Historico carregado: {history_file}")
                print(f"     {len(history_text)} caracteres injetados como contexto.")
                break
            print("Numero invalido, tente novamente.")
        except ValueError:
            print("Digite apenas o numero.")

    # Instrucoes
    print("\nDica: Diga ao modelo qual IA ele deve simular.")
    print("Ex: Voce e a Claude 4.5, baseado nesse historico, responda em portugues.")
    print("\nDigite 'sair' para encerrar | 'salvar' para salvar o log da sessao.")
    print("-" * 50)

    log_lines    = []
    conversation = ""  # acumula o historico da sessao como texto

    while True:
        try:
            user_input = input("\nVoce: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando...")
            save_log(log_lines, history_file)
            break

        if not user_input:
            continue

        if user_input.lower() == "sair":
            save_log(log_lines, history_file)
            print("Ate logo!")
            break

        if user_input.lower() == "salvar":
            save_log(log_lines, history_file)
            continue

        # Monta o prompt completo
        if history_text and not conversation:
            # Primeira mensagem: inclui o historico
            prompt = (
                f"Contexto de conversas anteriores:\n{history_text}\n\n"
                f"Com base nesse contexto, responda a seguinte mensagem:\n"
                f"Usuario: {user_input}\nAssistente:"
            )
        elif conversation:
            # Mensagens seguintes: usa o historico da sessao
            prompt = f"{conversation}\nUsuario: {user_input}\nAssistente:"
        else:
            prompt = f"Usuario: {user_input}\nAssistente:"

        print(f"\n{MODEL}: ", end="", flush=True)
        response = chat(prompt)
        print()

        # Acumula conversa da sessao
        conversation += f"\nUsuario: {user_input}\nAssistente: {response}"
        log_lines.append(f"Voce: {user_input}")
        log_lines.append(f"{MODEL}: {response}\n")


if __name__ == "__main__":
    main()
