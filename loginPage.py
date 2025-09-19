import tkinter as tk
from tkinter import messagebox
import sys
import os
import json
import keyring
import requests
import subprocess

SERVICE_NAME = "jira"

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(get_app_dir(), "jira_config.json")

def save_credentials(jira_url, username, password, remember=True):
    """Save Jira credentials for prefill."""
    data = {"jira_url": jira_url, "username": username}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)
    if remember:
        keyring.set_password(SERVICE_NAME, username, password)

def load_credentials():
    """Load Jira credentials (for prefill only)."""
    jira_url, username, password = "", "", ""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
            jira_url = data.get("jira_url", "")
            username = data.get("username", "")
    if username:
        password = keyring.get_password(SERVICE_NAME, username) or ""
    return jira_url, username, password

def validate_login(jira_url, username, password):
    """Check Jira credentials by calling /myself API."""
    try:
        url = jira_url.rstrip("/") + "/rest/api/2/myself"
        resp = requests.get(url, auth=(username, password))
        return resp.status_code == 200
    except Exception:
        return False

# 🔥 New: SubTask launcher (outside login)
def open_create_subtask():
    from homePage import resource_path   # reuse existing function
    relative_path = os.path.join("SubTaskCreator Tool", "chrome.bat")
    bat_path = resource_path(relative_path)

    if os.path.exists(bat_path):
        try:
            subprocess.Popen([bat_path], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open .bat file:\n{e}")
    else:
        messagebox.showerror("Error", f".bat file not found at:\n{bat_path}")

class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jira Login")

        try:
            self.state("zoomed")
        except:
            self.attributes("-zoomed", True)

        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(container, text="👋 Welcome! Please enter your Jira credentials below:",
                 font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(container, text="Jira URL").pack(pady=5)
        self.jira_url = tk.Entry(container, width=40)
        self.jira_url.pack(pady=5)

        tk.Label(container, text="Username").pack(pady=5)
        self.username = tk.Entry(container, width=40)
        self.username.pack(pady=5)

        tk.Label(container, text="Password").pack(pady=5)
        self.password = tk.Entry(container, show="*", width=40)
        self.password.pack(pady=5)

        self.remember_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Remember me", variable=self.remember_var).pack(pady=5)

        tk.Button(container, text="Login", command=self.login, width=20, height=2).pack(pady=20)

        # 🔥 New button for SubTask Tool (outside login)
        tk.Button(container,
                  text="📝 Create SubTask (No Login Required)",
                  command=open_create_subtask,
                  width=30, height=2).pack(pady=10)

        # Pre-fill if creds exist
        url, user, pwd = load_credentials()
        if url: self.jira_url.insert(0, url)
        if user: self.username.insert(0, user)
        if pwd: self.password.insert(0, pwd)

    def login(self):
        url = self.jira_url.get().strip()
        user = self.username.get().strip()
        pwd = self.password.get().strip()

        if not all([url, user, pwd]):
            messagebox.showerror("Error", "All fields are required!")
            return

        if validate_login(url, user, pwd):
            if self.remember_var.get():
                save_credentials(url, user, pwd, remember=True)

            messagebox.showinfo("Success", "✅ Login Successful!")

            # Destroy login window and launch HomePage in same process
            from homePage import HomePage
            self.destroy()
            home = HomePage(url, user, pwd)
            home.mainloop()
        else:
            messagebox.showerror("Error", "❌ Login Failed. Please check credentials.")

if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
