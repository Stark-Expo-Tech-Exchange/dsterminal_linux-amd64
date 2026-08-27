#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DSTerminal® Flask-SocketIO Windows Test
=======================================

Purpose:
    Verify that Flask + Flask-SocketIO works correctly in:
      1. Normal Python/venv execution
      2. PyInstaller-frozen Windows EXE

Architecture:
    Flask
      └── Flask-SocketIO
            └── threading

IMPORTANT:
    Eventlet is intentionally NOT used.

Why:
    Eventlet + PyInstaller on Windows can cause missing hub modules such as:
        eventlet.hubs.kqueue

    This test isolates the actual Flask-SocketIO functionality without
    Eventlet so that /socket.io/ is served correctly.

Requirements:
    Flask
    Flask-SocketIO
    python-socketio
    python-engineio
    simple-websocket

Example:
    python test_socketio.py

PyInstaller:
    pyinstaller --clean --onefile --console test_socketio.py
"""

import sys
import os
import time
import threading
import webbrowser
import traceback

# ============================================================
# WINDOWS / PYTHON SETTINGS
# ============================================================

if sys.platform.startswith("win"):
    # Prevent Python from buffering console output.
    os.environ.setdefault("PYTHONUNBUFFERED", "1")


# ============================================================
# IMPORT FLASK
# ============================================================

try:
    from flask import Flask, render_template_string

except ImportError as exc:
    print("=" * 70)
    print("[FATAL] Flask is not installed.")
    print("=" * 70)
    print(f"Error: {exc}")
    print()
    print("Install it with:")
    print("    pip install Flask")
    sys.exit(1)


# ============================================================
# IMPORT FLASK-SOCKETIO
# ============================================================

try:
    from flask_socketio import SocketIO, emit

except ImportError as exc:
    print("=" * 70)
    print("[FATAL] Flask-SocketIO is not installed.")
    print("=" * 70)
    print(f"Error: {exc}")
    print()
    print("Install the required packages with:")
    print()
    print("    pip install Flask Flask-SocketIO python-socketio")
    print("    pip install python-engineio simple-websocket")
    print()
    sys.exit(1)


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "dsterminal-test-key"

# ============================================================
# SOCKET.IO
#
# IMPORTANT:
# Explicitly use threading.
#
# DO NOT import eventlet.
# ============================================================

try:

    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        logger=False,
        engineio_logger=False,
    )

    print("[SOCKETIO] Flask-SocketIO initialized successfully")
    print("[SOCKETIO] Async mode: threading")

except Exception as exc:

    print("=" * 70)
    print("[FATAL] Flask-SocketIO initialization failed")
    print("=" * 70)

    print(f"Error: {exc}")
    print()

    traceback.print_exc()

    print()
    print("This test will NOT fall back to Flask-only mode.")
    print("Socket.IO must initialize successfully.")
    print()

    sys.exit(1)


# ============================================================
# HTML
# ============================================================

HTML_TEMPLATE = r"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>DSTerminal® Socket.IO Test</title>

    <!--
        Socket.IO JavaScript client.

        This test uses the official CDN first.
        If unavailable, the page will show a useful error.
    -->

    <script
        src="https://cdn.socket.io/4.8.1/socket.io.min.js"
        crossorigin="anonymous">
    </script>

    <style>

        * {
            box-sizing: border-box;
        }

        body {

            margin: 0;
            padding: 30px;

            font-family:
                Consolas,
                "Courier New",
                monospace;

            background:
                #070b12;

            color:
                #00ff88;
        }

        .container {

            max-width: 900px;

            margin: 0 auto;
        }

        h1 {

            color: #00ff88;

            margin-bottom: 10px;
        }

        .subtitle {

            color: #8b9bb4;

            margin-bottom: 30px;
        }

        .status {

            padding: 20px;

            border:
                2px solid
                #445;

            border-radius: 10px;

            background:
                rgba(255,255,255,0.03);

            margin-bottom: 20px;

            font-size: 18px;
        }

        .connected {

            border-color:
                #00ff88;

            color:
                #00ff88;

            box-shadow:
                0 0 20px
                rgba(0,255,136,0.12);
        }

        .disconnected {

            border-color:
                #ff3344;

            color:
                #ff3344;
        }

        .connecting {

            border-color:
                #ffaa00;

            color:
                #ffaa00;
        }

        .panel {

            padding: 20px;

            border:
                1px solid
                #243044;

            border-radius: 10px;

            background:
                #0c111c;
        }

        .panel-title {

            color:
                #7dd3fc;

            margin-bottom:
                15px;
        }

        #messages {

            max-height:
                500px;

            overflow-y:
                auto;
        }

        .msg {

            padding:
                10px 12px;

            margin:
                7px 0;

            background:
                rgba(0,255,136,0.04);

            border-left:
                3px solid
                #00ff88;

            border-radius:
                3px;
        }

        .error {

            border-left-color:
                #ff3344;

            color:
                #ff6677;
        }

        .info {

            border-left-color:
                #7dd3fc;

            color:
                #7dd3fc;
        }

        .footer {

            margin-top:
                30px;

            color:
                #58657a;

            font-size:
                12px;
        }

    </style>

</head>

<body>

<div class="container">

    <h1>🔮 DSTerminal®</h1>

    <div class="subtitle">
        Flask-SocketIO Windows Connectivity Test
    </div>

    <div
        id="status"
        class="status connecting"
    >
        ⏳ Connecting to Socket.IO server...
    </div>

    <div class="panel">

        <div class="panel-title">
            Socket.IO Events
        </div>

        <div id="messages"></div>

    </div>

    <div class="footer">

        DSTerminal® Socket.IO Diagnostic Test

    </div>

</div>


<script>

(function () {

    const statusElement =
        document.getElementById("status");

    const messagesElement =
        document.getElementById("messages");


    function addMessage(
        message,
        type = ""
    ) {

        const div =
            document.createElement("div");

        div.className =
            "msg " + type;

        div.textContent =
            message;

        messagesElement.appendChild(div);

        messagesElement.scrollTop =
            messagesElement.scrollHeight;
    }


    function setStatus(
        text,
        className
    ) {

        statusElement.textContent =
            text;

        statusElement.className =
            "status " + className;
    }


    /*
     * Verify that the Socket.IO JavaScript library
     * actually loaded.
     */

    if (
        typeof io === "undefined"
    ) {

        setStatus(
            "❌ Socket.IO JavaScript client failed to load",
            "disconnected"
        );

        addMessage(
            "The browser could not load the Socket.IO client.",
            "error"
        );

        addMessage(
            "Check your internet connection or bundle socket.io locally.",
            "error"
        );

        return;
    }


    addMessage(
        "Socket.IO JavaScript client loaded.",
        "info"
    );


    /*
     * Connect to the current Flask server.
     */

    const socket = io(
        window.location.origin,
        {
            transports: [
                "polling",
                "websocket"
            ],

            reconnection: true,

            reconnectionAttempts: Infinity,

            timeout: 10000
        }
    );


    /*
     * CONNECT
     */

    socket.on(
        "connect",
        function () {

            setStatus(
                "✅ Connected to DSTerminal Socket.IO server",
                "connected"
            );

            addMessage(
                "Socket.IO connection established."
            );

            addMessage(
                "Socket ID: " + socket.id
            );

            /*
             * Ask the server for diagnostic information.
             */

            socket.emit(
                "client_ready",
                {
                    browser:
                        navigator.userAgent,

                    timestamp:
                        Date.now()
                }
            );
        }
    );


    /*
     * DISCONNECT
     */

    socket.on(
        "disconnect",
        function (reason) {

            setStatus(
                "❌ Socket.IO disconnected",
                "disconnected"
            );

            addMessage(
                "Disconnected: " + reason,
                "error"
            );
        }
    );


    /*
     * CONNECT ERROR
     */

    socket.on(
        "connect_error",
        function (error) {

            setStatus(
                "❌ Socket.IO connection failed",
                "disconnected"
            );

            addMessage(
                "Connection error: " +
                error.message,
                "error"
            );
        }
    );


    /*
     * SERVER TEST MESSAGE
     */

    socket.on(
        "test_message",
        function (data) {

            if (
                data &&
                data.message
            ) {

                addMessage(
                    data.message
                );
            }
        }
    );


    /*
     * SERVER PONG
     */

    socket.on(
        "pong_test",
        function (data) {

            if (data) {

                addMessage(
                    "Pong received: " +
                    data.message
                );
            }
        }
    );


    /*
     * CLIENT READY RESPONSE
     */

    socket.on(
        "server_info",
        function (data) {

            if (!data) {
                return;
            }

            addMessage(
                "Server Socket.IO mode: " +
                data.async_mode
            );

            addMessage(
                "Server platform: " +
                data.platform
            );

            addMessage(
                "Server Python: " +
                data.python
            );
        }
    );


    /*
     * Send a ping every 2 seconds.
     */

    setInterval(
        function () {

            if (
                socket.connected
            ) {

                socket.emit(
                    "ping_test",
                    {
                        time:
                            Date.now()
                    }
                );
            }

        },
        2000
    );


})();

</script>

</body>

</html>
"""


