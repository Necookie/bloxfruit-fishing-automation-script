import pyautogui
import pydirectinput
import time
import keyboard
import numpy as np

# --- 0. ZERO LATENCY SETUP ---
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False

# --- 1. SENSOR CONFIGURATION ---
SENSOR_CAST_X, SENSOR_CAST_Y = 137, 446
SENSOR_BITE_X, SENSOR_BITE_Y = 960, 540

# --- 2. REELING CONFIGURATION (Your Custom Coordinates) ---
REEL_X = 523
REEL_Y = 832
REEL_W = 878
REEL_H = 1    

# --- 3. CLAIM POPUP ---
CLAIM_X = 934
CLAIM_Y = 626

class ChaosFisher:
    def __init__(self):
        self.active = False
        print("--- AUTOMATION: CHAOS ADAPTIVE ENGINE ---")
        print("Features: Dynamic Velocity Prediction & Soft-Edge Handling")
        print("Controls: [F1] START | [F2] STOP")

    def check_pixel(self, x, y, color):
        try:
            pix = pyautogui.pixel(x, y)
            r, g, b = pix
            if color == 'green': return g > 100 and g > r and g > b
            elif color == 'red': return r > 130 and r > g + 20 and r > b + 20
        except: return False
        return False

    def phase_cast(self):
        print("\n[1] Casting...")
        pydirectinput.mouseDown() 
        start = time.time()
        while time.time() - start < 5:
            if keyboard.is_pressed('f2'): return False
            if self.check_pixel(SENSOR_CAST_X, SENSOR_CAST_Y, 'green'):
                pydirectinput.mouseUp()
                return True
            time.sleep(0.01)
        pydirectinput.mouseUp()
        return False

    def phase_wait(self):
        print("[2] Waiting for Bite...")
        start = time.time()
        while time.time() - start < 15:
            if keyboard.is_pressed('f2'): return False
            if self.check_pixel(SENSOR_BITE_X, SENSOR_BITE_Y, 'red'):
                pydirectinput.click()
                print("-> HOOKED!")
                return True
            time.sleep(0.05)
        return False

    def phase_reel(self):
        print("[3] Reeling (Chaos Mode)...")
        time.sleep(0.2)
        
        start_game = time.time()
        mouse_held = False
        last_fish_x = 0
        
        # We start with low prediction (Precision) and scale up if fish panics
        current_momentum = 1.0 

        while time.time() - start_game < 30: # Max minigame length
            if keyboard.is_pressed('f2'):
                pydirectinput.mouseUp()
                return

            try:
                img = pyautogui.screenshot(region=(REEL_X, REEL_Y, REEL_W, REEL_H))
                row = np.array(img)[0]
            except: continue

            # --- 1. SHARP VISION (Day/Night Safe) ---
            R = row[:, 0].astype(int)
            G = row[:, 1].astype(int)
            B = row[:, 2].astype(int)
            
            # Score = Blue - Red - Green (Isolates Fish from Sky)
            blue_score = B - R - G
            fish_x = np.argmax(blue_score)
            
            # Locate Bar (Brightest Object)
            bright_scores = np.sum(row, axis=1)
            bar_x = np.argmax(bright_scores)

            # Check if Minigame Ended (UI Disappeared)
            if np.max(bright_scores) < 50:
                pydirectinput.mouseUp()
                break

            # --- 2. CHAOS MATH (Dynamic Velocity) ---
            if last_fish_x == 0: last_fish_x = fish_x
            
            # Calculate Speed
            velocity = fish_x - last_fish_x
            last_fish_x = fish_x
            
            # ADAPTIVE LOGIC:
            # If velocity is high (chaos), increase prediction strength.
            # If velocity is low (calm), decrease it for precision.
            raw_speed = abs(velocity)
            if raw_speed > 20:
                current_momentum = 2.5 # Turbo Tracking
            elif raw_speed > 10:
                current_momentum = 1.8 # Fast Tracking
            else:
                current_momentum = 1.0 # Precision Tracking

            # Apply Prediction
            predicted_target = fish_x + (velocity * current_momentum)

            # --- 3. EDGE SAFETY (The Anti-Stick Fix) ---
            # Clamp the prediction so we don't chase ghosts off-screen
            predicted_target = max(0, min(predicted_target, REEL_W))

            dist = predicted_target - bar_x

            # --- 4. CONTROL LOGIC ---
            
            # RIGHT WALL SAFETY:
            # If the bar is near the Right Wall (> 90% across),
            # we refuse to Hold Click unless the fish is SIGNIFICANTLY ahead.
            # This prevents pinning the bar to the wall.
            RIGHT_WALL_THRESHOLD = REEL_W - 80
            
            if bar_x > RIGHT_WALL_THRESHOLD:
                # We are in the Danger Zone (Right Edge).
                # Only push if fish is REALLY trying to escape right.
                if dist > 20: 
                    if not mouse_held:
                        pydirectinput.mouseDown()
                        mouse_held = True
                else:
                    # Otherwise, let gravity pull us off the wall
                    if mouse_held:
                        pydirectinput.mouseUp()
                        mouse_held = False
            
            else:
                # Normal Operation (Center of Bar)
                # Standard Bang-Bang Control
                if dist > 0:
                    if not mouse_held:
                        pydirectinput.mouseDown()
                        mouse_held = True
                else:
                    if mouse_held:
                        pydirectinput.mouseUp()
                        mouse_held = False

    def phase_claim(self):
        print("[4] Waiting for Popup...")
        time.sleep(4.0) 
        pydirectinput.moveTo(CLAIM_X, CLAIM_Y)
        pydirectinput.click()
        time.sleep(1.0) 

    def start_loop(self):
        while True:
            if keyboard.is_pressed('f1'):
                if not self.active:
                    self.active = True
                    print(">>> STARTED <<<")
                    time.sleep(0.5)

            if keyboard.is_pressed('f2'):
                if self.active:
                    self.active = False
                    pydirectinput.mouseUp()
                    print(">>> STOPPED <<<")
                    time.sleep(0.5)

            if self.active:
                if self.phase_cast():
                    time.sleep(0.5)
                    if self.phase_wait():
                        self.phase_reel()
                        self.phase_claim()
                    else:
                        time.sleep(1)
                else:
                    time.sleep(1)

if __name__ == "__main__":
    bot = ChaosFisher()
    bot.start_loop()