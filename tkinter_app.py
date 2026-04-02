from __future__ import annotations

'''
Tkinter desktop version of Student Progress Tracker Pro.

References used in this file:
- Tkinter docs: https://docs.python.org/3/library/tkinter.html
- ttk docs: https://docs.python.org/3/library/tkinter.ttk.html
- messagebox docs: https://docs.python.org/3/library/tkinter.messagebox.html
- StringVar docs through Tkinter reference: https://docs.python.org/3/library/tkinter.html
- Canvas drawing reference: https://docs.python.org/3/library/tkinter.html

Notes for marking:
- Tkinter is used for the GUI and the required data visualisation.
- Widgets and layout use official Tkinter/ttk APIs.
- Tracker-specific layout and chart design are original project work.
'''

# Tkinter is the standard Python GUI toolkit.
# Reference: https://docs.python.org/3/library/tkinter.html
import tkinter as tk

# ttk and messagebox are imported from Tkinter modules.
# References:
# - ttk: https://docs.python.org/3/library/tkinter.ttk.html
# - messagebox: https://docs.python.org/3/library/tkinter.messagebox.html
from tkinter import messagebox, ttk

from core import APP_NAME, StudentTracker, TrackerError, ValidationError


class TrackerGUI:
    '''Desktop interface built with Tkinter and ttk widgets.''' 

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_NAME + " - Tkinter")
        self.root.geometry("1360x820")
        self.root.configure(bg="#0b1020")
        self.root.minsize(1180, 720)

        self.tracker = StudentTracker()

        self._setup_style()
        self._build_header()
        self._build_metrics()
        self._build_form()
        self._build_table()
        self._build_chart()
        self._refresh_everything()

    def _setup_style(self) -> None:
        '''Configure custom ttk styling for the dark theme.'''
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background="#0b1020")
        style.configure("Card.TFrame", background="#131a2f")
        style.configure("Dark.TLabel", background="#0b1020", foreground="#e5ecff", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#0b1020", foreground="#76a9ff", font=("Segoe UI", 24, "bold"))
        style.configure("SubTitle.TLabel", background="#0b1020", foreground="#9fb6ef", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="#131a2f", foreground="#76a9ff", font=("Segoe UI", 13, "bold"))
        style.configure("MetricValue.TLabel", background="#131a2f", foreground="#ffffff", font=("Segoe UI", 18, "bold"))
        style.configure("MetricLabel.TLabel", background="#131a2f", foreground="#98a8d1", font=("Segoe UI", 10))
        style.configure("Accent.TButton", background="#2b5cff", foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Dark.Treeview", background="#131a2f", fieldbackground="#131a2f", foreground="#f5f7ff", rowheight=30)
        style.configure("Dark.Treeview.Heading", background="#243359", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.map("Dark.Treeview", background=[("selected", "#2b5cff")])

    def _build_header(self) -> None:
        '''Build the title area shown at the top of the window.'''
        header = ttk.Frame(self.root, style="Dark.TFrame")
        header.pack(fill="x", padx=18, pady=(16, 8))
        ttk.Label(header, text=APP_NAME + " Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Three-interface coursework app with file handling, search, bubble sort, analytics, and Tkinter data visualisation.",
            style="SubTitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

    def _build_metrics(self) -> None:
        '''Build dashboard metric cards above the form.'''
        self.metrics_frame = ttk.Frame(self.root, style="Dark.TFrame")
        self.metrics_frame.pack(fill="x", padx=18, pady=(0, 8))
        self.metric_labels: dict[str, ttk.Label] = {}

        metric_names = [
            ("total_students", "Total Students"),
            ("average_grade", "Average Grade"),
            ("average_attendance", "Average Attendance"),
            ("at_risk_count", "At Risk"),
            ("pass_rate", "Pass Rate"),
        ]

        for index, (key, title) in enumerate(metric_names):
            card = ttk.Frame(self.metrics_frame, style="Card.TFrame")
            card.grid(row=0, column=index, sticky="nsew", padx=6)
            self.metrics_frame.columnconfigure(index, weight=1)
            ttk.Label(card, text=title, style="MetricLabel.TLabel").pack(anchor="w", padx=14, pady=(12, 2))
            value_label = ttk.Label(card, text="-", style="MetricValue.TLabel")
            value_label.pack(anchor="w", padx=14, pady=(0, 12))
            self.metric_labels[key] = value_label

    def _build_form(self) -> None:
        '''Build the entry form and action buttons.'''
        outer = ttk.Frame(self.root, style="Dark.TFrame")
        outer.pack(fill="x", padx=18, pady=8)

        form = ttk.Frame(outer, style="Card.TFrame")
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        self.student_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.course_var = tk.StringVar(value="IY499")
        self.attendance_var = tk.StringVar(value="100")
        self.notes_var = tk.StringVar()
        self.module_var = tk.StringVar()
        self.lecturer_var = tk.StringVar()
        self.assessment_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.feedback_var = tk.StringVar()
        self.search_var = tk.StringVar()

        padx = 10
        pady = 8
        labels = [
            ("Student ID", self.student_id_var, 0, 0),
            ("Name", self.name_var, 0, 2),
            ("Email", self.email_var, 1, 0),
            ("Course", self.course_var, 1, 2),
            ("Attendance", self.attendance_var, 2, 0),
            ("Notes", self.notes_var, 2, 2),
            ("Module", self.module_var, 3, 0),
            ("Lecturer", self.lecturer_var, 3, 2),
            ("Assessment", self.assessment_var, 4, 0),
            ("Score", self.score_var, 4, 2),
            ("Weight", self.weight_var, 5, 0),
            ("Feedback", self.feedback_var, 5, 2),
        ]

        for text, variable, row, col in labels:
            ttk.Label(form, text=text, style="Dark.TLabel").grid(row=row, column=col, sticky="w", padx=padx, pady=(pady, 0))
            ttk.Entry(form, textvariable=variable).grid(row=row, column=col + 1, sticky="ew", padx=padx, pady=(0, pady))

        button_row = ttk.Frame(form, style="Card.TFrame")
        button_row.grid(row=6, column=0, columnspan=4, sticky="ew", padx=10, pady=8)

        ttk.Button(button_row, text="Add Student", style="Accent.TButton", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(button_row, text="Update Student", style="Accent.TButton", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(button_row, text="Add Module", style="Accent.TButton", command=self.add_module).pack(side="left", padx=4)
        ttk.Button(button_row, text="Add Assessment", style="Accent.TButton", command=self.add_assessment).pack(side="left", padx=4)
        ttk.Button(button_row, text="Export CSV", style="Accent.TButton", command=self.export_csv).pack(side="left", padx=4)
        ttk.Button(button_row, text="Seed Demo", style="Accent.TButton", command=self.seed_demo).pack(side="left", padx=4)
        ttk.Button(button_row, text="Clear Form", style="Accent.TButton", command=self.clear_form).pack(side="left", padx=4)

        search_row = ttk.Frame(form, style="Card.TFrame")
        search_row.grid(row=7, column=0, columnspan=4, sticky="ew", padx=10, pady=(0, 12))
        ttk.Label(search_row, text="Search", style="Dark.TLabel").pack(side="left", padx=(0, 8))
        ttk.Entry(search_row, textvariable=self.search_var, width=30).pack(side="left")
        ttk.Button(search_row, text="Run Search", style="Accent.TButton", command=self.run_search).pack(side="left", padx=6)
        ttk.Button(search_row, text="Sort by Name", style="Accent.TButton", command=lambda: self.refresh_table("name")).pack(side="left", padx=4)
        ttk.Button(search_row, text="Sort by ID", style="Accent.TButton", command=lambda: self.refresh_table("id")).pack(side="left", padx=4)
        ttk.Button(search_row, text="Sort by Attendance", style="Accent.TButton", command=lambda: self.refresh_table("attendance")).pack(side="left", padx=4)
        ttk.Button(search_row, text="Sort by Average", style="Accent.TButton", command=lambda: self.refresh_table("average")).pack(side="left", padx=4)

    def _build_table(self) -> None:
        '''Build the Treeview table used to show student records.'''
        wrapper = ttk.Frame(self.root, style="Dark.TFrame")
        wrapper.pack(fill="both", expand=True, padx=18, pady=8)

        left = ttk.Frame(wrapper, style="Card.TFrame")
        left.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Student Records", style="CardTitle.TLabel").pack(anchor="w", padx=12, pady=(10, 6))

        columns = ("id", "name", "course", "attendance", "average", "status")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", style="Dark.Treeview")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("course", text="Course")
        self.tree.heading("attendance", text="Attendance")
        self.tree.heading("average", text="Average")
        self.tree.heading("status", text="Status")
        self.tree.column("id", width=110)
        self.tree.column("name", width=170)
        self.tree.column("course", width=110)
        self.tree.column("attendance", width=110)
        self.tree.column("average", width=110)
        self.tree.column("status", width=160)
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_chart(self) -> None:
        '''Build the chart area used for Tkinter data visualisation.'''
        right = ttk.Frame(self.root, style="Card.TFrame")
        right.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Label(right, text="Average Score Visualisation", style="CardTitle.TLabel").pack(anchor="w", padx=12, pady=(10, 6))
        self.chart_canvas = tk.Canvas(right, height=280, bg="#11182c", highlightthickness=0)
        self.chart_canvas.pack(fill="x", padx=12, pady=(0, 12))

    def _refresh_everything(self) -> None:
        '''Refresh table, metrics, and chart together.'''
        self.refresh_metrics()
        self.refresh_table("name")
        self.draw_chart()

    def refresh_metrics(self) -> None:
        '''Update the dashboard metric cards from tracker analytics.'''
        stats = self.tracker.dashboard_metrics()
        self.metric_labels["total_students"].config(text=str(stats["total_students"]))
        self.metric_labels["average_grade"].config(text="-" if stats["average_grade"] is None else f"{stats['average_grade']:.2f}%")
        self.metric_labels["average_attendance"].config(text="-" if stats["average_attendance"] is None else f"{stats['average_attendance']:.2f}%")
        self.metric_labels["at_risk_count"].config(text=str(stats["at_risk_count"]))
        self.metric_labels["pass_rate"].config(text=f"{stats['pass_rate']:.2f}%")

    def refresh_table(self, sort_by: str = "name", students=None) -> None:
        '''Fill the table with sorted or searched records.'''
        for item in self.tree.get_children():
            self.tree.delete(item)

        items = self.tracker.sort_students(sort_by) if students is None else students
        for student in items:
            average = self.tracker.calculate_student_average(student)
            average_text = "-" if average is None else f"{average:.2f}"
            self.tree.insert("", "end", iid=student.student_id, values=(
                student.student_id,
                student.name,
                student.course,
                f"{student.attendance:.1f}%",
                average_text,
                self.tracker.get_progress_status(student),
            ))
        self.draw_chart(items)
        self.refresh_metrics()

    def draw_chart(self, students=None) -> None:
        '''Draw a bar chart using Tkinter Canvas rectangles and text.'''
        self.chart_canvas.delete("all")
        students = self.tracker.sort_students("average") if students is None else students
        students = students[:8]

        width = max(self.chart_canvas.winfo_width(), 980)
        height = 280
        self.chart_canvas.config(scrollregion=(0, 0, width, height))
        self.chart_canvas.create_text(20, 20, anchor="w", fill="#dce6ff", font=("Segoe UI", 12, "bold"), text="Top 8 student averages")

        if not students:
            self.chart_canvas.create_text(20, 70, anchor="w", fill="#ffffff", font=("Segoe UI", 12), text="No data available yet.")
            return

        # Horizontal guide lines help make the chart easier to read.
        for value in (0, 25, 50, 75, 100):
            y = 225 - (150 * (value / 100))
            self.chart_canvas.create_line(50, y, width - 30, y, fill="#23314f")
            self.chart_canvas.create_text(26, y, fill="#8ea1cf", text=str(value))

        bar_width = 85
        gap = 25
        start_x = 70
        base_y = 225
        max_height = 150

        for index, student in enumerate(students):
            average = self.tracker.calculate_student_average(student)
            if average is None:
                average = 0
            bar_height = max_height * (average / 100)
            x1 = start_x + index * (bar_width + gap)
            y1 = base_y - bar_height
            x2 = x1 + bar_width
            y2 = base_y

            colour = "#3e6cff"
            if average < 40:
                colour = "#cf3d5e"
            elif average < 60:
                colour = "#c28d2c"
            elif average >= 70:
                colour = "#24a36b"

            self.chart_canvas.create_rectangle(x1, y1, x2, y2, fill=colour, outline="#7fa4ff")
            self.chart_canvas.create_text((x1 + x2) / 2, y1 - 12, fill="#ffffff", text=f"{average:.1f}")
            self.chart_canvas.create_text((x1 + x2) / 2, base_y + 16, fill="#dce6ff", text=student.name[:10])

        self.chart_canvas.create_line(45, base_y, width - 30, base_y, fill="#ffffff")

    def run_search(self) -> None:
        '''Search students and update the table/chart.'''
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_table("name")
            return
        results = self.tracker.search_students(keyword)
        self.refresh_table(students=results)

    def on_select(self, _event=None) -> None:
        '''Load the selected record into the form fields for editing.'''
        selected = self.tree.selection()
        if not selected:
            return
        student = self.tracker.get_student(selected[0])
        self.student_id_var.set(student.student_id)
        self.name_var.set(student.name)
        self.email_var.set(student.email)
        self.course_var.set(student.course)
        self.attendance_var.set(str(student.attendance))
        self.notes_var.set(student.notes)

    def clear_form(self) -> None:
        '''Reset the form fields to empty/default values.'''
        self.student_id_var.set("")
        self.name_var.set("")
        self.email_var.set("")
        self.course_var.set("IY499")
        self.attendance_var.set("100")
        self.notes_var.set("")
        self.module_var.set("")
        self.lecturer_var.set("")
        self.assessment_var.set("")
        self.score_var.set("")
        self.weight_var.set("")
        self.feedback_var.set("")
        self.search_var.set("")

    def alert(self, title: str, message: str, is_error: bool = False) -> None:
        '''Show either an information or error message box.'''
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)

    def add_student(self) -> None:
        '''Button callback for adding a student.'''
        try:
            self.tracker.add_student(
                self.student_id_var.get(),
                self.name_var.get(),
                self.email_var.get(),
                self.course_var.get(),
                float(self.attendance_var.get() or 100),
                self.notes_var.get(),
            )
            self._refresh_everything()
            self.alert("Success", "Student added successfully.")
        except (ValidationError, TrackerError, ValueError) as exc:
            self.alert("Error", str(exc), True)

    def update_student(self) -> None:
        '''Button callback for updating a student.'''
        try:
            self.tracker.update_student(
                self.student_id_var.get(),
                self.name_var.get(),
                self.email_var.get(),
                self.course_var.get(),
                float(self.attendance_var.get() or 100),
                self.notes_var.get(),
            )
            self._refresh_everything()
            self.alert("Success", "Student updated successfully.")
        except (ValidationError, TrackerError, ValueError) as exc:
            self.alert("Error", str(exc), True)

    def add_module(self) -> None:
        '''Button callback for adding a module.'''
        try:
            self.tracker.add_module(self.student_id_var.get(), self.module_var.get(), self.lecturer_var.get())
            self._refresh_everything()
            self.alert("Success", "Module added successfully.")
        except (ValidationError, TrackerError) as exc:
            self.alert("Error", str(exc), True)

    def add_assessment(self) -> None:
        '''Button callback for adding an assessment.'''
        try:
            self.tracker.add_assessment(
                self.student_id_var.get(),
                self.module_var.get(),
                self.assessment_var.get(),
                float(self.score_var.get()),
                float(self.weight_var.get()),
                self.feedback_var.get(),
            )
            self._refresh_everything()
            self.alert("Success", "Assessment added successfully.")
        except (ValidationError, TrackerError, ValueError) as exc:
            self.alert("Error", str(exc), True)

    def export_csv(self) -> None:
        '''Button callback for exporting the report as CSV.'''
        path = self.tracker.export_csv()
        self.alert("Export Complete", f"CSV report saved to: {path}")

    def seed_demo(self) -> None:
        '''Button callback for inserting demo data.'''
        try:
            self.tracker.seed_demo_data()
            self._refresh_everything()
            self.alert("Success", "Demo data inserted.")
        except TrackerError as exc:
            self.alert("Error", str(exc), True)


if __name__ == "__main__":
    # Tk() creates the main application window.
    # Reference: https://docs.python.org/3/library/tkinter.html
    root = tk.Tk()
    app = TrackerGUI(root)
    root.mainloop()