# ============================================================
# HTTP ROUTE
# ============================================================

@app.route("/")
def index():

    return render_template_string(
        HTML_TEMPLATE
    )


# ============================================================
# SOCKET.IO EVENTS
# ============================================================

@socketio.on("connect")
def handle_connect():

    print(
        "[SOCKETIO] Client connected"
    )

    emit(
        "test_message",
        {
            "message":
                "Welcome to DSTerminal Socket.IO! 🎉"
        }
    )


@socketio.on("disconnect")
def handle_disconnect():

    print(
        "[SOCKETIO] Client disconnected"
    )


@socketio.on("client_ready")
def handle_client_ready(data):

    print(
        "[SOCKETIO] Client ready"
    )

    if data:

        print(
            f"[SOCKETIO] Browser: "
            f"{data.get('browser', 'Unknown')}"
        )

    emit(
        "server_info",
        {
            "async_mode":
                socketio.async_mode,

            "platform":
                sys.platform,

            "python":
                sys.version.split()[0]
        }
    )


@socketio.on("ping_test")
def handle_ping(data):

    current_time = time.strftime(
        "%H:%M:%S"
    )

    print(
        f"[SOCKETIO] Ping received "
        f"at {current_time}"
    )

    emit(
        "pong_test",
        {
            "message":
                f"Server time: {current_time}"
        }
    )


