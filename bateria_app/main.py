# main.py
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "assets", "lib"))

from ui.base_app import BatteryApp

if __name__ == "__main__":
    app = BatteryApp()
    app.mainloop()