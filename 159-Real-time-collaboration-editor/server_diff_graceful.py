# server_diff_graceful.py
import asyncio
import json
import websockets
from difflib import SequenceMatcher

PORT = 8765

# ---------------- GLOBAL STATE ---------------- #
document_content = ""  # Shared document
clients = {}  # websocket -> username
lock = asyncio.Lock()  # Async lock for safe updates

# ---------------- DIFF HELPERS ---------------- #
def apply_diff(content, ops):
    """Apply a list of diff operations to content"""
    new_content = []
    for op in ops:
        tag = op["tag"]
        i1, i2, text = op["i1"], op["i2"], op.get("text", "")
        if tag == "equal":
            new_content.append(content[i1:i2])
        elif tag in ("replace", "insert"):
            new_content.append(text)
        elif tag == "delete":
            pass  # skip deleted text
    return "".join(new_content)

# ---------------- BROADCAST ---------------- #
async def broadcast(message, exclude=None):
    """Send a message to all clients except the sender"""
    if clients:
        websockets_to_send = [ws for ws in clients if ws != exclude]
        if websockets_to_send:
            await asyncio.gather(*(ws.send(message) for ws in websockets_to_send))

# ---------------- HANDLER ---------------- #
async def handler(websocket):
    global document_content
    # Receive initial username
    username = await websocket.recv()
    clients[websocket] = username
    print(f"[+] {username} connected")
    
    # Send full document to new client
    await websocket.send(json.dumps({"type": "full_update", "content": document_content}))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            async with lock:
                if data["type"] == "diff":
                    # Apply diff to server content
                    document_content = apply_diff(document_content, data["ops"])
                    # Broadcast diff to others
                    await broadcast(json.dumps({"type": "diff", "ops": data["ops"], "user": username}), exclude=websocket)
                
                elif data["type"] == "cursor":
                    # Broadcast cursor positions to other clients
                    await broadcast(json.dumps({
                        "type": "cursor",
                        "position": data["position"],
                        "user": username
                    }), exclude=websocket)
                    
    except websockets.ConnectionClosed:
        print(f"[-] {username} disconnected")
    finally:
        if websocket in clients:
            del clients[websocket]

# ---------------- START SERVER ---------------- #
async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print(f"Diff-Based Collaborative Server running on port {PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.")
