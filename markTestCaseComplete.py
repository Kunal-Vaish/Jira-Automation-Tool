import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import traceback

class MarkTCCompletePage(tk.Frame):
    def __init__(self, master, controller=None, menu_page_class=None,
                 jira_url="", username="", password=""):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.menu_page_class = menu_page_class

        # ✅ Credentials passed from HomePage or standalone
        self.jira_url = jira_url
        self.username = username
        self.password = password
        self.auth = (self.username, self.password)
        self.headers = {"Content-Type": "application/json"}

        # Top frame for Back button
        if self.controller and self.menu_page_class:
            top_frame = tk.Frame(self)
            top_frame.pack(anchor="nw", padx=10, pady=10)
            self.back_btn = tk.Button(top_frame, text="⬅ Back", width=12, height=1, bg="lightgray",
                                      command=self.go_back)
            self.back_btn.pack(anchor="nw")
        else:
            self.back_btn = None

        # ✅ Show logged-in user info in green
        if self.username:
            tk.Label(self, text=f"Logged in as: {self.username}", fg="green",
                     font=("Arial", 12, "bold")).pack(pady=5)

        tk.Label(self, text="✅ Mark Test Cases Complete", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(self, text="Test Plan Number").pack()
        self.test_plan = tk.Entry(self, width=40)
        self.test_plan.pack(pady=5)

        self.mark_btn = tk.Button(self, text="Mark Complete", command=self.mark_complete)
        self.mark_btn.pack(pady=20)

        # General log
        tk.Label(self, text="Log", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.general_log = scrolledtext.ScrolledText(self, width=80, height=25)
        self.general_log.pack(fill="both", expand=True, padx=10, pady=5)
        self.general_log.config(state="disabled")

    def go_back(self):
        if self.controller and self.menu_page_class:
            self.controller.show_frame(self.menu_page_class)

    def log_message(self, msg):
        self.general_log.config(state="normal")
        self.general_log.insert(tk.END, f"[INFO] {msg}\n")
        self.general_log.see(tk.END)
        self.general_log.config(state="disabled")
        self.master.update()

    def log_error(self, msg):
        self.general_log.config(state="normal")
        self.general_log.insert(tk.END, f"[ERROR] {msg}\n")
        self.general_log.see(tk.END)
        self.general_log.config(state="disabled")
        self.master.update()

    def transition_issue(self, issue_key, status_name, direct=False):
        try:
            url_trans = f"{self.jira_url.rstrip('/')}/rest/api/2/issue/{issue_key}/transitions"
            resp = requests.get(url_trans, auth=self.auth, headers=self.headers)
            resp.raise_for_status()
            transitions = resp.json().get("transitions", [])

            if status_name.lower() == "done" and direct:
                target = next((t for t in transitions if t["name"].lower() == "done (direct)"), None)
            else:
                target = next((t for t in transitions if t["to"]["name"].lower() == status_name.lower()), None)

            if target:
                transition_id = target["id"]
                payload = {"transition": {"id": transition_id}}
                resp_post = requests.post(url_trans, json=payload, auth=self.auth, headers=self.headers)
                resp_post.raise_for_status()
                self.log_message(f"{issue_key} transitioned using '{target['name']}' → {status_name}")
            else:
                self.log_error(f"No transition to {status_name} found for {issue_key}")
        except Exception as e:
            self.log_error(f"Failed to transition {issue_key}: {e}")

    def mark_test_runs_passed(self, test_execution_key):
        try:
            url_tests = f"{self.jira_url.rstrip('/')}/rest/raven/1.0/api/testexec/{test_execution_key}/test"
            resp = requests.get(url_tests, auth=self.auth, headers=self.headers)
            resp.raise_for_status()
            tests = resp.json()
            test_keys = [test["key"] for test in tests]

            if not test_keys:
                self.log_error(f"No tests found under Test Execution {test_execution_key}")
                return

            url_batch = f"{self.jira_url.rstrip('/')}/rest/raven/1.0/testexec/{test_execution_key}/executeTestBatch"
            payload = {"keys": test_keys, "status": "0"}  # 0 = PASS
            resp_batch = requests.post(url_batch, json=payload, auth=self.auth, headers=self.headers)
            resp_batch.raise_for_status()
            self.log_message(f"Marked {len(test_keys)} tests as PASS in Test Execution {test_execution_key}")

            for test_key in test_keys:
                self.transition_issue(test_key, "Done")

            self.log_message(f"✅ All tests processed for Test Execution {test_execution_key}")

        except Exception as e:
            self.log_error(f"Failed to process Test Execution {test_execution_key}: {e}")

    def mark_complete(self):
        tp = self.test_plan.get().strip()
        if not tp:
            messagebox.showerror("Error", "Test Plan number is required")
            return

        if self.back_btn:
            self.back_btn.config(state="disabled")
        self.mark_btn.config(state="disabled")

        try:
            url_search = f"{self.jira_url.rstrip('/')}/rest/api/2/search"
            jql = f'"Test Plan" = {tp}'
            resp = requests.post(url_search, json={"jql": jql, "fields": ["key"]}, auth=self.auth, headers=self.headers)
            resp.raise_for_status()
            issues = resp.json().get("issues", [])
            exec_keys = [issue["key"] for issue in issues]

            if not exec_keys:
                self.log_error(f"No Test Executions found for Test Plan {tp}")
                return

            for exec_key in exec_keys:
                self.log_message(f"Processing Test Execution {exec_key}")
                self.mark_test_runs_passed(exec_key)
                self.transition_issue(exec_key, "Done", direct=True)

            self.transition_issue(tp, "Done", direct=True)

            messagebox.showinfo("Success", f"All Test Cases under Test Plan {tp} marked PASS and closed.")

        except Exception as e:
            self.log_error(f"Error: {e}")
            traceback.print_exc()
        finally:
            if self.back_btn:
                self.back_btn.config(state="normal")
            self.mark_btn.config(state="normal")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("Mark Test Cases Complete")
        try:
            root.state("zoomed")
        except:
            root.attributes("-zoomed", True)

        # Standalone run: credentials must be manually provided
        # Example placeholders (replace with actual credentials if testing standalone)
        jira_url = "https://your-jira-url"
        username = "your-username"
        password = "your-password"

        app = MarkTCCompletePage(root, jira_url=jira_url, username=username, password=password)
        app.pack(fill="both", expand=True)
        root.mainloop()
    except Exception:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise