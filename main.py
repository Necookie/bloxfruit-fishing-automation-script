import pyautogui
import pydirectinput
import time
import keyboard

# --- SENSOR CONFIGURATION ---
# 1. CASTING SENSOR (Green Bar)
SENSOR_CAST_X = 137
SENSOR_CAST_Y = 446
GREEN_THRESHOLD = 100

# 2. BITE SENSOR (Red Exclamation)
SENSOR_BITE_X = 960
SENSOR_BITE_Y = 540
RED_THRESHOLD = 130 

class PrecisionFisher:
    def __init__(self):
        self.active = False
        print("--- HARVARD AUTOMATION: PHASE 2 (STRICT MODE) ---")
        print(f"Cast Sensor: ({SENSOR_CAST_X}, {SENSOR_CAST_Y})")
        print(f"Bite Sensor: ({SENSOR_BITE_X}, {SENSOR_BITE_Y})")
        print("Controls: [F1] START | [F2] STOP")

    def check_pixel(self, x, y, color):
        """
        Helper to check pixel colors safely.
        """
        try:
            pix = pyautogui.pixel(x, y)
            r, g, b = pix
            
            if color == 'green':
                # Bright Green and Dominant
                return g > GREEN_THRESHOLD and g > r and g > b
            elif color == 'red':
                # Bright Red and Dominant
                return r > RED_THRESHOLD and r > g + 20 and r > b + 20
        except:
            return False
        return False

    def phase_cast(self):
        """
        ACTION: Hold Left Click.
        TRIGGER: Green at (137, 446).
        RESULT: Release Left Click (NO CLICK, JUST RELEASE).
        """
        print("\n[1] Casting... (Holding Button)")
        pydirectinput.mouseDown() 
        
        start_time = time.time()
        while time.time() - start_time < 5: # 5 second timeout
            if keyboard.is_pressed('f2'): return False
            
            # Watch for Green
            if self.check_pixel(SENSOR_CAST_X, SENSOR_CAST_Y, 'green'):
                print("[1] Green Detected -> Releasing Button.")
                pydirectinput.mouseUp() # <--- CRITICAL: JUST RELEASE
                return True
            
            time.sleep(0.01) # Fast scan
            
        print("[WARN] Cast Timeout. Releasing safety.")
        pydirectinput.mouseUp()
        return False

    def phase_wait(self):
        """
        ACTION: Do Nothing (Observe).
        TRIGGER: Red at (960, 540).
        RESULT: Single Click.
        """
        print("[2] Watching for Bite... (Silence Mode)")
        
        start_time = time.time()
        # Wait up to 15 seconds for the fish
        while time.time() - start_time < 15:
            if keyboard.is_pressed('f2'): return False

            # Watch for Red Exclamation
            if self.check_pixel(SENSOR_BITE_X, SENSOR_BITE_Y, 'red'):
                print("[2] ! BITE ! -> Hooking (Single Click).")
                pydirectinput.click() # <--- SINGLE CLICK TO HOOK
                return True
            
            time.sleep(0.05) # Scan every 50ms
            
        print("[WARN] No bite detected. Resetting.")
        return False

    def start_loop(self):
        while True:
            # --- CONTROLS ---
            if keyboard.is_pressed('f1'):
                if not self.active:
                    print(">>> ENGAGED (F1) <<<")
                    self.active = True
                    time.sleep(0.5)

            if keyboard.is_pressed('f2'):
                if self.active:
                    print(">>> STOPPED (F2) <<<")
                    self.active = False
                    pydirectinput.mouseUp() # Ensure mouse isn't stuck holding
                    time.sleep(0.5)

            # --- AUTOMATION LOGIC ---
            if self.active:
                # Step 1: Perform Cast
                cast_success = self.phase_cast()
                
                if cast_success:
                    # Brief pause to let the bobber hit water
                    time.sleep(0.5)
                    
                    # Step 2: Wait for Bite
                    bite_success = self.phase_wait()
                    
                    if bite_success:
                        print("[3] Catch Sequence Finished. Looping in 2s...")
                        time.sleep(2) # Wait for animation/minigame reset
                    else:
                        time.sleep(1) # Retry delay if missed
                else:
                    time.sleep(1) # Retry delay if cast failed

if __name__ == "__main__":
    bot = PrecisionFisher()
    bot.start_loop()