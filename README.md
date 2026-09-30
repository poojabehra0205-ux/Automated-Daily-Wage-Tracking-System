# Shramik Setu

This project is a Python implementation to track daily wage workers' details and records.

Shramik setu is a desktop application to store and track daily wage workers' attendance, skill level, and payments. The application uses Python's Tkinter module as an interface and CSV files to store the data.

## Features

- Registering workers and assigning a worker id

- Grouping of workers into broad skill categories according to their years of experience.

- Storing a work date, check-in and check-out time of a worker.

- Calculating the number of working hours and the estimated wage.

- Marking of a shift as paid.

- Viewing and exporting the above records in CSV format.

- Generating reports in text using reports.py

## Requirements

- A Python version 3.9 or above. Make sure that Tkinter is installed in your Python environment.

- No third-party Python packages were used for this application.

## Getting started

Launch a terminal in the shramik_setu directory, and run the below command.

```bash

python main.py

```

The file app.py can also be used as the entry point for this application.

## Files

This application consists of the below files.

- `main.py`: This file is used to launch the desktop application.

- `app.py`: This is the main file for the Tkinter UI.

- `algorithms.py`: This file stores the algorithms for assigning skill levels and calculating wages.

- `validation.py`: This file contains helper methods to validate the input.

- `task_manager.py`: This file stores helper methods for managing the tasks for the application development.

- `reports.py`: This file generates a summary of payments and other worker details.

- `design.md`: This file contains the design documentation of the application.

- `statement.md`: This file contains the project description, challenges, goals, and scope of the application.

- `src/`: This directory stores files related to implementing the business logic like storing and retrieving the worker details, attendance, and CSV files.

- `tests/`: This directory stores test files for the application.

Wage calculation formula:

For this project, a working day is considered to be 8 hours.

```python

wage = daily_rate hours_worked // 8

```

The formula is only for the purposes of this project, and there is no provision for overnight shifts or overtime.

When records are saved for the first time, a data directory is created. This directory stores two CSV files: `workers.csv` and `shifts.csv`. Make sure the files are not deleted or renamed since the application will not function correctly without them.

To run the tests, navigate to the root directory of the application in a terminal and run the command below:

```bash

python -m unittest discover -s tests

```

