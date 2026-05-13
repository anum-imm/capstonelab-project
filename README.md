# 🚀 Enterprise Agentic AI System: From Multi-Agent to Self-RAG

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-⚡-green)
![LangGraph](https://img.shields.io/badge/LangGraph-🕸️-blueviolet)
![Docker](https://img.shields.io/badge/Docker-🐳-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-lightgrey)

## 📌 Project Overview
This repository contains a comprehensive, production-ready **Agentic AI System** developed as a full-lifecycle capstone project. Moving beyond simple AI wrappers, this project demonstrates the end-to-end engineering of an enterprise AI application: starting from a basic multi-agent setup, evolving to include strict security guardrails, automated CI/CD evaluations, Docker containerization, post-deployment monitoring, and finally culminating in an advanced **Self-Reflective RAG (Self-RAG)** architecture.

---

## 🌟 Key Features & Project Phases

### 1️⃣ Core Multi-Agent Architecture (`graph.py`, `tools.py`)
* Implemented a ReAct-style multi-agent system using **LangGraph**.
* Agents possess specialized tools and collaborate to fulfill complex user requests (e.g., querying databases, tracking orders).

### 2️⃣ Enterprise Security & Guardrails (`secured_graph.py`, `guardrails_config.py`)
* Built a security layer wrapping the core agent to protect against prompt injections, jailbreaks, and toxic queries.
* Implemented strict moderation checkpoints before generation.

### 3️⃣ Automated Evaluation & CI/CD (`run_eval.py`, `.github/`)
* Built an automated testing pipeline to evaluate LLM responses against a golden dataset (`test_dataset.json`).
* Configured thresholds for latency, groundedness, and accuracy (`eval_threshold_config.json`).
* Integrated with **GitHub Actions** for continuous integration testing.

### 4️⃣ Docker Containerization (`Dockerfile`, `docker-compose.yaml`)
* Fully containerized the application for consistent, cross-platform deployment.
* Easy orchestration of the agent backend alongside vector databases using Docker Compose.

### 5️⃣ Post-Deployment Monitoring (Part A: `analyze.py`, `agent_runner.py`)
* Implemented a feedback collection loop to monitor drift and user satisfaction in production.
* Logs interactions to `feedback_log.json` and analyzes failure rates.
* Driven by analytics, prompt engineering fixes were applied to improve agent recovery from missing tool arguments (e.g., automatically asking for missing Order IDs).

### 6️⃣ Advanced Self-RAG Agent (Part B: `/PartB`)
* Built an independent **University Course Advisory Agent** using a state-of-the-art **Self-RAG** LangGraph pipeline.
* **Adaptive Retrieval:** Dynamically skips vector DB retrieval for general greetings.
* **Relevance Grading:** Pydantic-validated models ruthlessly filter out irrelevant documents.
* **Web Search Fallback:** Automatically scrapes the internet via `DuckDuckGo` if local FAISS databases fail to provide an answer.
* **Anti-Hallucination:** Strictly checks generated answers against retrieved facts; loops and retries to self-correct hallucinations before they reach the user.

---

## 📂 Repository Structure

```text
├── .github/                # CI/CD workflows for automated evaluation
├── PartB/                  # Independent Self-RAG University Agent (Final Project)
├── data/                   # Source PDFs and text files for FAISS ingestion
├── tools.py                # ReAct tool definitions (Python functions)
├── graph.py                # Core LangGraph state machine and routing
├── secured_graph.py        # Graph wrapped with strict security guardrails
├── guardrails_config.py    # Definitions for blocking toxic/injected prompts
├── run_eval.py             # Script to run CI/CD evaluations against test_dataset.json
├── agent_runner.py         # CLI entry point for interacting with the main agent
├── analyze.py              # Analytics script for post-deployment monitoring
├── Dockerfile              # Containerization instructions
└── docker-compose.yaml     # Orchestration for microservices
```

---

## 🛠️ Technology Stack
* **AI/LLM Frameworks:** LangChain, LangGraph, OpenAI (`gpt-4o-mini`)
* **Data & Search:** FAISS (Vector DB), OpenAI Embeddings, DuckDuckGo API
* **Engineering:** Python, Pydantic (Schema validation), PyTest
* **DevOps:** Docker, Docker Compose, GitHub Actions

---

## 🚀 Getting Started

### Prerequisites
1. Python 3.10+
2. An OpenAI API Key (`OPENAI_API_KEY`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agentic-ai-system.git
   cd agentic-ai-system
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

---

## 💻 Usage

### Run the Secure Multi-Agent (Main Project)
Interact with the primary multi-agent system (includes feedback monitoring):
```bash
python agent_runner.py
```

### Run the Self-RAG University Agent (Part B)
Test the advanced hallucination-checking and fallback logic:
```bash
cd PartB
python self_rag_agent.py
```
*(You can also run `python test_cases.py` in the PartB folder to watch the LangGraph nodes reflect and route decisions in real-time).*

### Run the Analytics Dashboard
View the post-deployment feedback stats and identify failed queries:
```bash
python analyze.py
```

---

## 🤝 Let's Connect!
I am actively seeking roles in **AI Engineering**, **Machine Learning**, and **Software Development**. I specialize in moving LLMs out of Jupyter notebooks and into robust, scalable, and secure production environments. If you're looking for a builder, let's talk!

🔗 **[LinkedIn Profile](https://linkedin.com/in/yourprofile)** | 📧 **[Email Me](mailto:your.email@example.com)**
