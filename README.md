# Minecraft Server Mod Sync

A lightweight client-server utility designed to keep Minecraft modpacks synchronized across clients. The system consists of a Go-based HTTP server for hosting files and directories, and a Python CLI desktop application for managing settings and downloading missing `.jar` mod files.

---

## Features

### **Go File Server (`server.go`)**:
* Command-line arguments to specify server IP address, port, and root directory.
* Built-in HTTP logging middleware.
* Directory listing support with automatic HTML rendering.


### **Python Client (`client.py`)**:
* Terminal-based interface (TUI) for quick navigation.
* Automatic detection of missing local mods by comparing client files against the remote server directory.
* Integrated GUI folder picker (via Tkinter) for selecting local Minecraft `mods` directories.
* Persistent local settings saved in `data.json`.
* ANSI colored terminal output for directory views and sync status.



---

## Prerequisites

* **Go**: Version 1.18 or higher (for building and running `server.go`).
* **Python**: Version 3.10 or higher (required for `match/case` support in `client.py`).
* **OS**: Windows (the client utilizes `msvcrt` and `ctypes` for keyboard inputs and window handling).

---

## Installation & Setup

### 1. Python Client Dependencies

Install the required Python packages before running the client:

```bash
pip install requests beautifulsoup4 keyboard colorama

```

---

## Usage

### Running the Server (`server.go`)

Start the server by providing the required `-address` and `-port` flags. You can optionally specify the served directory using `-dir`.

```bash
# Basic usage
go run server.go -address 127.0.0.1 -port 8080 -dir ./public

# Command-line Flags:
#   -address   The IP address to bind the server to (Required)
#   -port      The port to bind the server to (Required)
#   -dir       The root directory to serve (Default: ".")

```

#### Directory Structure Expected by Client

To support the client's version selection and sync features, structure your server host directory as follows:

```text
public/
└── 1.20.1/
    ├── mod-a.jar
    ├── mod-b.jar
    └── mod-c.jar

```

---

### Running the Client (`client.py`)

Run the client script from your command prompt or terminal:

```bash
python client.py

```

#### First-Time Setup

On initial startup, the application will prompt you to configure missing settings interactively:

1. **Server Address**: Input the server IP (e.g., `127.0.0.1`).
2. **Server Port**: Input the server port (e.g., `8080`).
3. **Minecraft Version**: Select an available version directory from the server list.
4. **Mods Folder**: A Windows folder-picker dialog will pop up; select your target local Minecraft `mods` directory (e.g., `%appdata%/.minecraft/mods`).

Settings are automatically saved to `data.json` for subsequent launches.

---

## File Overview

| File | Language | Description |
| --- | --- | --- |
| `server.go` | Go | HTTP server serving directory listings, raw static files, and media endpoints. |
| `client.py` | Python | Terminal client interface for listing, checking, and downloading missing `.jar` files from the server. |
| `data.json` | JSON | Automatically generated configuration file storing server host details and local file paths. |
