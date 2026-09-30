
"""
Shramik Setu - Automated Daily-Wage Tracking System
Simple Tkinter GUI for workers, attendance, shifts and payments.
Run with: py app.py
"""
import csv
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from worker_manager import register_worker, find_worker, unregister_worker, skill_from_experience
from attendance_engine import log_shift, settle_shift_payment
from storage import WORKERS_FILE, SHIFTS_FILE, WORKER_HISTORY_FILE, load_data, save_data


class ShramikSetuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shramik Setu - Daily Wage Tracking")
        self.geometry("1250x800")
        self.minsize(1080, 700)
        self.configure(bg="#f4f6f8")

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("TButton", padding=(10, 6))
        self.style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), padding=(12, 7))

        self.build_ui()
        self.refresh_all()

    # ---------- General helpers ----------
    def parse_time(self, value):
        """Accept HH:MM or legacy decimal-hour input and return decimal hours."""
        text = str(value).strip()
        if ":" in text:
            try:
                hour, minute = text.split(":", 1)
                hour = int(hour)
                minute = int(minute)
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError
                return hour + minute / 60.0
            except ValueError:
                raise ValueError("Use time as HH:MM, for example 08:30 or 17:30.")
        try:
            number = float(text)
        except ValueError:
            raise ValueError("Use time as HH:MM, for example 08:30 or 17:30.")
        if number < 0 or number >= 24:
            raise ValueError("Time must be between 00:00 and 23:59.")
        return number

    def format_time(self, value):
        try:
            hours = float(value)
            total_minutes = round(hours * 60)
            h = (total_minutes // 60) % 24
            m = total_minutes % 60
            return f"{h:02d}:{m:02d}"
        except (TypeError, ValueError):
            return "—"

    def format_money(self, value):
        try:
            return f"₹{float(value):,.2f}"
        except (TypeError, ValueError):
            return "₹0.00"

    def get_shift_by_id(self, shift_id):
        shifts = load_data(SHIFTS_FILE)
        return next((s for s in shifts if s.get("shift_id") == shift_id), None)

    # ---------- UI ----------
    def build_ui(self):
        header = tk.Frame(self, bg="#1f4e5f", height=86)
        header.pack(fill="x")
        tk.Label(header, text="SHRAMIK SETU", font=("Segoe UI", 24, "bold"),
                 bg="#1f4e5f", fg="white").pack(anchor="w", padx=28, pady=(10, 0))
        tk.Label(header, text="Automated Daily-Wage Tracking System",
                 font=("Segoe UI", 11), bg="#1f4e5f", fg="#d9edf2").pack(anchor="w", padx=30, pady=(0, 10))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=16)

        self.dashboard_tab = ttk.Frame(self.notebook, padding=16)
        self.worker_tab = ttk.Frame(self.notebook, padding=16)
        self.attendance_tab = ttk.Frame(self.notebook, padding=16)
        self.shifts_tab = ttk.Frame(self.notebook, padding=16)
        self.records_tab = ttk.Frame(self.notebook, padding=16)
        self.workers_records_tab = ttk.Frame(self.notebook, padding=16)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.worker_tab, text="Workers")
        self.notebook.add(self.attendance_tab, text="Attendance")
        self.notebook.add(self.shifts_tab, text="Shifts")
        self.notebook.add(self.records_tab, text="Payments & Records")
        self.notebook.add(self.workers_records_tab, text="All Workers")

        self.build_dashboard()
        self.build_worker_form()
        self.build_attendance_form()
        self.build_shifts()
        self.build_records()
        self.build_worker_records()

    def metric_card(self, parent, title, variable, row, col):
        frame = ttk.LabelFrame(parent, text=title, padding=14)
        frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        ttk.Label(frame, textvariable=variable, font=("Segoe UI", 19, "bold")).pack()

    # ---------- Dashboard ----------
    def build_dashboard(self):
        for c in range(3):
            self.dashboard_tab.columnconfigure(c, weight=1)

        self.worker_count = tk.StringVar(value="0")
        self.shift_count = tk.StringVar(value="0")
        self.total_hours = tk.StringVar(value="0")
        self.total_wages = tk.StringVar(value="₹0")
        self.unpaid_wages = tk.StringVar(value="₹0")
        self.overtime = tk.StringVar(value="0")
        self.skilled_count = tk.StringVar(value="0")
        self.semi_count = tk.StringVar(value="0")
        self.unskilled_count = tk.StringVar(value="0")

        self.metric_card(self.dashboard_tab, "Active Workers", self.worker_count, 0, 0)
        self.metric_card(self.dashboard_tab, "Total Shifts", self.shift_count, 0, 1)
        self.metric_card(self.dashboard_tab, "Total Hours", self.total_hours, 0, 2)
        self.metric_card(self.dashboard_tab, "Total Wages", self.total_wages, 1, 0)
        self.metric_card(self.dashboard_tab, "Unpaid Wages", self.unpaid_wages, 1, 1)
        self.metric_card(self.dashboard_tab, "Overtime Hours", self.overtime, 1, 2)

        skills = ttk.LabelFrame(self.dashboard_tab, text="Active Worker Skill Summary", padding=14)
        skills.grid(row=2, column=0, columnspan=3, padx=8, pady=10, sticky="ew")
        for c in range(3):
            skills.columnconfigure(c, weight=1)
        ttk.Label(skills, text="Skilled", font=("Segoe UI", 11, "bold")).grid(row=0, column=0)
        ttk.Label(skills, text="Semi-Skilled", font=("Segoe UI", 11, "bold")).grid(row=0, column=1)
        ttk.Label(skills, text="Unskilled", font=("Segoe UI", 11, "bold")).grid(row=0, column=2)
        ttk.Label(skills, textvariable=self.skilled_count, font=("Segoe UI", 18, "bold")).grid(row=1, column=0)
        ttk.Label(skills, textvariable=self.semi_count, font=("Segoe UI", 18, "bold")).grid(row=1, column=1)
        ttk.Label(skills, textvariable=self.unskilled_count, font=("Segoe UI", 18, "bold")).grid(row=1, column=2)

        actions = ttk.LabelFrame(self.dashboard_tab, text="Quick Actions", padding=14)
        actions.grid(row=3, column=0, columnspan=3, padx=8, pady=10, sticky="ew")
        ttk.Button(actions, text="Register Worker", command=lambda: self.notebook.select(self.worker_tab)).pack(side="left", padx=6)
        ttk.Button(actions, text="Record Attendance", command=lambda: self.notebook.select(self.attendance_tab)).pack(side="left", padx=6)
        ttk.Button(actions, text="View Shifts", command=lambda: self.notebook.select(self.shifts_tab)).pack(side="left", padx=6)
        ttk.Button(actions, text="View Payments", command=lambda: self.notebook.select(self.records_tab)).pack(side="left", padx=6)
        ttk.Button(actions, text="Refresh", command=self.refresh_all).pack(side="right", padx=6)

        summary = ttk.LabelFrame(self.dashboard_tab, text="System Summary", padding=14)
        summary.grid(row=4, column=0, columnspan=3, padx=8, pady=10, sticky="ew")
        self.summary_label = ttk.Label(summary, text="", wraplength=1100)
        self.summary_label.pack(anchor="w")

    # ---------- Workers ----------
    def build_worker_form(self):
        form = ttk.LabelFrame(self.worker_tab, text="Register New Worker", padding=18)
        form.pack(fill="x", pady=(0, 12))
        self.worker_name = tk.StringVar()
        self.worker_experience = tk.StringVar()
        self.worker_rate = tk.StringVar()
        self.skill_preview = tk.StringVar(value="Skill Level: —")

        fields = [
            ("Worker Name", self.worker_name),
            ("Work Experience (years)", self.worker_experience),
            ("Daily Wage (₹)", self.worker_rate),
        ]
        for r, (label, var) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=r, column=0, padx=10, pady=8, sticky="w")
            entry = ttk.Entry(form, textvariable=var, width=35)
            entry.grid(row=r, column=1, padx=10, pady=8, sticky="w")
            if label == "Work Experience (years)":
                entry.bind("<KeyRelease>", self.preview_skill)
        ttk.Label(form, textvariable=self.skill_preview, font=("Segoe UI", 10, "bold")).grid(row=3, column=0, columnspan=2, pady=4)
        ttk.Label(form, text="0–1 years: Unskilled | >1–3 years: Semi-Skilled | >3 years: Skilled").grid(row=4, column=0, columnspan=2, pady=4)
        ttk.Button(form, text="Register Worker", style="Accent.TButton", command=self.register_worker_ui).grid(row=5, column=0, columnspan=2, pady=10)
        form.columnconfigure(1, weight=1)

        manage = ttk.LabelFrame(self.worker_tab, text="Worker Management", padding=14)
        manage.pack(fill="x", pady=8)
        self.unregister_id = tk.StringVar()
        ttk.Label(manage, text="Worker ID:").pack(side="left", padx=(0, 8))
        ttk.Entry(manage, textvariable=self.unregister_id, width=18).pack(side="left")
        ttk.Button(manage, text="Unregister Worker", command=self.unregister_worker_ui).pack(side="left", padx=8)
        ttk.Label(manage, text="Past shifts remain in the Shifts and Payments records.").pack(side="left", padx=8)

        help_box = ttk.LabelFrame(self.worker_tab, text="Skill classification", padding=12)
        help_box.pack(fill="x", pady=8)
        ttk.Label(help_box, text="Enter relevant work experience. Skill level is calculated automatically; no manual skill selection is required.").pack(anchor="w")

    def preview_skill(self, event=None):
        try:
            self.skill_preview.set(f"Skill Level: {skill_from_experience(float(self.worker_experience.get()))}")
        except (ValueError, TypeError):
            self.skill_preview.set("Skill Level: —")

    def register_worker_ui(self):
        success, message = register_worker(self.worker_name.get(), self.worker_experience.get(), self.worker_rate.get())
        if success:
            messagebox.showinfo("Worker Registered", message)
            self.worker_name.set("")
            self.worker_experience.set("")
            self.worker_rate.set("")
            self.skill_preview.set("Skill Level: —")
            self.refresh_all()
        else:
            messagebox.showerror("Registration Error", message)

    def unregister_worker_ui(self):
        worker_id = self.unregister_id.get().strip()
        if not worker_id:
            messagebox.showwarning("Worker ID", "Enter a Worker ID first.")
            return
        worker = find_worker(worker_id)
        if worker is None:
            messagebox.showerror("Worker Not Found", "No active worker exists with that ID.")
            return
        if not messagebox.askyesno("Confirm Unregister", f"Unregister {worker['name']} ({worker['worker_id']})?\n\nThe worker remains in the historical register and past shifts are preserved."):
            return
        success, message = unregister_worker(worker_id)
        if success:
            self.unregister_id.set("")
            messagebox.showinfo("Worker Unregistered", message)
            self.refresh_all()
        else:
            messagebox.showerror("Unregister Error", message)

    # ---------- Attendance ----------
    def build_attendance_form(self):
        form = ttk.LabelFrame(self.attendance_tab, text="Record a Work Shift", padding=18)
        form.pack(fill="x", pady=(0, 12))

        self.att_worker = tk.StringVar()
        self.att_date = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        self.att_in = tk.StringVar(value="08:00")
        self.att_out = tk.StringVar(value="16:00")
        self.att_result = tk.StringVar(value="Enter the shift details and click Save Shift.")

        ttk.Label(form, text="Worker").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.att_worker_combo = ttk.Combobox(form, textvariable=self.att_worker, state="readonly", width=32)
        self.att_worker_combo.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        entries = [
            ("Date (DD-MM-YYYY)", self.att_date),
            ("Check-in time (HH:MM)", self.att_in),
            ("Check-out time (HH:MM)", self.att_out),
        ]
        for r, (label, var) in enumerate(entries, start=1):
            ttk.Label(form, text=label).grid(row=r, column=0, padx=10, pady=8, sticky="w")
            ttk.Entry(form, textvariable=var, width=35).grid(row=r, column=1, padx=10, pady=8, sticky="w")

        ttk.Button(form, text="Save Shift", style="Accent.TButton", command=self.log_attendance_ui).grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Label(form, text="Use 24-hour time, for example 08:30 and 17:30. Decimal input such as 8.5 is also accepted.").grid(row=5, column=0, columnspan=2, pady=2)

        result = ttk.LabelFrame(self.attendance_tab, text="Saved Shift Summary", padding=16)
        result.pack(fill="both", expand=True, pady=8)
        ttk.Label(result, textvariable=self.att_result, font=("Segoe UI", 11), justify="left", wraplength=1000).pack(anchor="w", fill="x")
        ttk.Button(result, text="Open Shifts", command=lambda: self.notebook.select(self.shifts_tab)).pack(anchor="w", pady=(18, 0))

    def refresh_worker_choices(self):
        workers = load_data(WORKERS_FILE)
        values = [f"{w['worker_id']} - {w['name']}" for w in workers]
        self.att_worker_combo["values"] = values
        if self.att_worker.get() not in values:
            self.att_worker.set(values[0] if values else "")

    def log_attendance_ui(self):
        selected = self.att_worker.get().strip()
        if not selected:
            messagebox.showwarning("Worker Required", "Select an active worker.")
            return
        worker_id = selected.split(" - ", 1)[0]
        try:
            check_in = self.parse_time(self.att_in.get())
            check_out = self.parse_time(self.att_out.get())
        except ValueError as exc:
            messagebox.showerror("Invalid Time", str(exc))
            return
        try:
            datetime.strptime(self.att_date.get().strip(), "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Invalid Date", "Use DD-MM-YYYY, for example 27-09-2026.")
            return
        success, message, shift = log_shift(worker_id, self.att_date.get().strip(), check_in, check_out)
        if not success:
            messagebox.showerror("Attendance Error", message)
            return

        # Store readable clock times in the shift record without breaking the existing calculation format.
        shifts = load_data(SHIFTS_FILE)
        for item in shifts:
            if item.get("shift_id") == shift.get("shift_id"):
                item["check_in_time"] = self.format_time(check_in)
                item["check_out_time"] = self.format_time(check_out)
                break
        save_data(SHIFTS_FILE, shifts)
        shift["check_in_time"] = self.format_time(check_in)
        shift["check_out_time"] = self.format_time(check_out)

        b = shift.get("breakdown", {})
        self.att_result.set(
            f"Shift saved successfully.\n\n"
            f"Shift ID: {shift.get('shift_id')}\n"
            f"Worker: {shift.get('name')} ({shift.get('worker_id')})\n"
            f"Date: {shift.get('date')}\n"
            f"Check-in: {self.format_time(check_in)}    Check-out: {self.format_time(check_out)}\n"
            f"Hours worked: {shift.get('hours_worked', 0):.2f}\n"
            f"Total wage: {self.format_money(b.get('total_wage', 0))}\n"
            f"Payment status: {shift.get('settlement_status', 'UNPAID')}"
        )
        self.refresh_all()
        messagebox.showinfo("Attendance Recorded", message)

    # ---------- Shifts ----------
    def build_shifts(self):
        toolbar = ttk.Frame(self.shifts_tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Refresh", command=self.refresh_shifts).pack(side="left")
        ttk.Button(toolbar, text="Export Shifts CSV", command=self.export_shifts).pack(side="left", padx=8)

        ttk.Label(toolbar, text="Search:").pack(side="left", padx=(20, 4))
        self.shift_search = tk.StringVar()
        search = ttk.Entry(toolbar, textvariable=self.shift_search, width=28)
        search.pack(side="left")
        search.bind("<KeyRelease>", lambda e: self.refresh_shifts())

        ttk.Label(self.shifts_tab, text="Complete shift register: worker, shift, check-in/check-out, hours, wage and payment status.").pack(anchor="w", pady=(0, 6))

        columns = ("worker_id", "worker_name", "shift_id", "date", "check_in", "check_out", "hours", "wage", "status")
        self.shift_tree = ttk.Treeview(self.shifts_tab, columns=columns, show="headings")
        headings = {
            "worker_id": "Worker ID", "worker_name": "Worker Name", "shift_id": "Shift ID", "date": "Date",
            "check_in": "Check In", "check_out": "Check Out", "hours": "Hours", "wage": "Wage (₹)", "status": "Status"
        }
        widths = {"worker_id":90, "worker_name":150, "shift_id":95, "date":105, "check_in":85, "check_out":85, "hours":70, "wage":100, "status":95}
        for col in columns:
            self.shift_tree.heading(col, text=headings[col])
            self.shift_tree.column(col, width=widths[col], anchor="center")
        self.shift_tree.pack(fill="both", expand=True)

    def refresh_shifts(self):
        if not hasattr(self, "shift_tree"):
            return
        for item in self.shift_tree.get_children():
            self.shift_tree.delete(item)
        search = self.shift_search.get().strip().lower() if hasattr(self, "shift_search") else ""
        for s in load_data(SHIFTS_FILE):
            check_in = s.get("check_in_time") or self.format_time(s.get("check_in"))
            check_out = s.get("check_out_time") or self.format_time(s.get("check_out"))
            wage = s.get("breakdown", {}).get("total_wage", 0)
            values = (
                s.get("worker_id", ""), s.get("name", ""), s.get("shift_id", ""), s.get("date", ""),
                check_in, check_out, f"{float(s.get('hours_worked', 0)):.2f}", f"{float(wage):.2f}",
                s.get("settlement_status", "UNPAID")
            )
            if search and search not in " ".join(str(v).lower() for v in values):
                continue
            self.shift_tree.insert("", "end", values=values)

    def export_shifts(self):
        shifts = load_data(SHIFTS_FILE)
        if not shifts:
            messagebox.showinfo("Export", "There are no shifts to export.")
            return
        path = filedialog.asksaveasfilename(title="Save Shift Register", defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="shift_register.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Worker ID", "Worker Name", "Shift ID", "Date", "Check In Time", "Check Out Time", "Hours Worked", "Total Wage", "Payment Status", "Paid On"])
            for s in shifts:
                writer.writerow([
                    s.get("worker_id", ""), s.get("name", ""), s.get("shift_id", ""), s.get("date", ""),
                    s.get("check_in_time") or self.format_time(s.get("check_in")),
                    s.get("check_out_time") or self.format_time(s.get("check_out")),
                    s.get("hours_worked", ""), s.get("breakdown", {}).get("total_wage", ""),
                    s.get("settlement_status", "UNPAID"), s.get("paid_on", "")
                ])
        messagebox.showinfo("Export Complete", f"Shift register saved to:\n{path}")

    # ---------- Payments & Records ----------
    def build_records(self):
        toolbar = ttk.Frame(self.records_tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Refresh", command=self.refresh_records).pack(side="left")
        ttk.Button(toolbar, text="✓ Mark Selected as PAID", style="Accent.TButton", command=self.mark_selected_paid).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Export Payment Records CSV", command=self.export_records).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Clear Attendance Log", command=self.clear_log_ui).pack(side="right")

        filters = ttk.Frame(self.records_tab)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Status:").pack(side="left")
        self.payment_status_filter = tk.StringVar(value="All")
        combo = ttk.Combobox(filters, textvariable=self.payment_status_filter, values=["All", "UNPAID", "PAID"], state="readonly", width=12)
        combo.pack(side="left", padx=6)
        combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_records())
        ttk.Label(filters, text="Search:").pack(side="left", padx=(18, 4))
        self.payment_search = tk.StringVar()
        entry = ttk.Entry(filters, textvariable=self.payment_search, width=30)
        entry.pack(side="left")
        entry.bind("<KeyRelease>", lambda e: self.refresh_records())

        columns = ("shift", "worker", "date", "wage", "status", "paid_on")
        self.tree = ttk.Treeview(self.records_tab, columns=columns, show="headings", height=16)
        headings = {"shift": "Shift ID", "worker": "Worker", "date": "Date", "wage": "Wage (₹)", "status": "Status", "paid_on": "Paid On"}
        widths = {"shift":100, "worker":220, "date":110, "wage":120, "status":110, "paid_on":170}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_payment_selected)

        details = ttk.LabelFrame(self.records_tab, text="Selected Payment", padding=12)
        details.pack(fill="x", pady=(8, 0))
        self.payment_details = tk.StringVar(value="Select a payment record to view its details.")
        ttk.Label(details, textvariable=self.payment_details, justify="left", wraplength=1100).pack(anchor="w")

    def get_selected_payment_shift(self):
        selected = self.tree.selection()
        if not selected:
            return None
        shift_id = self.tree.item(selected[0], "values")[0]
        return self.get_shift_by_id(shift_id)

    def on_payment_selected(self, event=None):
        shift = self.get_selected_payment_shift()
        if not shift:
            self.payment_details.set("Select a payment record to view its details.")
            return
        b = shift.get("breakdown", {})
        status = shift.get("settlement_status", "UNPAID")
        paid_on = shift.get("paid_on", "—") if status == "PAID" else "—"
        self.payment_details.set(
            f"Shift: {shift.get('shift_id')}    Worker: {shift.get('name')} ({shift.get('worker_id')})    "
            f"Date: {shift.get('date')}\n"
            f"Hours: {shift.get('hours_worked', 0):.2f}    Total Wage: {self.format_money(b.get('total_wage', 0))}    "
            f"Status: {status}    Paid On: {paid_on}"
        )

    def refresh_records(self):
        if not hasattr(self, "tree"):
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        status_filter = self.payment_status_filter.get() if hasattr(self, "payment_status_filter") else "All"
        search = self.payment_search.get().strip().lower() if hasattr(self, "payment_search") else ""
        for s in load_data(SHIFTS_FILE):
            status = s.get("settlement_status", "UNPAID")
            if status_filter != "All" and status != status_filter:
                continue
            paid_on = s.get("paid_on", "—") if status == "PAID" else "—"
            values = (s.get("shift_id", ""), f"{s.get('name', '')} ({s.get('worker_id', '')})", s.get("date", ""), f"{float(s.get('breakdown', {}).get('total_wage', 0)):.2f}", status, paid_on)
            if search and search not in " ".join(str(v).lower() for v in values):
                continue
            self.tree.insert("", "end", values=values)
        self.on_payment_selected()

    def mark_selected_paid(self):
        shift = self.get_selected_payment_shift()
        if not shift:
            messagebox.showwarning("Select Payment", "Select an UNPAID payment record first.")
            return
        if shift.get("settlement_status", "UNPAID") == "PAID":
            messagebox.showinfo("Already Paid", f"{shift.get('shift_id')} is already marked as PAID.")
            return
        amount = float(shift.get("breakdown", {}).get("total_wage", 0))
        confirm = messagebox.askyesno("Confirm Payment", f"Mark this wage as PAID?\n\nWorker: {shift.get('name')}\nShift: {shift.get('shift_id')}\nAmount: ₹{amount:.2f}")
        if not confirm:
            return
        success, message = settle_shift_payment(shift.get("shift_id", ""))
        if success:
            self.refresh_all()
            # Re-select the updated payment row after refresh.
            for item in self.tree.get_children():
                if self.tree.item(item, "values")[0] == shift.get("shift_id"):
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    break
            self.on_payment_selected()
            messagebox.showinfo("Payment Updated", f"{message}\n\nThe payment record now shows PAID with the payment date/time.")
        else:
            messagebox.showerror("Payment Error", message)

    def clear_log_ui(self):
        shifts = load_data(SHIFTS_FILE)
        if not shifts:
            messagebox.showinfo("Clear Log", "The attendance and payment log is already empty.")
            return
        confirm = messagebox.askyesno(
            "Clear Attendance Log",
            "Delete ALL attendance, shift, wage and payment records?\n\nRegistered workers will NOT be deleted.\nThis action cannot be undone."
        )
        if not confirm:
            return
        save_data(SHIFTS_FILE, [])
        self.refresh_all()
        self.payment_details.set("The attendance and payment log is empty.")
        self.att_result.set("Attendance log cleared. Registered workers are unchanged.")
        messagebox.showinfo("Log Cleared", "All attendance, shift and payment records have been cleared.")

    def export_records(self):
        shifts = load_data(SHIFTS_FILE)
        if not shifts:
            messagebox.showinfo("Export", "There are no payment records to export.")
            return
        path = filedialog.asksaveasfilename(title="Save Payment Records", defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="payment_records.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Shift ID", "Worker ID", "Worker Name", "Date", "Hours", "Total Wage", "Payment Status", "Paid On"])
            for s in shifts:
                writer.writerow([
                    s.get("shift_id", ""), s.get("worker_id", ""), s.get("name", ""), s.get("date", ""),
                    s.get("hours_worked", ""), s.get("breakdown", {}).get("total_wage", ""),
                    s.get("settlement_status", "UNPAID"), s.get("paid_on", "")
                ])
        messagebox.showinfo("Export Complete", f"Payment records saved to:\n{path}")

    # ---------- All Workers ----------
    def build_worker_records(self):
        toolbar = ttk.Frame(self.workers_records_tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Label(toolbar, text="Search:").pack(side="left")
        self.worker_search = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.worker_search, width=28)
        search_entry.pack(side="left", padx=6)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_worker_records())
        ttk.Label(toolbar, text="Skill:").pack(side="left", padx=(12, 4))
        self.skill_filter = tk.StringVar(value="All")
        skill_combo = ttk.Combobox(toolbar, textvariable=self.skill_filter, values=["All", "Skilled", "Semi-Skilled", "Unskilled"], state="readonly", width=14)
        skill_combo.pack(side="left")
        skill_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_worker_records())
        ttk.Label(toolbar, text="Status:").pack(side="left", padx=(12, 4))
        self.status_filter = tk.StringVar(value="All")
        status_combo = ttk.Combobox(toolbar, textvariable=self.status_filter, values=["All", "ACTIVE", "UNREGISTERED"], state="readonly", width=14)
        status_combo.pack(side="left")
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_worker_records())
        ttk.Button(toolbar, text="Export Worker Register CSV", command=self.export_workers).pack(side="right")

        columns = ("id", "name", "experience", "skill", "rate", "hours", "status")
        self.worker_tree = ttk.Treeview(self.workers_records_tab, columns=columns, show="headings")
        headings = {"id":"Worker ID", "name":"Name", "experience":"Experience (yrs)", "skill":"Skill Level", "rate":"Daily Wage (₹)", "hours":"Standard Hours", "status":"Status"}
        widths = {"id":100, "name":180, "experience":130, "skill":140, "rate":120, "hours":120, "status":130}
        for col in columns:
            self.worker_tree.heading(col, text=headings[col])
            self.worker_tree.column(col, width=widths[col], anchor="center")
        self.worker_tree.pack(fill="both", expand=True)
        self.worker_tree.bind("<Double-1>", self.show_worker_details)
        ttk.Label(self.workers_records_tab, text="Search or filter the complete worker register. Unregistered workers remain in history.").pack(anchor="w", pady=(8, 0))

    def refresh_worker_records(self):
        if not hasattr(self, "worker_tree"):
            return
        current_workers = load_data(WORKERS_FILE)
        history = load_data(WORKER_HISTORY_FILE)
        existing_ids = {w.get("worker_id") for w in history}
        changed = False
        for worker in current_workers:
            if worker.get("worker_id") not in existing_ids:
                history.append({**worker, "status": "ACTIVE", "registered_on": ""})
                changed = True
        if changed:
            save_data(WORKER_HISTORY_FILE, history)

        search = self.worker_search.get().strip().lower()
        skill = self.skill_filter.get()
        status = self.status_filter.get()
        for item in self.worker_tree.get_children():
            self.worker_tree.delete(item)
        for worker in history:
            values = (
                worker.get("worker_id", ""), worker.get("name", ""), worker.get("experience_years", ""),
                worker.get("skill_level", ""), f"{float(worker.get('daily_rate', 0)):.2f}",
                worker.get("standard_hours", 8.0), worker.get("status", "ACTIVE")
            )
            searchable = " ".join(str(v).lower() for v in values)
            if search and search not in searchable:
                continue
            if skill != "All" and worker.get("skill_level") != skill:
                continue
            if status != "All" and worker.get("status", "ACTIVE") != status:
                continue
            self.worker_tree.insert("", "end", values=values)

    def show_worker_details(self, event=None):
        selected = self.worker_tree.selection()
        if not selected:
            return
        values = self.worker_tree.item(selected[0], "values")
        messagebox.showinfo("Worker Details", f"Worker ID: {values[0]}\nName: {values[1]}\nExperience: {values[2]} years\nSkill: {values[3]}\nDaily Wage: ₹{values[4]}\nStandard Hours: {values[5]}\nStatus: {values[6]}")

    def export_workers(self):
        history = load_data(WORKER_HISTORY_FILE)
        if not history:
            messagebox.showinfo("Export", "There are no worker records to export.")
            return
        path = filedialog.asksaveasfilename(title="Save Worker Register", defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="worker_register.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Worker ID", "Name", "Experience (years)", "Skill Level", "Daily Wage", "Standard Hours", "Status", "Registered On"])
            for w in history:
                writer.writerow([w.get("worker_id", ""), w.get("name", ""), w.get("experience_years", ""), w.get("skill_level", ""), w.get("daily_rate", ""), w.get("standard_hours", ""), w.get("status", ""), w.get("registered_on", "")])
        messagebox.showinfo("Export Complete", f"Worker register saved to:\n{path}")

    # ---------- Dashboard refresh ----------
    def refresh_dashboard(self):
        workers = load_data(WORKERS_FILE)
        shifts = load_data(SHIFTS_FILE)
        history = load_data(WORKER_HISTORY_FILE)
        total_hours = sum(float(s.get("hours_worked", 0)) for s in shifts)
        overtime = sum(float(s.get("breakdown", {}).get("overtime_hours", 0)) for s in shifts)
        wages = sum(float(s.get("breakdown", {}).get("total_wage", 0)) for s in shifts)
        unpaid = sum(float(s.get("breakdown", {}).get("total_wage", 0)) for s in shifts if s.get("settlement_status", "UNPAID") == "UNPAID")
        self.worker_count.set(str(len(workers)))
        self.shift_count.set(str(len(shifts)))
        self.total_hours.set(f"{total_hours:.2f}")
        self.overtime.set(f"{overtime:.2f}")
        self.total_wages.set(self.format_money(wages))
        self.unpaid_wages.set(self.format_money(unpaid))
        self.skilled_count.set(str(sum(1 for w in workers if w.get("skill_level") == "Skilled")))
        self.semi_count.set(str(sum(1 for w in workers if w.get("skill_level") == "Semi-Skilled")))
        self.unskilled_count.set(str(sum(1 for w in workers if w.get("skill_level") == "Unskilled")))
        unregistered = sum(1 for w in history if w.get("status") == "UNREGISTERED")
        self.summary_label.config(text=f"Active workers: {len(workers)}   |   Historical workers: {len(history)}   |   Unregistered workers: {unregistered}   |   Shift records: {len(shifts)}")

    def refresh_all(self):
        self.refresh_worker_choices()
        self.refresh_dashboard()
        self.refresh_shifts()
        self.refresh_records()
        self.refresh_worker_re
cords()


if __name__ == "__main__":
    ShramikSetuApp().mainloop()