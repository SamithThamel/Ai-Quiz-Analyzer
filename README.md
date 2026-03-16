# AI Quiz Analyzer (AI Quiz Solver)

A small desktop app that helps you solve quiz questions using **Google Gemini**.  
You can either:

- **Snip** a region of your screen containing the question (Ctrl+S), or
- **Paste** the question text into the app and analyze it.

The app sends the snipped image / pasted text to Gemini and shows a concise answer (and for MCQs, the correct option).

## Features

- Screen snipping overlay (draw a rectangle to capture a question)
- Paste-and-analyze textbox workflow
- Uses `google.generativeai` with the model `gemini-2.5-flash`
- Modern UI using `customtkinter`
- Copy answer to clipboard
- Light / Dark / System appearance modes

## Project Structure

- `AiAgent.py` — main application script (GUI + snipping + Gemini calls)
- `README.md` — documentation (this file)

## Requirements

- Python 3.9+ recommended
- OS notes:
  - Screen capture uses `PIL.ImageGrab` (works best on Windows/macOS; Linux may require extra setup).

Python packages used by the script:

- `customtkinter`
- `pillow`
- `google-generativeai`

## Setup

### 1) Clone the repo

```bash
git clone https://github.com/SamithThamel/Ai-Quiz-Analyzer.git
cd Ai-Quiz-Analyzer
```

### 2) Install dependencies

```bash
pip install customtkinter pillow google-generativeai
```

### 3) Add your Gemini API key

Open `AiAgent.py` and set:

```python
GEMINI_API_KEY = "#######ADD YOUR API KEY HERE#####"
```

Replace the placeholder with your real key.

> Tip: A safer approach is to read the key from an environment variable, but this repo currently uses a constant in the script.

## Run

```bash
python AiAgent.py
```

## How to Use

### Snip mode
1. Click **“Start Snipping”** (or press **Ctrl+S**).
2. Your screen will darken and your cursor becomes a crosshair.
3. Click and drag to select the region containing the question.
4. Release to capture → the app sends it to Gemini → the answer appears in a result window.
5. Use **Copy to Clipboard** if needed.

Press **Esc** to cancel snipping.

### Text mode
1. Paste/type a question into the textbox.
2. Click **“Analyze Text”**.
3. The answer appears in the result window.

## Notes / Troubleshooting

- **API Configuration Error** at startup usually means the API key is missing/invalid or the `google-generativeai` package isn’t installed properly.
- If the snip capture fails, it may be due to OS permissions (screen recording permissions on macOS) or `ImageGrab` limitations on your platform.
- If the selection box is too small, the app cancels the capture automatically.

## License

No license file is included in this repository. If you want others to use/modify/distribute it, add a `LICENSE` file (e.g., MIT).
