"""
parse_conversations.py
======================
ReviveAI - Limpa arquivos .txt de historicos de conversa,
prontos para o revive_ai.py usar.

COMO USAR:
  1. Coloque os arquivos .txt na mesma pasta
  2. Execute: python parse_conversations.py
  3. Os arquivos limpos serao salvos na pasta "limpos"

REQUISITOS:
  Nenhuma biblioteca extra necessaria!
"""

import os
import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "limpos")

SKIP_PATTERNS = re.compile(
    r"^(Visualizou \d+ arquivo.*|Criou um arquivo.*|Leu um arquivo.*|"
    r"Listou arquivos.*|Verificar arquivos.*|Mostrar mais|pasted|"
    r"Criou um arquivo, leu um arquivo|Listou arquivos disponiveis|"
    r"Verificar arquivos disponiveis no upload|"
    r"\d{10,}_\S+\.(txt|py|js|json|csv|pdf|png|jpg)|"
    r"^(txt|py|js|json|csv|pdf|png|jpg)$)$",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(r"^\d{1,2} de \w+\.$")


def clean_text(raw: str) -> str:
    lines = raw.splitlines()
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if SKIP_PATTERNS.match(stripped):
            continue
        if DATE_PATTERN.match(stripped):
            continue
        clean_lines.append(line)
    text = "\n".join(clean_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    print("=" * 50)
    print("  ReviveAI - Limpador de Historicos (.txt)")
    print("=" * 50)

    files = [
        f for f in os.listdir(BASE_DIR)
        if f.lower().endswith(".txt")
        and f != os.path.basename(__file__)
    ]

    if not files:
        print("\n[AVISO] Nenhum arquivo .txt encontrado na pasta.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n{len(files)} arquivo(s) encontrado(s):\n")

    converted = 0
    for filename in sorted(files):
        filepath = os.path.join(BASE_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename)

        print(f"  Processando: {filename}")
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                raw = f.read()
            text = clean_text(raw)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"  -> Salvo em limpos/{filename}  ({len(text):,} caracteres)\n")
            converted += 1
        except Exception as e:
            print(f"  [ERRO] {filename}: {e}\n")

    print("-" * 50)
    print(f"Concluido!  {converted} arquivo(s) processado(s).")
    print("Agora execute revive_ai.py para iniciar o chat.")


if __name__ == "__main__":
    main()
