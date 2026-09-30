# Project Report: Shramik Setu

Feel free to use this as a draft. Consult your department’s project guidelines PDF to update the title page, section names, length, and order according to their template.

1. Project title

Shramik Setu – Automated Daily Wage Ledger

2. Introduction and problem statement

Daily attendance and wage records for workers can be maintained manually. This practice becomes inconvenient for larger groups as retrieving specific entries becomes time-consuming. Shramik Setu is a desktop application that maintains worker records, their working hours, and wages.

This project implements a basic Python application for a specific task to demonstrate Python’s versatility as a programming language.

3. Objectives

The main objectives of the project are as follows:

• Maintain a reference list of currently employed workers

• Keep track of daily working shifts

• Calculate wage amounts based on daily shifts

• Record if a worker has been paid or not

• Persist data across application launches

• Export shift records in CSV format

4. Tools used

The following tools are used in the project:

• Python programming language

• Tkinter / Ttk GUI framework

• CSV data serialization format

• Unittest testing framework

5. Program organization

The application’s source code is split into discrete modules for separation of concerns.

Module

Purpose

app.py

Implements the graphical user interface (GUI) windows, forms, tables, and operations

worker_manager.py

Manages worker records, skill categories, and persistence

attendance_engine.py

Implements duration calculation and payment logic

storage.py

Implements saving and loading operations for CSV files

6. Program algorithms

There are several algorithms that implement the program’s logic. For example, when registering a worker:

1. Read the name, experience, and daily wage from the form fields

2. Validate the input fields are not empty and that numbers are positive

3. Validate that the experience is appropriate for a given skill category

4. Assign the next available worker ID

5. Update the workers list

Another algorithm calculates the duration and wage for a shift:

1. Read the worker, date, check-in, and check-out time

2. Validate the date and time formats

3. Validate that the chosen worker is registered and that the check-out time is after check-in

4. Calculate the duration in hours

5. Calculate the wage amount based on the daily rate for 8-hour shifts

6. Save the new shift record with status ‘UNPAID’

Updating the status of a shift to ‘PAID’ involves the following steps:

1. Find the shift record by the given ID

2. If it does not exist, display an error message

3. If the shift is already paid, do nothing

4. Update the status to ‘PAID’ and record the current date and time

7. Time and space complexity

The application’s time and space complexity can be expressed with Big O notation as follows:

• Looking for a worker by ID requires O(W) time complexity in the worst case

• Looking for a shift by ID requires O(S) time complexity in the worst case

• Reading from and writing to CSV files requires O(N) time complexity, where N is the number of rows

• Storing worker and shift records requires O(W + S) space complexity, where W is the number of workers and S is the number of shifts

8. Testing

The following unit tests are implemented:

• Tests for skill category boundaries

• Tests for negative experience and zero daily wage

• Tests for parsing date and time strings

To execute the unit tests, change into the project directory and execute the following command:

python -m unittest discover -s tests -v

Include the output from your unit tests in this section. You may also want to test the application manually, for example, by attempting to submit an empty form or invalid date, register a worker, record a shift, and mark it as paid.

9. Limitations

The application is suitable for demonstration purposes. It is not a production-ready payroll system because:

• It stores data in CSV files rather than a database

• It is designed for single-user/single-computer use

• It does not support multi-day shifts or overtime

• It does not provide user account management

• It does not support concurrency

• The formula for calculating daily wage is oversimplified

10. Conclusion

Shramik Setu demonstrates how Python can be used to create a functioning desktop application. It organizes code into discrete modules for separation of concerns. Additionally, the application’s logic and presentation layers are divided, which increases maintainability. The program can be expanded by adding new features such as more types of payments, reports, and enhanced validation checks.