from __future__ import annotations

'''
Tkinter desktop version of Student Progress Tracker Pro.

References used in this file:
- Tkinter documentation: https://docs.python.org/3/library/tkinter.html
- ttk documentation: https://docs.python.org/3/library/tkinter.ttk.html
- messagebox documentation: https://docs.python.org/3/library/tkinter.messagebox.html
- Canvas overview in Tkinter docs: https://docs.python.org/3/library/tkinter.html

The chart is drawn with Tkinter Canvas so the project includes data
visualisation using Tkinter, as required by the brief.
'''

import tkinter as tk  # Reference: https://docs.python.org/3/library/tkinter.html
from tkinter import messagebox, ttk  # Reference: https://docs.python.org/3/library/tkinter.ttk.html

from core import APP_NAME, StudentTracker, TrackerError, ValidationError


class TrackerGUI:
    '''Main desktop interface built with Tkinter widgets.'''

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_NAME + " - Tkinter")
        self.root.geometry("1280x760")
        self.root.configure(bg="#0b1020")

        self.tracker = StudentTracker()

        self._setup_style()
        self._build_header()
        self._build_form()
        self._build_table()
        self._build_chart()
        self._refresh_everything()

    def _setup_style(self) -> None:
        '''Configure ttk widget styling.'''
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background="#0b1020")
        style.configure("Card.TFrame", background="#131a2f")
        style.configure("Dark.TLabel", background="#0b1020", foreground="#e5ecff", font=("Arial", 11))
        style.configure("Title.TLabel", background="#0b1020", foreground="#76a9ff", font=("Arial", 22, "bold"))
        style.configure("CardTitle.TLabel", background="#131a2f", foreground="#76a9ff", font=("Arial", 13, "bold"))
        style.configure("Dark.TEntry", fieldbackground="#1a2340", foreground="#ffffff")
        style.configure("Dark.Treeview", background="#131a2f", fieldbackground="#131a2f", foreground="#f5f7ff", rowheight=28)
        style.configure("Dark.Treeview.Heading", background="#243359", foreground="#ffffff", font=("Arial", 10, "bold"))
        style.map("Dark.Treeview", background=[("selected", "#2b5cff")])
        style.configure("Accent.TButton", background="#2b5cff", foreground="#ffffff", font=("Arial", 10, "bold"))

    def _build_header(self) -> None:
        '''Build the top title area.'''
        header = ttk.Frame(self.root, style="Dark.TFrame")
        header.pack(fill="x", padx=18, pady=(16, 8))
        ttk.Label(header, text=APP_NAME + " Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Add, search, sort, analyse, and visualise student data.", style="Dark.TLabel").pack(anchor="w", pady=(4, 0))

    def _build_form(self) -> None:
        '''Build the input form and action buttons.'''
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

        search_row = ttk.Frame(form, style="Card.TFrame")
        search_row.grid(row=7, column=0, columnspan=4, sticky="ew", padx=10, pady=(0, 12))
        ttk.Label(search_row, text="Search", style="Dark.TLabel").pack(side="left", padx=(0, 8))
        ttk.Entry(search_row, textvariable=self.search_var, width=30).pack(side="left")
        ttk.Button(search_row, text="Run Search", style="Accent.TButton", command=self.run_search).pack(side="left", padx=6)
        ttk.Button(search_row, text="Sort by Name", style="Accent.TButton", command=lambda: self.refresh_table("name")).pack(side="left", padx=4)
        ttk.Button(search_row, text="Sort by Attendance", style="Accent.TButton", command=lambda: self.refresh_table("attendance")).pack(side="left", padx=4)
        ttk.Button(search_row, text="Sort by Average", style="Accent.TButton", command=lambda: self.refresh_table("average")).pack(side="left", padx=4)

    def _build_table(self) -> None:
        '''Build the student table.'''
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
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_chart(self) -> None:
        '''Build the Tkinter Canvas chart area.

        This visualises grade averages using rectangles and text labels,
        satisfying the data visualisation requirement with Tkinter.
        '''
        right = ttk.Frame(self.root, style="Card.TFrame")
        right.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Label(right, text="Average Score Visualisation", style="CardTitle.TLabel").pack(anchor="w", padx=12, pady=(10, 6))
        self.chart_canvas = tk.Canvas(right, height=260, bg="#11182c", highlightthickness=0)
        self.chart_canvas.pack(fill="x", padx=12, pady=(0, 12))

    def _refresh_everything(self) -> None:
        '''Refresh table and chart together.'''
        self.refresh_table("name")
        self.draw_chart()

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

    def draw_chart(self, students=None) -> None:
        '''Draw a simple bar chart with Tkinter Canvas.'''
        self.chart_canvas.delete("all")
        students = self.tracker.sort_students("average") if students is None else students
        students = students[:8]

        width = max(self.chart_canvas.winfo_width(), 900)
        height = 260
        self.chart_canvas.config(scrollregion=(0, 0, width, height))
        self.chart_canvas.create_text(20, 20, anchor="w", fill="#dce6ff", font=("Arial", 12, "bold"), text="Top 8 student averages")

        if not students:
            self.chart_canvas.create_text(20, 70, anchor="w", fill="#ffffff", font=("Arial", 12), text="No data available yet.")
            return

        bar_width = 80
        gap = 25
        start_x = 30
        base_y = 210
        max_height = 140

        for index, student in enumerate(students):
            average = self.tracker.calculate_student_average(student)
            if average is None:
                average = 0
            bar_height = max_height * (average / 100)
            x1 = start_x + index * (bar_width + gap)
            y1 = base_y - bar_height
            x2 = x1 + bar_width
            y2 = base_y

            self.chart_canvas.create_rectangle(x1, y1, x2, y2, fill="#3e6cff", outline="#7fa4ff")
            self.chart_canvas.create_text((x1 + x2) / 2, y1 - 12, fill="#ffffff", text=f"{average:.1f}")
            self.chart_canvas.create_text((x1 + x2) / 2, base_y + 14, fill="#dce6ff", text=student.name[:10])

        self.chart_canvas.create_line(20, base_y, width - 30, base_y, fill="#ffffff")

    def run_search(self) -> None:
        '''Search students and update the table/chart.'''
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_table("name")
            return
        results = self.tracker.search_students(keyword)
        self.refresh_table(students=results)

    def on_select(self, _event=None) -> None:
        '''Load the selected row into the input fields.'''
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

    def alert(self, title: str, message: str, is_error: bool = False) -> None:
        '''Display either an info or error message box.'''
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)

    def add_student(self) -> None:
        '''Button action: add a student.'''
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
        '''Button action: update a student.'''
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
        '''Button action: add a module.'''
        try:
            self.tracker.add_module(self.student_id_var.get(), self.module_var.get(), self.lecturer_var.get())
            self._refresh_everything()
            self.alert("Success", "Module added successfully.")
        except (ValidationError, TrackerError) as exc:
            self.alert("Error", str(exc), True)

    def add_assessment(self) -> None:
        '''Button action: add an assessment.'''
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
        '''Button action: export CSV report.'''
        path = self.tracker.export_csv()
        self.alert("Export Complete", f"CSV report saved to: {path}")

    def seed_demo(self) -> None:
        '''Button action: insert sample data.'''
        try:
            self.tracker.seed_demo_data()
            self._refresh_everything()
            self.alert("Success", "Demo data inserted.")
        except TrackerError as exc:
            self.alert("Error", str(exc), True)


def main() -> None:
    '''Start the Tkinter application.'''
    root = tk.Tk()
    TrackerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
