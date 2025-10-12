# main.py
import sys
sys.path.append("assets\libs")

from ui.base_app import BatteryApp

if __name__ == "__main__":
    app = BatteryApp()
    app.mainloop()