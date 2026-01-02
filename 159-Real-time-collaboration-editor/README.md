# 📝 Real-Time Collaborative Text Editor (Diff-Based)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/rogers-cyber/python-tiny-tools.svg?style=social&label=Stars)](https://github.com/rogers-cyber/python-tiny-tools/stargazers)

A Python-based **real-time collaborative text editor** with diff-based updates, floating colored cursors, and username labels — designed to feel like Google Docs. Built using `ttkbootstrap` for a modern **Flatly theme**.

---

## 🌟 Features

- Real-time collaborative editing over a local network or internet.
- **Diff-based updates** using Python `difflib` for minimal network usage.
- **Floating colored cursors** for all collaborators.
- **Username labels** next to each cursor.
- Efficient and scalable for hundreds of users.
- Modern, sleek **Flatly theme** via `ttkbootstrap`.
- Works cross-platform: **Windows, macOS, Linux**.

---

## 🛠 Requirements

- **Python 3.10+**
- Python packages:
```bash
pip install ttkbootstrap websockets pillow
```

---

## 📂 Project Files

- `server_diff_graceful.py` – WebSocket server handling diff updates, cursors, and usernames.
- `client_diff_floating_cursors.py` – Collaborative client with diff-based editing, floating cursors, and username labels.
- `README.md` – This file.

---

## 🚀 Usage

### 1️⃣ Start the Server

```bash
python server_diff_graceful.py
```

- The server runs on `0.0.0.0:8765` by default.
- Press **Ctrl+C** to stop gracefully.

### 2️⃣ Start a Client

```bash
python client_diff_floating_cursors.py
```

- Enter a **unique username** when prompted.
- The editor window will open. You can start typing and collaborate in real-time.

### 3️⃣ Multi-User Collaboration

- Run multiple clients on the same or different machines connected to the server.
- Features you’ll see in real-time:
  - **Floating colored cursors** for each user.
  - **Username labels** next to cursors.
  - Live document updates from all collaborators.

---

## ⚙ How It Works

- **Diff-Based Syncing**: Only changes are sent over the network, making it bandwidth-efficient.
- **Floating Cursors & Labels**: Cursors and labels are drawn visually without modifying the actual text content.
- **Async + Threaded**: Smooth updates using `asyncio` alongside Tkinter GUI.

---

## 🎨 Customization

- **Server IP / Port**: Modify `SERVER_URI` in `client_diff_floating_cursors.py`.
- **Cursor Colors**: Edit the `colors_list` variable for different cursor/label colors.
- **UI Theme**: Change the `themename` in `tb.Window()` to use other `ttkbootstrap` themes.

---

## 💡 Notes

- All clients must connect to the **same server IP and port**.
- Designed for **text documents**. Very large files may affect Tkinter performance.
- Ideal for collaborative note-taking, coding experiments, or teaching demos.

---

## 📝 License

MIT License – Free to use, modify, and distribute.  
See the [LICENSE](LICENSE) file for details.

---

## ❤️ Contribution

- Star the repository if you find it useful!  
- Open issues or PRs for bug fixes, improvements, or new features.  

---

Enjoy **real-time collaborative editing** with colored cursors and live username labels!
