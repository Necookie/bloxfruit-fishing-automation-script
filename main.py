import pyautogui
import pydirectinput
import time
import keyboard
import numpy as np

# --- 0. SPEED & SAFETY ---
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False

# --- 1. SENSOR CONFIGURATION ---
SENSOR_CAST_X, SENSOR_CAST_Y = 137, 446
SENSOR_BITE_X, SENSOR_BITE_Y = 960, 540

# --- 2. REELING CONFIGURATION ---
# UPDATE THIS to match your specific resolution/bar location
REEL_X, REEL_Y = 510, 830 
REEL_W, REEL_H = 900, 1

class PredictiveFisher:
    def __init__(self):
        self.active = False
        print("--- AUTOMATION: PREDICTIVE MOMENTUM ENGINE ---")
        print("Fixes: Lag ('Sleeping'), Edge Sticking, Prediction")
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
        print("[2] Waiting...")
        start = time.time()
        while time.time() - start < 15:
            if keyboard.is_pressed('f2'): return False
            if self.check_pixel(SENSOR_BITE_X, SENSOR_BITE_Y, 'red'):
                pydirectinput.click()
                return True
            time.sleep(0.05)
        return False

    def phase_reel(self):
        print("[3] PREDICTIVE REELING (No Console Logs)...")
        time.sleep(0.2)
        
        start_game = time.time()
        mouse_held = False
        
        # MOTION TRACKING VARIABLES
        last_fish_x = 0
        
        # PREDICTION TUNING
        # How many pixels to aim ahead? 
        # Increase this if it still trails behind.
        MOMENTUM_FACTOR = 1.5 

        while time.time() - start_game < 25:
            if keyboard.is_pressed('f2'):
                pydirectinput.mouseUp()
                return

            # 1. Capture Image
            try:
                img = pyautogui.screenshot(region=(REEL_X, REEL_Y, REEL_W, REEL_H))
                row = np.array(img)[0]
            except: continue

            # 2. Find Objects
            # Fish = Blue Channel Spike
            blue_diff = row[:, 2].astype(int) - row[:, 0].astype(int)
            fish_x = np.argmax(blue_diff)
            
            # Bar = Brightness Spike
            bright_scores = np.sum(row, axis=1)
            bar_x = np.argmax(bright_scores)

            # Check Game Over
            if np.max(bright_scores) < 50:
                pydirectinput.mouseUp()
                break

            # 3. VELOCITY CALCULATION (Prediction)
            if last_fish_x == 0: last_fish_x = fish_x # First frame init
            
            # Calculate speed: (Current - Last)
            velocity = fish_x - last_fish_x
            last_fish_x = fish_x

            # Apply Prediction: Aim where the fish IS GOING, not where it IS.
            predicted_target = fish_x + (velocity * MOMENTUM_FACTOR)

            # 4. EDGE CLAMPING (Fixes "Stuck at side" bug)
            # If fish is hugging the right wall (>850px), FORCE HOLD
            if fish_x > (REEL_W - 50):
                if not mouse_held:
                    pydirectinput.mouseDown()
                    mouse_held = True
                continue # Skip the rest of the logic
            
            # If fish is hugging left wall (<50px), FORCE RELEASE
            if fish_x < 50:
                if mouse_held:
                    pydirectinput.mouseUp()
                    mouse_held = False
                continue

            # 5. CONTROL LOGIC
            # Use the PREDICTED target, not the actual fish_x
            dist = predicted_target - bar_x
            
            # Offset: Aim slightly right (-10) to fight gravity
            if dist > -10:
                if not mouse_held:
                    pydirectinput.mouseDown()
                    mouse_held = True
            else:
                if mouse_held:
                    pydirectinput.mouseUp()
                    mouse_held = False
            
            # NO PRINTS HERE. Printing causes "Sleeping" lag.

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
                        time.sleep(3.0)
                    else:
                        time.sleep(1)
                else:
                    time.sleep(1)

if __name__ == "__main__":
    bot = PredictiveFisher()
    bot.start_loop()