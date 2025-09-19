import tkinter as tk
from tkinter import messagebox
from uploadTPTETC import JiraXrayUploader
from markTestCaseComplete import MarkTCCompletePage
# from createSubTask import CreateSubTaskPage  # disabled for now

class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jira Automation Tool")
        try:
            self.state("zoomed")
        except:
            self.attributes("-zoomed", True)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.container = container
        self.frames = {}

        # Initialize Menu Page first
        menu_page = MenuPage(container, self)
        self.frames[MenuPage] = menu_page
        menu_page.grid(row=0, column=0, sticky="nsew")

        # Show menu by default
        self.show_frame(MenuPage)

    def show_frame(self, page_class):
        frame = self.frames.get(page_class)
        if frame:
            frame.tkraise()

    def open_uploader(self):
        # Remove existing uploader if exists
        if JiraXrayUploader in self.frames:
            self.frames[JiraXrayUploader].destroy()
            del self.frames[JiraXrayUploader]

        # Create a fresh uploader instance
        uploader_page = JiraXrayUploader(self.container, controller=self, menu_page_class=MenuPage)
        self.frames[JiraXrayUploader] = uploader_page
        uploader_page.grid(row=0, column=0, sticky="nsew")
        self.show_frame(JiraXrayUploader)

    def open_mark_complete(self):
        # Remove existing mark complete page if exists
        if MarkTCCompletePage in self.frames:
            self.frames[MarkTCCompletePage].destroy()
            del self.frames[MarkTCCompletePage]

        page = MarkTCCompletePage(self.container, controller=self, menu_page_class=MenuPage)
        self.frames[MarkTCCompletePage] = page
        page.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MarkTCCompletePage)

    # Placeholder for future SubTask page
    def open_create_subtask(self):
        # Currently disabled
        messagebox.showinfo("Info", "Create SubTask page not implemented yet.")


class MenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        container = tk.Frame(self)
        container.pack(pady=50)

        tk.Label(container, text="Welcome to Jira Automation Tool",
                 font=("Arial", 18, "bold")).pack(pady=20)

        tk.Button(container, text="📤 Upload Test Cases",
                  command=controller.open_uploader,
                  width=30, height=2).pack(pady=10)

        tk.Button(container, text="✅ Mark Test Cases Complete",
                  command=controller.open_mark_complete,
                  width=30, height=2).pack(pady=10)

        tk.Button(container, text="📝 Create SubTask",
                  state="disabled",  # disabled for now
                  command=controller.open_create_subtask,
                  width=30, height=2).pack(pady=10)


if __name__ == "__main__":
    app = HomePage()
    app.mainloop()