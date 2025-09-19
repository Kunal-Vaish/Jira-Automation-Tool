import os
import json
import keyring
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import csv
from collections import defaultdict
import xlrd
import openpyxl
import tempfile
import traceback
import time

CONFIG_FILE = os.path.expanduser("~/.jira_config.json")
SERVICE_NAME = "jira"

def save_credentials(jira_url, username, password):
    data = {"jira_url": jira_url, "username": username}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)
    keyring.set_password(SERVICE_NAME, username, password)

def load_credentials():
    jira_url, username, password = "", "", ""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
            jira_url = data.get("jira_url", "")
            username = data.get("username", "")
    if username:
        password = keyring.get_password(SERVICE_NAME, username) or ""
    return jira_url, username, password

class JiraXrayUploader:
    def __init__(self, master):
        self.master = master
        master.title("Jira Test Case Uploader")

        # Make window resizable & support maximize
        try:
            master.state("zoomed")  # Windows
        except:
            master.attributes("-zoomed", True)  # Linux/Mac

        # Jira credentials
        # tk.Label(master, text="Jira URL:").grid(row=0, column=0, sticky="e")
        # self.jira_url = tk.Entry(master, width=50)
        # self.jira_url.grid(row=0, column=1)

        # tk.Label(master, text="Jira Username:").grid(row=1, column=0, sticky="e")
        # self.username = tk.Entry(master, width=50)
        # self.username.grid(row=1, column=1)

        # tk.Label(master, text="Jira Password:").grid(row=2, column=0, sticky="e")
        # self.password = tk.Entry(master, show="*", width=50)
        # self.password.grid(row=2, column=1)

                # Configure grid inside container
        # Create container frame
        container = tk.Frame(master)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        for i in range(3):
            container.grid_columnconfigure(i, weight=1)

        # Row counter
        row = 0

        # Jira URL
        tk.Label(container, text="Jira URL").grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        self.jira_url = tk.Entry(container, width=40)
        self.jira_url.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        # Username
        tk.Label(container, text="Jira Username").grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        self.username = tk.Entry(container, width=40)
        self.username.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        # Password
        tk.Label(container, text="Jira Password").grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        self.password = tk.Entry(container, show="*", width=40)
        self.password.grid(row=row, column=0, columnspan=3, pady=5)
        #row += 1


        # Load saved credentials
        jira_url_val, username_val, password_val = load_credentials()
        self.jira_url.insert(0, jira_url_val)
        self.username.insert(0, username_val)
        self.password.insert(0, password_val)

        # Remember me checkbox
        self.remember_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Remember me", variable=self.remember_var).grid(row=row, column=2, pady=1)
        row += 1

        # User Story Number
        tk.Label(container, text="User Story Number").grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        self.user_story = tk.Entry(container, width=40)
        self.user_story.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        # File selection
        tk.Button(container, text="Select File (.csv/.xls/.xlsx)", command=self.select_file).grid(row=row, column=0, columnspan=3, pady=10)
        row += 1
        self.file_label = tk.Label(container, text="No file selected")
        self.file_label.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        # Upload button
        self.upload_btn = tk.Button(container, text="Upload Test Cases", command=self.upload)
        self.upload_btn.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1

        # Log/output box
        self.log = scrolledtext.ScrolledText(container, width=100, height=25)
        self.log.grid(row=row, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        container.grid_rowconfigure(row, weight=1)

        self.file_path = None
        self.temp_csv = None

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV, XLS, XLSX", "*.csv;*.xls;*.xlsx")])
        self.file_label.config(text=self.file_path or "No file selected")

    def log_message(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.master.update()
        time.sleep(0.1)  # small buffer so messages appear steadily

    def ensure_csv(self, file_path):
        if file_path.endswith(".csv"):
            return file_path
        elif file_path.endswith(".xls"):
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)
            tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8")
            writer = csv.writer(tmp_csv)
            for r in range(sheet.nrows):
                writer.writerow(sheet.row_values(r))
            tmp_csv.close()
            self.temp_csv = tmp_csv.name
            return tmp_csv.name
        elif file_path.endswith(".xlsx"):
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8")
            writer = csv.writer(tmp_csv)
            for row in sheet.iter_rows(values_only=True):
                writer.writerow([cell if cell is not None else "" for cell in row])
            tmp_csv.close()
            self.temp_csv = tmp_csv.name
            return tmp_csv.name
        else:
            raise ValueError("Unsupported file type. Only .csv, .xls, and .xlsx are allowed.")

    def upload(self):
        if not all([self.jira_url.get(), self.username.get(), self.password.get(), self.user_story.get(), self.file_path]):
            messagebox.showerror("Error", "All fields and file selection are required")
            return

        if self.remember_var.get():
            save_credentials(self.jira_url.get(), self.username.get(), self.password.get())

        try:
            csv_path = self.ensure_csv(self.file_path)
        except Exception as e:
            messagebox.showerror("Error", f"File conversion failed: {e}")
            return

        auth = (self.username.get(), self.password.get())
        headers = {"Content-Type": "application/json"}
        user_story_key = self.user_story.get().strip()
        project_key = user_story_key.split("-")[0]
        url_issue = f"{self.jira_url.get().rstrip('/')}/rest/api/2/issue"

        try:
            # Create Test Plan
            self.log_message("=== Creating Test Plan ===")
            test_plan_payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"Test Plan for {user_story_key}",
                    "description": f"Created automated Test Plan for {user_story_key} via Kunalv's App",
                    "issuetype": {"name": "Test Plan"},
                    "assignee": {"name": self.username.get()},
                }
            }
            resp = requests.post(url_issue, json=test_plan_payload, auth=auth, headers=headers)
            resp.raise_for_status()
            test_plan_key = resp.json()["key"]
            self.log_message(f"✅ Test Plan created: {test_plan_key}")

            # Link Test Plan to User Story
            link_payload = {
                "type": {"name": "Relates"},
                "inwardIssue": {"key": test_plan_key},
                "outwardIssue": {"key": user_story_key},
            }
            requests.post(f"{self.jira_url.get().rstrip('/')}/rest/api/2/issueLink", json=link_payload, auth=auth, headers=headers)

            # Create Test Execution
            self.log_message("=== Creating Test Execution ===")
            test_execution_payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"Test Execution for {user_story_key}",
                    "description": f"Created automated Test Execution for {user_story_key} via Kunalv's App",
                    "issuetype": {"name": "Test Execution"},
                    "assignee": {"name": self.username.get()},
                    "customfield_11368": [test_plan_key]
                }
            }
            resp_exec = requests.post(url_issue, json=test_execution_payload, auth=auth, headers=headers)
            resp_exec.raise_for_status()
            test_execution_key = resp_exec.json()["key"]
            self.log_message(f"✅ Test Execution created: {test_execution_key}")

            # Read CSV and create Test Cases
            self.log_message("=== Creating Test Cases ===")
            tests = defaultdict(list)
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    tests[row["S.No."]].append(row)

            created_tests = []
            for sno, rows in tests.items():
                first = rows[0]
                summary = first.get("Test Name") or f"Test {sno}"
                description = first.get("HLTC Description & Pre-condition") or ""
                priority = first.get("Priority") or "Medium"
                fix_version = first.get("Fix Version/s")
                fix_versions = [{"name": fix_version}] if fix_version else []
                labels = list(filter(None, (first.get("labels") or "").split(",")))
                assignee = first.get("Designer") or self.username.get()

                # Build steps
                steps = []
                for i, r in enumerate(rows, start=1):
                    action = r.get("LLTC Description") or ""
                    expected = r.get("Expected result") or ""
                    if action:
                        steps.append({
                            "index": i,
                            "fields": {
                                "Action": action,
                                "Data": "",
                                "Expected Result": expected
                            }
                        })

                test_payload = {
                    "fields": {
                        "project": {"key": project_key},
                        "summary": summary,
                        "description": description,
                        "issuetype": {"name": "Test"},
                        "priority": {"name": priority},
                        "fixVersions": fix_versions,
                        "assignee": {"name": assignee},
                        "labels": labels,
                        "customfield_11341": {"id": "12281"},   # Test Type: Manual
                        "customfield_11345": {"steps": steps},  # Steps
                        "customfield_11350": [test_plan_key]   # Link Test Plan
                    }
                }

                resp_test = requests.post(url_issue, json=test_payload, auth=auth, headers=headers)
                resp_test.raise_for_status()
                test_key = resp_test.json()["key"]
                created_tests.append(test_key)
                self.log_message(f"✅ Created Test: {test_key}")

                # Link Test Case to Test Execution
                link_payload = {
                    "type": {"name": "Tests(1)"},
                    "inwardIssue": {"key": test_execution_key},  # Test Execution
                    "outwardIssue": {"key": test_key}            # Test Case
                }
                resp_link = requests.post(
                    f"{self.jira_url.get().rstrip('/')}/rest/api/2/issueLink",
                    json=link_payload,
                    auth=auth,
                    headers=headers
                )
                resp_link.raise_for_status()
                self.log_message(f"🔗 Linked Test Case {test_key} to Test Execution {test_execution_key}")
                time.sleep(0.2)  # small buffer so GUI stays responsive

            #self.log_message(f"All test cases created: {', '.join(created_tests)}")
            self.log_message(f"All {len(created_tests)} test cases created under {test_plan_key}")
            messagebox.showinfo("Success", f"Uploaded {len(created_tests)} test cases under {test_plan_key}")

        except Exception as e:
            self.log_message(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            if self.temp_csv and os.path.exists(self.temp_csv):
                os.remove(self.temp_csv)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = JiraXrayUploader(root)
        root.mainloop()
    except Exception:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise