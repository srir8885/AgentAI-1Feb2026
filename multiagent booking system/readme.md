# Multi-Agent Booking System

A multi-agent travel booking system built with LangGraph, FastAPI, and MCP (Model Context Protocol) for flight search and booking.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- An `OPENAI_API_KEY`

---

## Setup

1. Clone the repository and navigate to the project folder.

2. Create a `.env` file in the project root:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEBUG=False
   ```

---

## Running with Docker Desktop

### macOS

1. Open **Docker Desktop** and make sure it is running (whale icon in the menu bar).

2. Open **Terminal** and navigate to the project directory:

   ```bash
   cd "multiagent booking system"
   ```

3. Build and start the containers:

   ```bash
   docker-compose up -d --build
   ```

4. Verify the container is running:

   ```bash
   docker-compose ps
   ```

5. The API will be available at: `http://localhost:8000`

6. To stop the service:

   ```bash
   docker-compose down
   ```

---

### Windows

1. Open **Docker Desktop** and make sure it is running (whale icon in the system tray).

   > Docker Desktop on Windows requires either **WSL 2** (recommended) or **Hyper-V** as the backend. Ensure WSL 2 is enabled if prompted during installation.

2. Open **Command Prompt** or **PowerShell** and navigate to the project directory:

   ```powershell
   cd "multiagent booking system"
   ```

3. Build and start the containers:

   ```powershell
   docker-compose up -d --build
   ```

4. Verify the container is running:

   ```powershell
   docker-compose ps
   ```

5. The API will be available at: `http://localhost:8000`

6. To stop the service:

   ```powershell
   docker-compose down
   ```

---

## Useful Commands

| Command | Description |
|---|---|
| `docker-compose up -d --build` | Build images and start containers in the background |
| `docker-compose ps` | Show running containers |
| `docker-compose logs -f` | Stream container logs |
| `docker-compose down` | Stop and remove containers |
| `docker-compose down -v` | Stop containers and remove volumes |

---

## Health Check

Once running, verify the service is healthy:

```bash
curl http://localhost:8000/health
```
