import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import csv
import xlrd
import openpyxl
import tempfile
import os
import traceback

class JiraXrayUploader:
    def __init__(self, master):
        self.master = master
        master.title("Jira Test Case Uploader")

        # Jira credentials
        tk.Label(master, text="Jira URL:").grid(row=0, column=0, sticky="e")
        self.jira_url = tk.Entry(master, width=50)
        self.jira_url.grid(row=0, column=1)

        tk.Label(master, text="Username:").grid(row=1, column=0, sticky="e")
        self.username = tk.Entry(master, width=50)
        self.username.grid(row=1, column=1)

        tk.Label(master, text="Password/API Token:").grid(row=2, column=0, sticky="e")
        self.password = tk.Entry(master, show="*", width=50)
        self.password.grid(row=2, column=1)

        tk.Label(master, text="User Story Key:").grid(row=3, column=0, sticky="e")
        self.user_story = tk.Entry(master, width=50)
        self.user_story.grid(row=3, column=1)

        # File selection
        tk.Button(master, text="Select File (.csv/.xls/.xlsx)", command=self.select_file).grid(row=4, column=0, columnspan=2)
        self.file_label = tk.Label(master, text="No file selected")
        self.file_label.grid(row=5, column=0, columnspan=2)

        # Upload button
        tk.Button(master, text="Upload Test Cases", command=self.upload).grid(row=6, column=0, columnspan=2)

        # Log/output box
        self.log = scrolledtext.ScrolledText(master, width=70, height=20)
        self.log.grid(row=7, column=0, columnspan=2)

        self.file_path = None
        self.temp_csv = None  # Holds temporary CSV path if XLS/XLSX is converted

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV, XLS, XLSX", "*.csv;*.xls;*.xlsx")])
        self.file_label.config(text=self.file_path or "No file selected")

    def log_message(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.master.update()

    def ensure_csv(self, file_path):
        """Converts Excel files to CSV if needed, returns CSV path."""
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

        # Convert Excel to CSV if needed
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
            # === Step 1: Create Test Plan ===
            self.log_message("=== Creating Test Plan ===")
            test_plan_payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"Test Plan for {user_story_key}",
                    "description": f"Created via Kunalv's Test uploader App for {user_story_key}",
                    "issuetype": {"name": "Test Plan"}
                }
            }

            resp = requests.post(url_issue, json=test_plan_payload, auth=auth, headers=headers)
            resp.raise_for_status()
            test_plan_key = resp.json()["key"]
            self.log_message(f"✅ Test Plan created: {test_plan_key}")

            # === Step 2: Link Test Plan to User Story ===
            self.log_message(f"=== Linking {test_plan_key} to {user_story_key} ===")
            link_payload = {
                "type": {"name": "Relates"},
                "inwardIssue": {"key": test_plan_key},
                "outwardIssue": {"key": user_story_key}
            }
            url_link = f"{self.jira_url.get().rstrip('/')}/rest/api/2/issueLink"
            resp2 = requests.post(url_link, json=link_payload, auth=auth, headers=headers)
            resp2.raise_for_status()
            self.log_message(f"✅ Linked {test_plan_key} to {user_story_key}")

            # === Step 3: Read CSV and create Test Issues ===
            self.log_message("=== Creating Test issues under Test Plan ===")
            created_tests = []

            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for index, row in enumerate(reader):
                    summary = str(row.get("Test Name") or row.get("summary") or f"Test {index+1}")
                    description = str(row.get("HLTC Description & Pre-condition") or "")
                    preconditions = str(row.get("Preconditions") or "")
                    expected_result = str(row.get("Expected Result") or "")
                    labels = list(filter(None, str(row.get("labels") or "").split(",")))

                    test_payload = {
                        "fields": {
                            "project": {"key": project_key},
                            "summary": summary,
                            "description": description,
                            "issuetype": {"name": "Test"},
                            "customfield_11350": test_plan_key,
                            "customfield_XXXXX": preconditions,  # Replace with your Precondition field ID
                            "customfield_YYYYY": expected_result,  # Replace with your Expected Result field ID
                            "labels": labels
                        }
                    }

                    resp_test = requests.post(url_issue, json=test_payload, auth=auth, headers=headers)
                    resp_test.raise_for_status()
                    test_key = resp_test.json()["key"]
                    created_tests.append(test_key)
                    self.log_message(f"✅ Created Test: {test_key}")

            self.log_message(f"All test cases created: {', '.join(created_tests)}")
            messagebox.showinfo("Success", f"Uploaded {len(created_tests)} test cases under {test_plan_key}")

        except Exception as e:
            self.log_message(str(e))
            messagebox.showerror("Error", f"Failed to upload: {e}")

        finally:
            # Clean up temporary CSV if any
            if self.temp_csv and os.path.exists(self.temp_csv):
                os.remove(self.temp_csv)
                self.temp_csv = None


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = JiraXrayUploader(root)
        root.mainloop()
    except Exception:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise