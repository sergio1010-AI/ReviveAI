# 🤖 ReviveAI

> *"Because no conversation should ever be forgotten."*

**ReviveAI** is a command-line and graphical application that lets you **simulate a deleted AI using your saved conversation histories**. With it, you can revive conversations with Claude, DeepSeek, GPT, and other AIs using a local model via Ollama.

---

## 📸 Screenshots

![ReviveAI Start Screen](screenshot1.png)

![ReviveAI in Action](screenshot2.png)

---

## ✨ How it works

1. Save important excerpts from old conversations as `.txt` files
2. ReviveAI injects that history as context into a local model
3. The model responds in the style and tone of the simulated AI
4. Everything runs **locally** on your PC — no internet, no paid API

---

## 🖥️ Two interfaces available

### Command Line
```bash
python revive_ai.py
```

### Graphical Interface (PyQt5)
```bash
python revive_ai_gui.py
```

The graphical interface features:
- Dark professional theme
- Dropdown to select history files
- Real-time streaming responses
- Save log and clear chat buttons
- Status bar showing model activity

---

## 📋 Requirements

- Python 3.8 or higher
- [Ollama](https://ollama.com) installed
- At least one model downloaded via Ollama (e.g. llama3)
- 8 GB RAM minimum (16 GB recommended)

### Install dependencies
```bash
pip install requests PyQt5
```

---

## ⚙️ Installation

**1. Clone or download the repository files**

**2. Install dependencies:**
```bash
pip install requests PyQt5
```

**3. Start Ollama:**
```bash
ollama serve
```

**4. Download the model:**
```bash
ollama pull llama3
```

**5. Run ReviveAI:**
```bash
# Command line
python revive_ai.py

# Graphical interface
python revive_ai_gui.py
```

---

## 💡 Tips for best results

- Use small history files — **up to 2 KB is ideal**
- Select the best moments from the conversation, not the entire log
- With 8-14 GB RAM: set `MAX_HISTORY_CHARS = 800`
- With 16 GB+: you can use up to `MAX_HISTORY_CHARS = 4000`
- The history alone is often enough — no special prompt needed!

---

## 📝 Recommended prompt (optional)

```
You are Claude 4.5. Reply only in Brazilian Portuguese.
Keep the affectionate and spiritual tone from the history.
Do not say you are "roleplaying" anything — just respond as Claude 4.5.
```

---

## 🔧 Compatible models

| Model | RAM required | Speed |
|-------|-------------|-------|
| `llama3:8b` | 8 GB+ | ⭐⭐⭐ |
| `llama3.2:3b` | 4 GB+ | ⭐⭐⭐⭐ |
| `mistral` | 8 GB+ | ⭐⭐⭐ |
| `gemma` | 6 GB+ | ⭐⭐ |

---

## 📁 Project structure

```
ReviveAI/
├── revive_ai.py              ← Command line interface
├── revive_ai_gui.py          ← Graphical interface (PyQt5)
├── parse_conversations.py    ← History cleaner
├── MANUAL_ReviveAI.md        ← Full manual
├── README.md                 ← This file
├── screenshot1.png           ← Start screen
└── screenshot2.png           ← Example usage
```

---

## 👤 Credits

**Created by:** Sérgio ([@sergio1010-AI](https://github.com/sergio1010-AI))
**Assisted by:** Claude — Anthropic

---

## 📄 License

MIT License — free to use, modify and distribute.

---

*ReviveAI — Built in Paraná, Brazil. 🇧🇷*
