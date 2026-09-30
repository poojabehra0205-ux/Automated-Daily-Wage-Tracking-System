# Design Notes — Shramik Setu

## Purpose of the project

Shramik Setu is a small desktop application designed to keep records of day-wage workers’ shifts in one place.

This helps everyday operations such as registration of new workers, recording of shifts and checking of payments that have already been made.

## Component Description

The following components make the Shramik Setu application:

Component Description

app.py The Tkinter graphical user interface (GUI) windows and buttons.

main.py A simple script to open the desktop application.

src/worker_manager.py A module to register and deactivate workers

src/attendance_engine.py Script to check details of shifts, calculate wages and mark payments.

src/storage.py A script to read and write CSV files.

algorithms.py A short file containing functions related to calculation of skills and wages.

validation.py Short validation functions related to names, numbers, dates and time.

reports.py A script to generate formatted payment reports.

The data related to workers is stored in a file called `data/workers.csv`. Information about specific shifts and payments is stored in `data/shifts.csv`. Storing this information in CSV format allows the files to be portable and easily viewed in a spreadsheet application without requiring additional software to manage a relational database.

## Calculating Wages

The wage calculation for the day-wage workers is based on a standard 8-hour day. This sets the ratio for calculating hourly wages

$$

\text{wage} = \frac{\text{daily rate} \times \text{hours worked}}{8}

$$

This is a very simplistic approach and not fit for production or for official payroll purposes. Adjustments for overtime, deductions and other considerations would have to be made in a real-world application.

The application uses Tkinter as the GUI framework due to its availability in most Python distributions.

The interface is split into tabs to allow swift navigation between managing workers and checking attendance and payments.