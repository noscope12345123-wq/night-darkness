from __future__ import annotations

"""Tkinter desktop dashboard for Student Progress Tracker Pro Ultra.

References:
- tkinter: https://docs.python.org/3/library/tkinter.html
- ttk widgets: https://docs.python.org/3/library/tkinter.ttk.html
- messagebox: https://docs.python.org/3/library/tkinter.messagebox.html
- canvas drawing: https://tkdocs.com/tutorial/canvas.html
"""

import tkinter as tk
from tkinter import messagebox, ttk

from corepkg import APP_NAME, StudentTracker, TrackerError, ValidationError


class TrackerApp:
    """Desktop UI with dark theme, metrics, forms, and chart visualisation."""

    def __init__(self) -> None:
        self.tracker = StudentTracker()
        self.root = tk.Tk()
        self.root.title(APP_NAME + " | Tkinter Edition")
        self.root.geometry("1420x900")
        self.root.configure(bg="#08111f")
        self.setup_styles()
        self.build_layout()
        self.refresh_all()

    def setup_styles(self) -> None:
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Card.TFrame", background="#0f1b30")
        self.style.configure("Panel.TLabelframe", background="#0f1b30", foreground="white")
        self.style.configure(
            "Panel.TLabelframe.Label",
            background="#0f1b30",
            foreground="#d9e7ff",
            font=("Segoe UI", 11, "bold"),
        )
        self.style.configure("Dark.TLabel", background="#0f1b30", foreground="#dce6ff", font=("Segoe UI", 10))
        self.style.configure("Metric.TLabel", background="#0f1b30", foreground="white", font=("Segoe UI", 18, "bold"))
        self.style.configure("Subtle.TLabel", background="#0f1b30", foreground="#93a7d1", font=("Segoe UI", 10))
        self.style.configure("Dark.TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("Treeview", background="#12213b", fieldbackground="#12213b", foreground="white", rowheight=28)
        self.style.map("Treeview", background=[("selected", "#3b82f6")])
        self.style.configure("Treeview.Heading", background="#162742", foreground="white", font=("Segoe UI", 10, "bold"))

    def build_layout(self) -> None:
        top = ttk.Frame(self.root, style="Card.TFrame", padding=16)
        top.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(top, text=APP_NAME, bg="#0f1b30", fg="white", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(
            top,
            text="Ultra dashboard with analytics, search, bubble sort, and Tkinter data visualisation.",
            bg="#0f1b30",
            fg="#8ea1cf",
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(4, 0))

        metrics_holder = ttk.Frame(self.root, style="Card.TFrame", padding=8)
        metrics_holder.pack(fill="x", padx=16)
        self.metric_frames = {}
        for key, title in [
            ("total_students", "Students"),
            ("overall_average", "Overall Avg"),
            ("pass_rate", "Pass Rate"),
            ("at_risk_count", "At Risk"),
            ("strongest_module", "Strongest Module"),
        ]:
            frame = ttk.Frame(metrics_holder, style="Card.TFrame", padding=12)
            frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)
            ttk.Label(frame, text=title, style="Subtle.TLabel").pack(anchor="w")
            value = ttk.Label(frame, text="—", style="Metric.TLabel")
            value.pack(anchor="w", pady=(6, 0))
            self.metric_frames[key] = value

        middle = ttk.Frame(self.root, style="Card.TFrame", padding=8)
        middle.pack(fill="both", expand=True, padx=16, pady=8)

        left = ttk.Frame(middle, style="Card.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = ttk.Frame(middle, style="Card.TFrame")
        right.pack(side="left", fill="y")

        table_card = ttk.LabelFrame(left, text="Students", style="Panel.TLabelframe", padding=10)
        table_card.pack(fill="both", expand=True)
        search_bar = ttk.Frame(table_card, style="Card.TFrame")
        search_bar.pack(fill="x", pady=(0, 8))
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="name")
        tk.Entry(search_bar, textvariable=self.search_var, bg="#12213b", fg="white", insertbackground="white", relief="flat").pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=6)
        ttk.Button(search_bar, text="Search", command=self.search_students, style="Dark.TButton").pack(side="left", padx=4)
        ttk.Button(search_bar, text="Refresh", command=self.refresh_all, style="Dark.TButton").pack(side="left", padx=4)
        ttk.Combobox(search_bar, textvariable=self.sort_var, values=["name", "id", "average", "attendance", "risk"], state="readonly", width=12).pack(side="right")

        columns = ("id", "name", "course", "attendance", "average", "risk", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        headings = {
            "id": "ID",
            "name": "Name",
            "course": "Course",
            "attendance": "Attendance",
            "average": "Average",
            "risk": "Risk",
            "status": "Status",
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=120 if col != "name" else 180, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_student_selected)

        chart_card = ttk.LabelFrame(left, text="Data Visualisation", style="Panel.TLabelframe", padding=10)
        chart_card.pack(fill="x", pady=(8, 0))
        self.chart_canvas = tk.Canvas(chart_card, height=260, bg="#091426", highlightthickness=0)
        self.chart_canvas.pack(fill="x")

        detail_card = ttk.LabelFrame(right, text="Student Analytics", style="Panel.TLabelframe", padding=10)
        detail_card.pack(fill="x", padx=8, pady=(0, 8))
        self.detail_text = tk.Text(detail_card, width=48, height=18, bg="#0a1528", fg="white", insertbackground="white", relief="flat", wrap="word")
        self.detail_text.pack(fill="both", expand=True)

        form_card = ttk.LabelFrame(right, text="Add Student", style="Panel.TLabelframe", padding=10)
        form_card.pack(fill="x", padx=8)
        self.student_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.course_var = tk.StringVar(value="IY499")
        self.attendance_var = tk.StringVar(value="100")
        self.notes_var = tk.StringVar()
        for label, var in [
            ("Student ID", self.student_id_var),
            ("Name", self.name_var),
            ("Email", self.email_var),
            ("Course", self.course_var),
            ("Attendance", self.attendance_var),
            ("Notes", self.notes_var),
        ]:
            ttk.Label(form_card, text=label, style="Dark.TLabel").pack(anchor="w", pady=(6, 0))
            tk.Entry(form_card, textvariable=var, bg="#12213b", fg="white", insertbackground="white", relief="flat").pack(fill="x", ipady=6)
        button_row = ttk.Frame(form_card, style="Card.TFrame")
        button_row.pack(fill="x", pady=(10, 0))
        ttk.Button(button_row, text="Add Student", command=self.add_student, style="Dark.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(button_row, text="Seed Demo", command=self.seed_demo, style="Dark.TButton").pack(side="left", padx=6)
        ttk.Button(button_row, text="Export CSV", command=self.export_csv, style="Dark.TButton").pack(side="left", padx=6)
        ttk.Button(button_row, text="Clear Form", command=self.clear_form, style="Dark.TButton").pack(side="left", padx=6)

    def refresh_metrics(self) -> None:
        stats = self.tracker.dashboard_metrics()
        self.metric_frames["total_students"].config(text=str(stats["total_students"]))
        self.metric_frames["overall_average"].config(text="N/A" if stats["overall_average"] is None else f"{stats['overall_average']}%")
        self.metric_frames["pass_rate"].config(text=f"{stats['pass_rate']}%")
        self.metric_frames["at_risk_count"].config(text=str(stats["at_risk_count"]))
        self.metric_frames["strongest_module"].config(text=str(stats["strongest_module"]))

    def refresh_tree(self, students=None) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        students = self.tracker.sort_students(self.sort_var.get()) if students is None else students
        for student in students:
            average = self.tracker.calculate_student_average(student)
            self.tree.insert(
                "",
                "end",
                values=(
                    student.student_id,
                    student.name,
                    student.course,
                    f"{student.attendance:.1f}%",
                    "N/A" if average is None else f"{average:.2f}%",
                    self.tracker.calculate_risk_score(student),
                    self.tracker.get_progress_status(student),
                ),
            )
        self.draw_chart(students)
        self.refresh_metrics()

    def draw_chart(self, students=None) -> None:
        self.chart_canvas.delete("all")
        students = self.tracker.sort_students("average") if students is None else students
        students = students[:8]
        width = max(self.chart_canvas.winfo_width(), 900)
        self.chart_canvas.config(scrollregion=(0, 0, width, 240))
        self.chart_canvas.create_text(20, 18, anchor="w", fill="#dce6ff", font=("Segoe UI", 12, "bold"), text="Top student averages")
        if not students:
            self.chart_canvas.create_text(20, 70, anchor="w", fill="white", text="No data yet.")
            return
        for value in (0, 25, 50, 75, 100):
            y = 205 - (140 * (value / 100))
            self.chart_canvas.create_line(50, y, width - 30, y, fill="#1d3358")
            self.chart_canvas.create_text(28, y, fill="#8ea1cf", text=str(value))
        bar_width = 80
        gap = 28
        x = 70
        colours = {
            "Excellent": "#10b981",
            "Stable": "#3b82f6",
            "Needs support": "#f59e0b",
            "Critical risk": "#ef4444",
            "Insufficient data": "#64748b",
        }
        for student in students:
            average = self.tracker.calculate_student_average(student) or 0
            status = self.tracker.get_progress_status(student)
            bar_height = 140 * (average / 100)
            y1 = 205 - bar_height
            self.chart_canvas.create_rectangle(x, y1, x + bar_width, 205, fill=colours.get(status, "#3b82f6"), outline="")
            self.chart_canvas.create_text(x + bar_width / 2, y1 - 10, fill="white", text=f"{average:.1f}%")
            self.chart_canvas.create_text(x + bar_width / 2, 220, fill="#dce6ff", text=student.name[:10])
            x += bar_width + gap

    def refresh_all(self) -> None:
        self.refresh_tree()
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("end", "Select a student to view advanced analytics.\n")

    def search_students(self) -> None:
        keyword = self.search_var.get().strip()
        results = self.tracker.search_students(keyword)
        self.refresh_tree(results)

    def on_student_selected(self, event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        student = self.tracker.get_student(values[0])
        info = self.tracker.summary_for_student(student)
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("end", f"ID: {student.student_id}\n")
        self.detail_text.insert("end", f"Name: {student.name}\n")
        self.detail_text.insert("end", f"Email: {student.email}\n")
        self.detail_text.insert("end", f"Course: {student.course}\n")
        self.detail_text.insert("end", f"Attendance: {student.attendance}%\n")
        self.detail_text.insert("end", f"Average: {info['average']}\n")
        self.detail_text.insert("end", f"Grade band: {info['grade_band']}\n")
        self.detail_text.insert("end", f"Status: {info['status']}\n")
        self.detail_text.insert("end", f"Trend: {info['trend']}\n")
        self.detail_text.insert("end", f"Risk score: {info['risk']}\n\n")
        self.detail_text.insert("end", f"Recommendation:\n{info['recommendation']}\n\n")
        self.detail_text.insert("end", "Modules:\n")
        for module in student.modules.values():
            module_avg = self.tracker.calculate_module_average(module)
            self.detail_text.insert("end", f"- {module.module_name} ({module.lecturer}) | Avg: {module_avg}\n")
            for assessment in module.assessments:
                self.detail_text.insert("end", f"    • {assessment.name}: {assessment.score}% weighted {assessment.weight}%\n")

    def add_student(self) -> None:
        try:
            self.tracker.add_student(
                self.student_id_var.get(),
                self.name_var.get(),
                self.email_var.get(),
                self.course_var.get(),
                float(self.attendance_var.get() or "100"),
                self.notes_var.get(),
            )
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_form()
            self.refresh_all()
        except (ValidationError, TrackerError, ValueError) as exc:
            messagebox.showerror("Error", str(exc))

    def clear_form(self) -> None:
        self.student_id_var.set("")
        self.name_var.set("")
        self.email_var.set("")
        self.course_var.set("IY499")
        self.attendance_var.set("100")
        self.notes_var.set("")

    def seed_demo(self) -> None:
        try:
            self.tracker.seed_demo_data()
            messagebox.showinfo("Success", "Demo data inserted.")
            self.refresh_all()
        except TrackerError as exc:
            messagebox.showwarning("Notice", str(exc))

    def export_csv(self) -> None:
        path = self.tracker.export_csv()
        messagebox.showinfo("Export", f"CSV exported to {path}")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    TrackerApp().run()
