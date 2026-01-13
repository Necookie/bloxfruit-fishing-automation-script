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

# --- 2. REELING CONFIGURATION (UPDATED) ---
# Calculated from your new box: (523, 795) to (1401, 870)
REEL_X = 523
REEL_Y = 832  # Exact vertical center of your box
REEL_W = 878
REEL_H = 1    # We still scan 1 pixel height for max speed

# --- 3. POPUP CLAIM CONFIGURATION ---
# (Kept from previous setting)
CLAIM_X = 934
CLAIM_Y = 626

class DayNightFisher:
    def __init__(self):
        self.active = False
        print("--- AUTOMATION: COORDINATES UPDATED ---")
        print(f"Scanning Bar at Y={REEL_Y} (Width={REEL_W})")
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
        print("[3] Reeling...")
        time.sleep(0.2)
        
        start_game = time.time()
        mouse_held = False
        last_fish_x = 0
        MOMENTUM_FACTOR = 1.5 

        while time.time() - start_game < 25:
            if keyboard.is_pressed('f2'):
                pydirectinput.mouseUp()
                return

            try:
                # Capture just the new bar area
                img = pyautogui.screenshot(region=(REEL_X, REEL_Y, REEL_W, REEL_H))
                row = np.array(img)[0]
            except: continue

            # --- DAY/NIGHT COLOR MATH ---
            R = row[:, 0].astype(int)
            G = row[:, 1].astype(int)
            B = row[:, 2].astype(int)

            # Score = Blue - Red - Green (Ignores Sky)
            blue_score = B - R - G
            fish_x = np.argmax(blue_score)
            
            # Find Bar (Brightest Object)
            bright_scores = np.sum(row, axis=1)
            bar_x = np.argmax(bright_scores)

            # End Condition: Bar Disappears
            if np.max(bright_scores) < 50:
                pydirectinput.mouseUp()
                break

            # Predictive Logic
            if last_fish_x == 0: last_fish_x = fish_x
            velocity = fish_x - last_fish_x
            last_fish_x = fish_x
            predicted_target = fish_x + (velocity * MOMENTUM_FACTOR)

            # Edge Clamping
            if fish_x > (REEL_W - 50): # Right Wall
                if not mouse_held:
                    pydirectinput.mouseDown()
                    mouse_held = True
                continue 
            
            if fish_x < 50: # Left Wall
                if mouse_held:
                    pydirectinput.mouseUp()
                    mouse_held = False
                continue

            # Movement
            dist = predicted_target - bar_x
            if dist > -10:
                if not mouse_held:
                    pydirectinput.mouseDown()
                    mouse_held = True
            else:
                if mouse_held:
                    pydirectinput.mouseUp()
                    mouse_held = False

    def phase_claim(self):
        print("[4] Catch Finished. Waiting for Popup...")
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
    bot = DayNightFisher()
    bot.start_loop()