# ============================================================
# SERVER STARTUP
# ============================================================

def print_banner():

    frozen = getattr(
        sys,
        "frozen",
        False
    )

    print()
    print("=" * 70)
    print("🔮 DSTerminal® SOCKET.IO WINDOWS TEST")
    print("=" * 70)

    print(
        f"📍 Server: "
        f"http://localhost:5000"
    )

    print(
        f"🌐 Network: "
        f"http://0.0.0.0:5000"
    )

    print(
        f"📦 Frozen EXE: "
        f"{frozen}"
    )

    print(
        f"🐍 Python: "
        f"{sys.version.split()[0]}"
    )

    print(
        f"🖥️ Platform: "
        f"{sys.platform}"
    )

    print(
        f"⚡ Async mode: "
        f"{socketio.async_mode}"
    )

    print("=" * 70)
    print(
        "Socket.IO is REQUIRED for this test."
    )
    print(
        "No DummySocketIO fallback is enabled."
    )
    print("=" * 70)
    print()


# ============================================================
# BROWSER
# ============================================================

def open_browser():

    time.sleep(2)

    url = (
        "http://localhost:5000"
    )

    try:

        opened = webbrowser.open(
            url,
            new=2
        )

        if opened:

            print(
                f"[OK] Browser opened: {url}"
            )

        else:

            print(
                "[WARNING] Browser could not "
                "be opened automatically."
            )

            print(
                f"[INFO] Open manually: {url}"
            )

    except Exception as exc:

        print(
            f"[WARNING] Browser error: {exc}"
        )

        print(
            f"[INFO] Open manually: {url}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print_banner()

    print(
        "[SERVER] Starting Flask-SocketIO..."
    )

    print(
        "[SERVER] Press CTRL+C to stop."
    )

    print()

    browser_thread = threading.Thread(
        target=open_browser,
        daemon=True
    )

    browser_thread.start()

    try:

        socketio.run(
            app,
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )

    except KeyboardInterrupt:

        print()
        print(
            "[SERVER] Shutdown requested."
        )

    except Exception as exc:

        print()
        print("=" * 70)
        print("[FATAL] Server failed")
        print("=" * 70)
        print(
            f"Error: {exc}"
        )

        traceback.print_exc()

        print()
        sys.exit(1)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()