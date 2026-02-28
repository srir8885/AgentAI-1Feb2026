# Phidata Agent

A basic AI agent built with [Phidata](https://github.com/phidatahq/phidata) and OpenAI's GPT-4o model.

## Overview

This project creates a simple conversational AI agent named **Jarvis** using the Phidata framework. The agent uses GPT-4o as its underlying model and responds with markdown-formatted output.

## Prerequisites

- Python 3.8+
- An OpenAI API key

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd phidata-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the `phidata-agent` directory:

```bash
touch .env
```

Add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Project

### Run the basic agent

```bash
python basic.py
```

This will start the agent and send it the prompt `"What is the capital of France?"`, printing the response to the terminal.

## Project Structure

```
phidata-agent/
├── basic.py          # Main agent definition and entry point
├── requirements.txt  # Python dependencies
└── .env              # Environment variables (not committed)
```

## Dependencies

| Package           | Purpose                        |
|-------------------|--------------------------------|
| `phidata`         | Agent framework                |
| `openai`          | GPT-4o model integration       |
| `duckduckgo-search` | Web search tool              |
| `yfinance`        | Financial data tool            |
| `newspaper4k`     | News article extraction tool   |
| `python-dotenv`   | Load environment variables     |
| `lancedb`         | Vector database                |
| `sqlalchemy`      | SQL database ORM               |
