"""Shramik Setu - Automated Daily-Wage Tracking System.

Run from this folder with: python app.py
Uses Python's standard library and Tkinter.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.worker_manager import register_worker, unregister_worker, active_workers
from src.attendance_engine import record_shift, settle_payment
from src.storage import load_workers, load_shifts, save_workers, save_shifts


class ShramikSetuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shramik Setu - Daily-Wage Tracking")
        self.geometry("1050x680")
        self.minsize(850, 560)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        ttk.Label(self, text="SHRAMIK SETU", font=("Arial", 20, "bold")).pack(pady=(12, 0))
        ttk.Label(self, text="Automated Daily-Wage Tracking System").pack(pady=(0, 12))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)

        self.workers_tab = ttk.Frame(self.tabs, padding=12)
        self.attendance_tab = ttk.Frame(self.tabs, padding=12)
        self.records_tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.workers_tab, text="Workers")
        self.tabs.add(self.attendance_tab, text="Attendance")
        self.tabs.add(self.records_tab, text="Shifts & Payments")
        self.build_workers()
        self.build_attendance()
        self.build_records()

    def build_workers(self):
        form = ttk.LabelFrame(self.workers_tab, text="Register worker", padding=10)
        form.pack(fill="x")
        self.name = tk.StringVar()
        self.experience = tk.StringVar()
        self.rate = tk.StringVar()
        for row, (label, variable) in enumerate([
            ("Name", self.name), ("Experience (years)", self.experience),
            ("Daily wage (₹)", self.rate)
        ]):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(form, textvariable=variable, width=30).grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(form, text="Register", command=self.add_worker).grid(row=3, column=0, columnspan=2, pady=8)

        manage = ttk.LabelFrame(self.workers_tab, text="Unregister worker", padding=10)
        manage.pack(fill="x", pady=10)
        self.remove_id = tk.StringVar()
        ttk.Label(manage, text="Worker ID").pack(side="left")
        ttk.Entry(manage, textvariable=self.remove_id, width=18).pack(side="left", padx=8)
        ttk.Button(manage, text="Unregister", command=self.remove_worker).pack(side="left")
        self.worker_tree = ttk.Treeview(self.workers_tab, columns=("id", "name", "experience", "skill", "rate"),
                                        show="headings", height=12)
        for col, label, width in [
            ("id", "Worker ID", 100), ("name", "Name", 200),
            ("experience", "Experience", 120), ("skill", "Skill", 150), ("rate", "Daily wage (₹)", 130)
        ]:
            self.worker_tree.heading(col, text=label)
            self.worker_tree.column(col, width=width, anchor="center")
        self.worker_tree.pack(fill="both", expand=True, pady=10)

    def build_attendance(self):
        form = ttk.LabelFrame(self.attendance_tab, text="Record a shift", padding=12)
        form.pack(anchor="nw", fill="x")
        self.worker_choice = tk.StringVar()
        self.shift_date = tk.StringVar()
        self.check_in = tk.StringVar(value="08:00")
        self.check_out = tk.StringVar(value="16:00")
        fields = [
            ("Worker", None), ("Date (DD-MM-YYYY)", self.shift_date),
            ("Check-in (HH:MM)", self.check_in), ("Check-out (HH:MM)", self.check_out)
        ]
        for row, (label, variable) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=6)
            if variable is None:
                self.worker_combo = ttk.Combobox(form, textvariable=self.worker_choice, state="readonly", width=28)
                self.worker_combo.grid(row=row, column=1, padx=5, pady=6, sticky="w")
            else:
                ttk.Entry(form, textvariable=variable, width=31).grid(row=row, column=1, padx=5, pady=6, sticky="w")
        ttk.Button(form, text="Save shift", command=self.add_shift).grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Label(form, text="Use 24-hour time. Overnight shifts are not supported in this beginner version.").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=4)

    def build_records(self):
        toolbar = ttk.Frame(self.records_tab)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Mark selected as PAID", command=self.pay_selected).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Export CSV", command=self.export_csv).pack(side="left", padx=4)
        self.shift_tree = ttk.Treeview(self.records_tab,
            columns=("shift", "worker", "date", "hours", "wage", "status"),
            show="headings", height=18)
        for col, label, width in [
            ("shift", "Shift ID", 100), ("worker", "Worker", 190), ("date", "Date", 120),
            ("hours", "Hours", 100), ("wage", "Wage (₹)", 120), ("status", "Status", 120)
        ]:
            self.shift_tree.heading(col, text=label)
            self.shift_tree.column(col, width=width, anchor="center")
        self.shift_tree.pack(fill="both", expand=True, pady=10)

    def add_worker(self):
        ok, message = register_worker(self.name.get(), self.experience.get(), self.rate.get())
        if ok:
            self.name.set(""); self.experience.set(""); self.rate.set("")
            self.refresh()
            messagebox.showinfo("Worker registered", message)
        else:
            messagebox.showerror("Registration error", message)

    def remove_worker(self):
        ok, message = unregister_worker(self.remove_id.get())
        if ok:
            self.remove_id.set("")
            self.refresh()
            messagebox.showinfo("Worker updated", message)
        else:
            messagebox.showerror("Unregister error", message)

    def add_shift(self):
        selected = self.worker_choice.get()
        if not selected:
            messagebox.showwarning("Worker required", "Register and select a worker first.")
            return
        worker_id = selected.split(" - ", 1)[0]
        ok, message, shift = record_shift(worker_id, self.shift_date.get(),
                                         self.check_in.get(), self.check_out.get())
        if ok:
            self.refresh()
            messagebox.showinfo("Shift saved", message)
        else:
            messagebox.showerror("Attendance error", message)

    def pay_selected(self):
        selected = self.shift_tree.selection()
        if not selected:
            messagebox.showwarning("Select shift", "Select a shift first.")
            return
        shift_id = self.shift_tree.item(selected[0], "values")[0]
        if not messagebox.askyesno("Confirm payment", "Mark this shift as paid?"):
            return
        ok, message = settle_payment(shift_id)
        if ok:
            self.refresh()
            messagebox.showinfo("Payment updated", message)
        else:
            messagebox.showerror("Payment error", message)

    def export_csv(self):
        import csv
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        shifts = load_shifts()
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "shift_id", "worker_id", "worker_name", "date", "check_in", "check_out",
                "hours", "wage", "status", "paid_on"
            ])
            writer.writeheader()
            writer.writerows(shifts)
        messagebox.showinfo("Export complete", "CSV file exported.")

    def refresh(self):
        workers = active_workers()
        self.worker_combo["values"] = [f"{w['worker_id']} - {w['name']}" for w in workers]
        if self.worker_choice.get() not in self.worker_combo["values"]:
            self.worker_choice.set(self.worker_combo["values"][0] if workers else "")
        for item in self.worker_tree.get_children():
            self.worker_tree.delete(item)
        for w in workers:
            self.worker_tree.insert("", "end", values=(
                w["worker_id"], w["name"], w["experience"], w["skill"], f'{w["daily_rate"]:.2f}'
            ))
        for item in self.shift_tree.get_children():
            self.shift_tree.delete(item)
        for s in load_shifts():
            self.shift_tree.insert("", "end", values=(
                s["shift_id"], f'{s["worker_name"]} ({s["worker_id"]})', s["date"],
                f'{s["hours"]:.2f}', f'{s["wage"]:.2f}', s["status"]
            ))


if __name__ == "__main__":
    ShramikSetuApp().mainloop()
