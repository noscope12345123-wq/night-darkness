from __future__ import annotations

"""Flask web interface for Student Progress Tracker Pro Ultra.

References:
- Flask quickstart: https://flask.palletsprojects.com/en/stable/quickstart/
- Flask testing: https://flask.palletsprojects.com/en/stable/testing/
"""

from flask import Flask, flash, redirect, render_template, request, url_for

from corepkg import APP_NAME, StudentTracker, TrackerError, ValidationError

app = Flask(__name__)
app.secret_key = 'night-iy499-ultra-secret'
tracker = StudentTracker()


@app.route('/')
def index():
    sort_by = request.args.get('sort', 'name')
    query = request.args.get('q', '').strip()
    students = tracker.search_students(query) if query else tracker.sort_students(sort_by)
    return render_template('index.html', app_name=APP_NAME, tracker=tracker, students=students, stats=tracker.dashboard_metrics(), sort_by=sort_by, query=query)


@app.route('/student/<student_id>')
def student_detail(student_id: str):
    student = tracker.get_student(student_id)
    return render_template('student_detail.html', app_name=APP_NAME, tracker=tracker, student=student, info=tracker.summary_for_student(student))


@app.route('/add-student', methods=['POST'])
def add_student():
    try:
        tracker.add_student(
            request.form.get('student_id', ''),
            request.form.get('name', ''),
            request.form.get('email', ''),
            request.form.get('course', ''),
            float(request.form.get('attendance', '100') or 100),
            request.form.get('notes', ''),
        )
        flash('Student added successfully.', 'success')
    except (ValidationError, TrackerError, ValueError) as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('index'))


@app.route('/add-module', methods=['POST'])
def add_module():
    student_id = request.form.get('student_id', '')
    try:
        tracker.add_module(student_id, request.form.get('module_name', ''), request.form.get('lecturer', ''))
        flash('Module added successfully.', 'success')
    except (ValidationError, TrackerError) as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('student_detail', student_id=student_id))


@app.route('/add-assessment', methods=['POST'])
def add_assessment():
    student_id = request.form.get('student_id', '')
    try:
        tracker.add_assessment(
            student_id,
            request.form.get('module_name', ''),
            request.form.get('assessment_name', ''),
            float(request.form.get('score', '0') or 0),
            float(request.form.get('weight', '0') or 0),
            request.form.get('feedback', ''),
        )
        flash('Assessment added successfully.', 'success')
    except (ValidationError, TrackerError, ValueError) as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('student_detail', student_id=student_id))


@app.route('/export')
def export_report():
    path = tracker.export_csv()
    flash(f'CSV report exported to {path}', 'success')
    return redirect(url_for('index'))


@app.route('/seed-demo', methods=['POST'])
def seed_demo():
    try:
        tracker.seed_demo_data()
        flash('Demo data inserted.', 'success')
    except TrackerError as exc:
        flash(str(exc), 'warning')
    return redirect(url_for('index'))


@app.route('/delete-student/<student_id>', methods=['POST'])
def delete_student(student_id: str):
    try:
        tracker.delete_student(student_id)
        flash(f'Deleted {student_id}.', 'success')
    except TrackerError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
