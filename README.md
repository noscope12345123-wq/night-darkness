# APP NAME
Student Progress Tracker Pro

GitHub Repository URL:  
The source code for this project is available on GitHub: `PASTE-YOUR-GITHUB-REPOSITORY-URL-HERE`

## Identification
- Name: Night
- P-number: 476432
- Course code: IY499

## Declaration of Own Work
I confirm that this assignment is my own work. Where I have referred to documentation, tutorials, libraries, or learning resources, I have cited them in code comments and in the references section below.

## Introduction
This project implements a student record and progress analysis system using **Python**, **Tkinter**, and **Flask**. The same shared backend is reused across three interfaces:
- `console_app.py` – console version
- `tkinter_app.py` – desktop GUI version with **Tkinter data visualisation**
- `flask_app.py` – browser-based web version

The main functionality of the app includes:
- adding, editing, searching, sorting, and deleting student records
- adding modules and weighted assessments
- calculating averages, grade bands, and progress status
- exporting a CSV report
- saving data in JSON and writing actions to a log file

## Installation
To run the app locally:
1. Make sure Python 3.x is installed.
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run the App
1. Open terminal/command prompt in the project folder.
2. Run one of the following:
   ```bash
   python console_app.py
   python tkinter_app.py
   python flask_app.py
   ```
3. For testing:
   ```bash
   python tests.py
   ```

## App Elements
- **Student Profiles**: store ID, name, email, course, attendance, and notes
- **Module and Assessment Tracking**: manage academic performance data
- **Dashboard Analytics**: show average grade, attendance, at-risk count, and top student
- **Tkinter Chart**: visualise average results as a bar chart
- **File Handling**: JSON storage, CSV export, and log file creation
- **Error Handling**: catches invalid data and prevents crashes
- **Search and Sorting Algorithms**: explicit linear search and bubble sort for evidence of algorithm use

## Libraries Used
- **Tkinter** – desktop GUI and data visualisation
- **Flask** – web application framework
- **colorama** – optional coloured console text
- **json / csv / re / datetime / dataclasses / typing** – standard Python libraries used for file handling, validation, dates, and structured data

## Project Structure
```text
student_tracker_github_ready/
├── templates/
│   ├── base.html
│   ├── index.html
│   └── student_detail.html
├── core.py
├── console_app.py
├── tkinter_app.py
├── flask_app.py
├── tests.py
├── requirements.txt
├── README.md
├── README.txt
└── .gitignore
```

## Package Management
External packages are listed in `requirements.txt` and can be installed with pip. This keeps the project easier to run on another machine and follows package management best practice.

## Testing
Test scenarios included in `tests.py` cover:
- **Valid cases**: adding a valid student, module, and assessment
- **Invalid cases**: duplicate ID and invalid email
- **Edge/boundary cases**: report export, sorting, and searching behaviour

## GitHub / Version Control Plan
The brief asks for small, meaningful commits spread through development. I cannot create a real GitHub history from here, but use a sequence like this when uploading:

```bash
git init
git add README.md README.txt requirements.txt .gitignore
git commit -m "Set up project documentation and dependency list"

git add core.py
git commit -m "Build shared tracker core with file handling and validation"

git add console_app.py
git commit -m "Add console interface with safe input and menu system"

git add tkinter_app.py
git commit -m "Create Tkinter interface with chart visualisation"

git add flask_app.py templates/
git commit -m "Add Flask web version and HTML templates"

git add tests.py
git commit -m "Add manual tests for valid and invalid cases"

git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## References
Official and learning resources used:
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- Python json: https://docs.python.org/3/library/json.html
- Python csv: https://docs.python.org/3/library/csv.html
- Python datetime: https://docs.python.org/3/library/datetime.html
- Python re: https://docs.python.org/3/library/re.html
- Python exceptions tutorial: https://docs.python.org/3/tutorial/errors.html
- Python tutorial: https://docs.python.org/3/tutorial/
- Tkinter docs: https://docs.python.org/3/library/tkinter.html
- ttk docs: https://docs.python.org/3/library/tkinter.ttk.html
- messagebox docs: https://docs.python.org/3/library/tkinter.messagebox.html
- Flask quickstart: https://flask.palletsprojects.com/en/stable/quickstart/
- Flask tutorial: https://flask.palletsprojects.com/en/stable/tutorial/
- Flask installation: https://flask.palletsprojects.com/en/stable/installation/
- Colorama: https://pypi.org/project/colorama/
