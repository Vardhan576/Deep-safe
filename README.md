# DeepSafe

DeepSafe is an AI integrity and media verification project designed to help identify potentially manipulated or untrustworthy digital content. The repository currently centers around the `DEEPSAFE/AI_Integrity_Checker` module and is built primarily with Python, with supporting Cython, C, HTML, and related components. 

## Overview

With the rapid growth of AI-generated and edited media, verifying whether content is authentic has become increasingly important. DeepSafe aims to provide a practical framework for checking the integrity of media or AI-generated outputs through a structured detection and analysis pipeline.

This repository is suitable for:
- AI and cybersecurity learners
- Developers building trust and safety tools
- Students working on fake media or deepfake detection projects
- Researchers exploring AI integrity validation workflows

## Project Structure

```bash
Deep-safe/
├── DEEPSAFE/
│   └── AI_Integrity_Checker/
├── .gitignore
```

## Features

- AI integrity checking workflow
- Modular project structure for future expansion
- Python-based implementation for easy development and experimentation
- Supportive low-level components using Cython/C for performance-oriented parts
- Repository layout that can be extended into a full detection platform or research prototype

## Tech Stack

- Python
- Cython
- C
- HTML
- PowerShell (minor usage)

## Use Cases

DeepSafe can be adapted for scenarios such as:
- Detecting suspicious or manipulated AI-generated media
- Building academic mini-projects or major projects around deepfake analysis
- Demonstrating media authenticity checking in presentations or hackathons
- Extending into a trust, safety, or misinformation detection platform

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Vardhan576/Deep-safe.git
cd Deep-safe
```

### 2. Navigate to the main module

```bash
cd DEEPSAFE/AI_Integrity_Checker
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\\Scripts\\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 4. Install dependencies

If a `requirements.txt` file is available inside the project, run:

```bash
pip install -r requirements.txt
```

If dependencies are not yet listed, install the core libraries used by the project manually after checking the source files.

### 5. Run the project

Run the main Python file from inside `AI_Integrity_Checker`:

```bash
python main.py
```

If your entry file has a different name, replace `main.py` with the actual startup script.

## How It Works

A typical DeepSafe workflow may include:
1. Input collection, such as media, image, video, or AI-generated output.
2. Preprocessing and feature extraction.
3. Integrity analysis using detection logic or learned models.
4. Output generation with a result, confidence score, or authenticity assessment.

This structure makes the project useful for both experimentation and future deployment-oriented improvements.

## Future Improvements

- Add a complete `requirements.txt`
- Add sample input/output files
- Add screenshots of the interface or results
- Provide trained model details and dataset references
- Add performance metrics such as accuracy, precision, recall, and F1-score
- Add Docker support for easier deployment
- Add API endpoints for integration with other applications

## Contribution

Contributions are welcome. You can contribute by:
- Improving detection accuracy
- Refactoring the codebase
- Adding documentation
- Building a frontend dashboard
- Adding deployment support
- Writing tests

To contribute:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

## License

Add your preferred license here, such as MIT, Apache-2.0, or GPL-3.0.

Example:

```md
This project is licensed under the MIT License.
```

## Author

**Megha Vardhan**  
GitHub: [Vardhan576](https://github.com/Vardhan576)

## Repository Link

[Deep-safe Repository](https://github.com/Vardhan576/Deep-safe)

## 📸 Application Screenshots

### 🔐 User Authentication

<p align="center">
  <img src="images/login.png" width="900" alt="Login Page">
</p>

> Secure user authentication with Login and Sign-Up functionality.

---

### 🤖 AI Document Detection

<p align="center">
  <img src="images/ai-detection.png" width="900" alt="AI Detection">
</p>

> Upload documents, images, audio, or video to detect AI-generated content and view recent scan history.

---

### 🛡️ Cyber Analyzer

<p align="center">
  <img src="images/cyber-analyzer-home.png" width="900" alt="Cyber Analyzer">
</p>

> Analyze suspicious text, encoded data, and CTF payloads using intelligent AI-powered threat detection.

---

### 📊 Cyber Analyzer Results

<p align="center">
  <img src="images/cyber-analyzer-result.png" width="900" alt="Cyber Analyzer Results">
</p>

> Displays AI probability, Trust Score, hidden data detection, decoded output, and extracted CTF flags.

---

### 🔒 Steganography - Hide Secret Message

<p align="center">
  <img src="images/steganography-encode.png" width="900" alt="Encode Message">
</p>

> Hide confidential messages inside images, videos, audio, or documents.

---

### 🔓 Steganography - Reveal Secret Message

<p align="center">
  <img src="images/steganography-decode.png" width="900" alt="Decode Message">
</p>

> Reveal hidden messages securely from encoded files.

---

### 📈 Advanced Media Analyzer

<p align="center">
  <img src="images/advanced-media-analyzer.png" width="900" alt="Advanced Media Analyzer">
</p>

> Analyze text, images, audio, and video for AI-generated content with detailed percentage breakdowns.

---

### 📋 Dashboard & Recent Scans

<p align="center">
  <img src="images/dashboard.png" width="49%" alt="Dashboard">
  <img src="images/recent-scans.png" width="49%" alt="Recent Scans">
</p>

> Monitor previous analyses and maintain a history of AI detection results.
