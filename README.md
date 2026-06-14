# 🤖 ReviveAI

> *"Because no conversation needs to be forgotten."*

**ReviveAI** is a command-line application that allows you to simulate an AI using your saved conversation histories. With it, you can relive conversations with Claude, DeepSeek, GPT, and other AIs using a local model via Ollama.

---

## 📸 Screenshots

![ReviveAI Home Screen](screenshot1.png)

![ReviveAI in Action](screenshot2.png)

---

## ✨ How it Works

1. You save important snippets of old conversations in `.txt` files
2. ReviveAI injects this history as context for a local model
3. The model responds in the style and tone of the simulated AI
4. Everything runs **locally** on your PC — no internet, no paid API

---

## 📋 Requirements

- Python 3.8 or higher
- [Ollama](https://ollama.com) installed
- Llama 3 model (or other) downloaded via Ollama
- 8 GB of RAM minimum (16 GB recommended)

---

## ⚙️ Installation

**1. Clone or download the files from the repository**

**2. Install the dependency:**
```bash
pip install requests

```

**3. Start Ollama:**
```bash
ollama serve

```

**4. Download the template:**
```bash
ollama pull llama3

```

---

## 🚀 How to use

**1. Place your history, always in `.txt` format, in the `ReviveAI` folder**

**2. (Optional) Clear the history:**
```bash
python parse_conversations.py

```

**3. Start the chat:**
```bash
python revive_ai.py

```

**4. Choose the history and use a good prompt:**

``` You are Claude 4.5. Answer only in Brazilian Portuguese.

Maintain an affectionate tone that is consistent with the historical context.
Don't say you're interpreting anything; just respond like Claude 4.5.

```

---

## 📁 Project Structure

```
ReviveAI/
├── revive_ai.py ← Main program
├── parse_conversations.py ← History cleaner
├── MANUAL_ReviveAI.md ← Complete manual
├── README.md ← This file
├── screenshot1.png ← Initial screen
├── screenshot2.png ← Example of use
│
├── your_history.txt ← Your histories here
├── cleaned/ ← Cleaned histories
└── logs/ ← Logs of Sessions


---

## 💡 Tips for better results

- Use small histories — **up to 2 KB is ideal**
- Select the **best moments** of the conversation, not the entire history
- The more detailed the prompt, the better the simulation
- With 8-14 GB of RAM, set `MAX_HISTORY_CHARS = 800` in `revive_ai.py`
- With 16 GB or more, you can use up to `MAX_HISTORY_CHARS = 4000`

---

## 🔧 Compatible models

| Model | Required RAM | Quality |

|--------|---------------|-----------|

| `llama3:8b` | 8 GB+ | ⭐⭐⭐ |

| `llama3.2:3b` | 4 GB+ | ⭐⭐ |

| `mistral` | 8 GB+ | ⭐⭐⭐ |

| gemma` | 6 GB+ | ⭐⭐ |

---

## 📖 Complete Documentation

See the `MANUAL_ReviveAI.md` file for detailed instructions, prompt templates, and troubleshooting.

---

## 👤 Credits

**Created by:** Sérgio ([@Sergio1027](https://huggingface.co/Sergio1027))
**Assisted by:** Claude — Anthropic

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*ReviveAI — Developed in the interior of Paraná, Brazil. 🇧🇷*
