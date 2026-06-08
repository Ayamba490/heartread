# 💕 HeartRead — AI Relationship Signal Analyzer

> *The 3am thought you can't tell your friends.*

HeartRead uses AI to help people understand whether someone has romantic feelings for them. You describe the situation, it reads the signals, tracks patterns over time, and even writes you the perfect message to send.

---

## 🎯 The Problem

Millions of people silently wonder: *"Does this person like me back?"* They overanalyze texts, replay conversations, and suffer in uncertainty — with no one objective to talk to.

HeartRead solves this by acting as a warm, honest, AI-powered advisor available at 3am when you can't call your friends.

---

## ✨ Features

### 🔍 Signal Analysis
Answer 5 guided questions about your situation. HeartRead analyzes behavioral patterns and returns:
- **Verdict** — Likely Interested / Mixed Signals / Probably Just Friendly / Hard to Tell
- **Confidence score** — How strong the signals are
- **Honest analysis** — 3-4 paragraph breakdown specific to your situation
- **Color-coded flags** — Green (promising), Yellow (ambiguous), Red (cautionary)
- **Next step** — One specific action to take this week

### 📊 Signal Tracker
Log interactions over time with warmth scores (1–10). HeartRead:
- Plots your warmth trend on a chart
- Detects if signals are warming up, cooling down, or staying flat
- Identifies who is initiating contact

### ✉️ What to Say
Stuck on what to text? Choose a tone and goal, and HeartRead writes you a natural, human-sounding message tailored to your exact situation.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Free Groq API key from [console.groq.com](https://console.groq.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/heartread.git
cd heartread

# Install dependencies
pip install streamlit groq python-dotenv

# Create your .env file
echo GROQ_API_KEY=your_key_here > .env

# Run the app
streamlit run heartread_app.py
```

Open your browser at `http://localhost:8501`

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| AI Model | Llama 3.3 70B via Groq API |
| Language | Python |
| Deployment | Streamlit Cloud |

---

## 📁 Project Structure

```
heartread/
├── heartread_app.py   # Main Streamlit app
├── .env               # API key (never committed)
├── .gitignore         # Keeps secrets safe
└── README.md          # You are here
```

---

## 🔒 Privacy

- No user data is stored or logged
- All conversations are processed in real-time and discarded
- API key is stored locally in .env and never exposed

---

## 🏆 Built For

This project was built for a hackathon to demonstrate how AI can provide emotional intelligence and clarity in personal relationships — a space where people are deeply underserved by technology.

---

## 👨‍💻 Author

Built with love by **Ronald**
Makerere University Business School

---

## 📄 License

MIT License — free to use and build on.
