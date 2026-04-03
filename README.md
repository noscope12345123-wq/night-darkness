# Student Progress Tracker Pro Ultra

**GitHub Repository URL:** Paste your repository link here after upload.

## Identification
- **Name:** Night
- **P-number:** 476432
- **Course code:** IY499

## Declaration of Own Work
I confirm that this assignment is my own work. Where I referred to external resources, I cited them in code comments and in the references section below.

## Introduction
Student Progress Tracker Pro Ultra is a Python coursework project that manages student performance data across three interfaces: a console application, a Tkinter desktop dashboard, and a Flask web app. The system stores students, modules, and weighted assessments, then calculates averages, grade bands, attendance risk, pass rate, trend analysis, and generated recommendations. The project demonstrates practical programming skills by combining functions, methods, file handling, error handling, searching, sorting, and data visualisation.

## Main Features
- Add, update, search, sort, and delete student records
- Add modules and weighted assessments
- JSON persistence, CSV export, logging, and automatic backups
- Tkinter data visualisation using a Canvas bar chart
- Flask web dashboard with analytics panels
- Explicit **linear search** and **bubble sort** algorithms for coursework evidence
- Robust validation and custom exceptions
- Test scenarios for valid, invalid, and edge cases

## Installation
1. Install Python 3.10+.
2. Open the project folder in terminal.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
### Console version
```bash
python console_app.py
```

### Tkinter version
```bash
python tkinter_app.py
```

### Flask version
```bash
python flask_app.py
```
Then open the local URL shown in the terminal.

### Tests
```bash
python tests.py
```

## Project Structure
```text
student_tracker_ultra_final/
├── corepkg/
│   ├── __init__.py
│   ├── analytics.py
│   ├── errors.py
│   ├── models.py
│   ├── services.py
│   └── storage.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── student_detail.html
├── console_app.py
├── tkinter_app.py
├── flask_app.py
├── tests.py
├── requirements.txt
├── README.md
└── README.txt
```

## Package Management
External packages are listed in `requirements.txt`.
- **Flask**: web interface
- **colorama**: coloured console output
- **Tkinter**: desktop GUI and visualisation (included with standard Python on most installations)

## Testing
Included test scenarios cover:
- valid input and expected behaviour
- invalid input such as duplicate IDs and bad emails
- edge cases such as assessment weight overflow and empty data
- CSV export, persistence reload, and backup creation
- Flask route smoke test when Flask is installed

## References
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- Python JSON: https://docs.python.org/3/library/json.html
- Python CSV: https://docs.python.org/3/library/csv.html
- Python regex: https://docs.python.org/3/library/re.html
- Python exceptions: https://docs.python.org/3/tutorial/errors.html
- Python Tkinter: https://docs.python.org/3/library/tkinter.html
- TkDocs Canvas tutorial: https://tkdocs.com/tutorial/canvas.html
- Flask quickstart: https://flask.palletsprojects.com/en/stable/quickstart/
- Flask testing: https://flask.palletsprojects.com/en/stable/testing/
- Colorama: https://pypi.org/project/colorama/
