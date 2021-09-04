import websocket
import _thread
import time


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("ws opened")


if __name__ == "__main__":
    websocket.enableTrace(True)
    host = "192.168.1.15"
    port = 8005
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(f"ws://{host}:{port}/transform",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
