# APP NAME
Student Progress Tracker Pro

GitHub Repository URL:  
The source code for this project is available on GitHub: `PASTE-YOUR-GITHUB-REPOSITORY-URL-HERE`

## Identification
- Name: Night
- P-number: 476432
- Course code: IY499

## Declaration of Own Work
I confirm that this assignment is my own work. Where I referred to documentation, tutorials, libraries, or learning resources, I cited them in code comments and in the references section below.

## Introduction
This project implements a student record and progress analysis system using **Python**, **Tkinter**, and **Flask**. One shared backend file powers three interfaces:
- `console_app.py` – console version
- `tkinter_app.py` – desktop GUI version with **Tkinter data visualisation**
- `flask_app.py` – browser-based web version

The program can:
- add, update, search, sort, and delete student records
- add modules and weighted assessments
- calculate averages, grade bands, progress status, pass rate, and recommendations
- save records to JSON, write activity logs, and export CSV reports
- display a Tkinter bar chart for average scores
- handle invalid inputs with validation and exceptions

## Installation
1. Make sure Python 3.x is installed.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run the App
```bash
python console_app.py
python tkinter_app.py
python flask_app.py
python tests.py
```

## App Elements
- **Student profiles**: ID, name, email, course, attendance, notes
- **Module records**: module name, lecturer, assessment list
- **Assessment tracking**: score, weight, and feedback
- **Analytics dashboard**: average grade, attendance, pass rate, at-risk count
- **Tkinter chart**: bar chart showing top student averages
- **File handling**: JSON storage, CSV export, and log file writing
- **Error handling**: validation, custom exceptions, and safe recovery
- **Algorithms**: explicit linear search and explicit bubble sort

## Package Management
External libraries are listed in `requirements.txt` and can be installed with `pip`. This follows package management good practice and makes the project reproducible on another machine.

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

## Testing
`tests.py` covers:
- valid cases
- invalid input cases
- edge cases such as assessment weight overflow
- CSV export
- log creation
- a Flask route smoke test when Flask is installed

## Comments and References in Code
The brief asks for comments and cited references. I added:
- file-level reference blocks
- comments near important library/API usage
- docstrings explaining key functions and algorithms

I did **not** put a fake source under every single line, because many lines are original project logic rather than copied from a single source. Instead, I cited the official documentation for each library, function family, or feature used.

## GitHub / Version Control Plan
Use small, meaningful commits when uploading:

```bash
git init
git add README.md README.txt requirements.txt .gitignore
git commit -m "Set up project documentation and dependency list"

git add core.py
git commit -m "Build shared tracker core with validation, analytics, and file handling"

git add console_app.py
git commit -m "Add console interface with safe input and menu system"

git add tkinter_app.py
git commit -m "Create Tkinter interface with chart visualisation and dashboard cards"

git add flask_app.py templates/
git commit -m "Add Flask web version and styled HTML templates"

git add tests.py
git commit -m "Add tests for valid, invalid, and edge cases"

git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## References
- Python tutorial: https://docs.python.org/3/tutorial/
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- Python json: https://docs.python.org/3/library/json.html
- Python csv: https://docs.python.org/3/library/csv.html
- Python datetime: https://docs.python.org/3/library/datetime.html
- Python pathlib: https://docs.python.org/3/library/pathlib.html
- Python re: https://docs.python.org/3/library/re.html
- Python typing: https://docs.python.org/3/library/typing.html
- Python exceptions tutorial: https://docs.python.org/3/tutorial/errors.html
- Tkinter docs: https://docs.python.org/3/library/tkinter.html
- ttk docs: https://docs.python.org/3/library/tkinter.ttk.html
- messagebox docs: https://docs.python.org/3/library/tkinter.messagebox.html
- Flask quickstart: https://flask.palletsprojects.com/en/stable/quickstart/
- Flask tutorial: https://flask.palletsprojects.com/en/stable/tutorial/
- Flask testing: https://flask.palletsprojects.com/en/stable/testing/
- Colorama: https://pypi.org/project/colorama/
