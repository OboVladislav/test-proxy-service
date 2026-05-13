import json
import threading
import tkinter as tk
from tkinter import messagebox

import requests
import websocket

API_URL = "http://localhost"
WS_URL = "ws://localhost"


class ProxyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proxy Client")
        self.resizable(False, False)
        self.geometry("420x320")

        self._ws = None
        self._ws_thread = None
        self._user_id = None
        self._token = None

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 16, "pady": 6}

        tk.Label(self, text="Ключ активации:", font=("", 11)).pack(**pad, anchor="w")

        self._key_var = tk.StringVar()
        self._key_entry = tk.Entry(self, textvariable=self._key_var, font=("", 11), width=36)
        self._key_entry.pack(**pad, fill="x")

        btn_frame = tk.Frame(self)
        btn_frame.pack(**pad, fill="x")

        self._connect_btn = tk.Button(
            btn_frame, text="Подключиться", font=("", 11),
            bg="#1976D2", fg="white", command=self._on_connect,
        )
        self._connect_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self._disconnect_btn = tk.Button(
            btn_frame, text="Отключиться", font=("", 11),
            bg="#D32F2F", fg="white", command=self._on_disconnect,
            state="disabled",
        )
        self._disconnect_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))

        tk.Label(self, text="Статус:", font=("", 11)).pack(**pad, anchor="w")

        self._status_var = tk.StringVar(value="Ожидание")
        self._status_label = tk.Label(
            self, textvariable=self._status_var,
            font=("", 12, "bold"), fg="gray",
        )
        self._status_label.pack(**pad)

        self._info_var = tk.StringVar()
        tk.Label(self, textvariable=self._info_var, font=("", 10), fg="#555").pack(**pad)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_connect(self):
        key = self._key_var.get().strip()
        if not key:
            messagebox.showerror("Ошибка", "Введите ключ активации")
            return

        self._connect_btn.config(state="disabled")
        self._set_status("Подключение...", "orange")

        threading.Thread(target=self._activate, args=(key,), daemon=True).start()

    def _on_disconnect(self):
        self._disconnect_btn.config(state="disabled")
        threading.Thread(target=self._do_disconnect, daemon=True).start()

    def _activate(self, key: str):
        try:
            resp = requests.post(
                f"{API_URL}/api/activate-key",
                json={"activation_key": key},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                self._user_id = data["user_id"]
                self._token = data["access_token"]
                info = f"{data['protocol']}://{data['host']}:{data['port']}"
                self.after(0, lambda: self._info_var.set(info))
                self.after(0, lambda: self._disconnect_btn.config(state="normal"))
                self._start_websocket(self._user_id)
            elif resp.status_code == 503:
                self.after(0, lambda: self._set_status("Все прокси заняты", "red"))
                self.after(0, lambda: self._connect_btn.config(state="normal"))
            else:
                detail = resp.json().get("detail", "Неверный ключ")
                self.after(0, lambda: self._set_status(f"Ошибка: {detail}", "red"))
                self.after(0, lambda: self._connect_btn.config(state="normal"))
        except requests.exceptions.ConnectionError:
            self.after(0, lambda: self._set_status("Нет связи с сервером", "red"))
            self.after(0, lambda: self._connect_btn.config(state="normal"))

    def _do_disconnect(self):
        if self._ws:
            self._ws.close()
            self._ws = None

        if self._user_id and self._token:
            try:
                requests.post(
                    f"{API_URL}/api/disconnect",
                    headers={"Authorization": f"Bearer {self._token}"},
                    timeout=5,
                )
            except Exception:
                pass

        self._user_id = None
        self._token = None
        self.after(0, self._reset_ui)

    def _reset_ui(self):
        self._set_status("Ожидание", "gray")
        self._info_var.set("")
        self._key_var.set("")
        self._connect_btn.config(state="normal")
        self._disconnect_btn.config(state="disabled")

    # ── WebSocket ─────────────────────────────────────────────────────────────

    def _start_websocket(self, user_id: int):
        url = f"{WS_URL}/ws/status/{user_id}"
        self._ws = websocket.WebSocketApp(
            url,
            on_message=self._on_ws_message,
            on_error=self._on_ws_error,
            on_close=self._on_ws_close,
        )
        self._ws_thread = threading.Thread(target=self._ws.run_forever, daemon=True)
        self._ws_thread.start()

    def _on_ws_message(self, ws, raw: str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return

        status = data.get("status", "disconnected")
        if status == "connected":
            info = f"{data.get('protocol')}://{data.get('host')}:{data.get('port')}"
            self.after(0, lambda: self._set_status("Подключено", "green"))
            self.after(0, lambda: self._info_var.set(info))
        else:
            self.after(0, lambda: self._set_status("Отключено", "red"))
            self.after(0, lambda: self._info_var.set(""))

    def _on_ws_error(self, ws, error):
        self.after(0, lambda: self._set_status("Ошибка WebSocket", "red"))

    def _on_ws_close(self, ws, code, msg):
        self.after(0, lambda: self._set_status("Соединение закрыто", "gray"))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, text: str, color: str):
        self._status_var.set(text)
        self._status_label.config(fg=color)

    def destroy(self):
        if self._ws:
            self._ws.close()
        super().destroy()


if __name__ == "__main__":
    app = ProxyApp()
    app.mainloop()
