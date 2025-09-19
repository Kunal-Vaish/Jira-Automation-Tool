import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

from uploadTPTETC import JiraXrayUploader
from markTestCaseComplete import MarkTCCompletePage

def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", None)
        if base_path:
            return os.path.join(base_path, relative_path)
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

class HomePage(tk.Tk):
    def __init__(self, jira_url, username, password):
        super().__init__()
        self.title("Jira Automation Tool")

        try:
            self.state("zoomed")
        except:
            self.attributes("-zoomed", True)

        self.jira_url = jira_url
        self.username = username
        self.password = password

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.container = container
        self.frames = {}

        menu_page = MenuPage(container, self)
        self.frames[MenuPage] = menu_page
        menu_page.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MenuPage)

    def show_frame(self, page_class):
        frame = self.frames.get(page_class)
        if frame:
            frame.tkraise()

    def open_uploader(self):
        if JiraXrayUploader in self.frames:
            self.frames[JiraXrayUploader].destroy()
            del self.frames[JiraXrayUploader]

        uploader_page = JiraXrayUploader(
            self.container,
            controller=self,
            menu_page_class=MenuPage,
            jira_url=self.jira_url,
            username=self.username,
            password=self.password
        )
        self.frames[JiraXrayUploader] = uploader_page
        uploader_page.grid(row=0, column=0, sticky="nsew")
        self.show_frame(JiraXrayUploader)

    def open_mark_complete(self):
        if MarkTCCompletePage in self.frames:
            self.frames[MarkTCCompletePage].destroy()
            del self.frames[MarkTCCompletePage]

        page = MarkTCCompletePage(
            self.container,
            controller=self,
            menu_page_class=MenuPage,
            jira_url=self.jira_url,
            username=self.username,
            password=self.password
        )
        self.frames[MarkTCCompletePage] = page
        page.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MarkTCCompletePage)

    # def open_create_subtask(self):
    #     relative_path = os.path.join("SubTaskCreator Tool", "chrome.bat")
    #     bat_path = resource_path(relative_path)

    #     if os.path.exists(bat_path):
    #         try:
    #             subprocess.Popen([bat_path], shell=True)
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to open .bat file:\n{e}")
    #     else:
    #         messagebox.showerror("Error", f".bat file not found at:\n{bat_path}")

class MenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Top frame for Logout button
        top_frame = tk.Frame(self)
        top_frame.pack(fill="x", anchor="nw", padx=10, pady=10)
        tk.Button(top_frame, text="⬅ Logout / Back to Login",
                  command=self.back_to_login, bg="lightgray").pack(anchor="w")

        # Main content container
        container = tk.Frame(self)
        container.pack(pady=100)  # adjust as needed

        # ✅ Logged in user info
        tk.Label(container,
                 text=f"Logged in as: {controller.username}",
                 fg="green",
                 font=("Arial", 12, "bold")).pack(pady=5)

        tk.Label(container, text="Welcome to Jira Automation Tool",
                 font=("Arial", 18, "bold")).pack(pady=20)

        tk.Button(container, text="📤 Upload Test Cases",
                  command=controller.open_uploader,
                  width=30, height=2).pack(pady=10)

        tk.Button(container, text="✅ Mark Test Cases Complete",
                  command=controller.open_mark_complete,
                  width=30, height=2).pack(pady=10)

        # tk.Button(container, text="📝 Create SubTask",
        #           command=controller.open_create_subtask,
        #           width=30, height=2).pack(pady=10)
        
    def back_to_login(self):
        import loginPage
        self.controller.destroy()  # destroy HomePage session
        login_window = loginPage.LoginPage()
        login_window.mainloop()


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        jira_url, username, password = sys.argv[1:4]
    else:
        jira_url = username = password = ""
    app = HomePage(jira_url, username, password)
    app.mainloop()