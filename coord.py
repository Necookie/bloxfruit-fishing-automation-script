from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        print(f"Left click at X: {x}, Y: {y}")

print("Listening for left mouse clicks... Press CTRL+C to stop.")

with mouse.Listener(on_click=on_click) as listener:
    listener.join()
