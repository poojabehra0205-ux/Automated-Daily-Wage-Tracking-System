# Sample Outputs

This file contains some examples of the output produced by the app as the result of a typical actions performed by the user. All samples are illustrative - none was generated as a result of an actual run of the application, or in context of any particular worker being employed.

## 1. Register a worker

Example input

- Name: Ravi Kumar

- Experience: 2 years

- Daily wage: ₹800

Message shown

```

Worker registered

Registered Ravi Kumar with ID W0001.

```

Example row in the Workers tab

| Worker ID | Name | Experience | Skill | Daily wage (₹) |

|---|---|---:|---|---:|

| W0001 | Ravi Kumar | 2.0 | Semi-Skilled | 800.00 |

## 2. Save an attendance shift

Example input

- Worker: W0001 – Ravi Kumar

- Date: 30-09-2026

- Check-in: 08:00

- Check-out: 16:00

The shift lasts 8 hours. Using the example project's algorithm (daily wage × hours worked ÷ 8), the calculated wage is ₹800.00.

Message shown

```

Shift saved

Saved S00001: 8.00 hours, ₹800.00.

```

Example row in the Shifts & Payments tab

| Shift ID | Worker | Date | Hours | Wage (₹) | Status |

|---|---|---|---:|---:|---|

| S00001 | Ravi Kumar (W0001) | 30-09-2026 | 8.00 | 800.00 | UNPAID |

## 3. Mark a shift as paid

After choosing the shift being processed and marking it as paid, the following message shall appear in the UI:

```

Payment updated

S00001 marked as PAID.

```

The status is updated from `UNPAID` to `PAID` in the records table. In addition, the payment's date and time is stored into the shift's record in the database.

## 4. Example validation messages

| Situation | Message |

|---|---|

| Name is left blank | Enter the worker's name. |

| Experience or wage is not numeric | Experience and daily wage must be numbers. |

| No worker is selected for attendance | Register and select a worker first. |

| Check-out is earlier than or equal to check-in | Check-out must be later than check-in; overnight shifts are not supported. |

| No shift is selected before payment | Select a shift first. |

## 5. Example CSV export

The CSV export contains a header row followed by the saved attendance records. Each of the above rows corresponds to a record which may be exported in the following manner (the content of the `paid_on` column varies depending on which shift was marked as paid):

```

shift_id,worker_id,worker_name,date,check_in,check_out,hours,wage,status,paid_on

S00001,W0001,Ravi Kumar,30-09-2026,08:00,16:00,8.0,800.0,PAID,"30-09-2026 16:30"

```

Note that the timestamp on the far right is an illustration of the data format that will be used; the actual datetime string will be printed by the application when a user marks a shift as paid.

## 6. Run the automated tests

From within the project folder, execute:

```

python -m unittest discover -s tests -v

```

The test runner will print the test's name and outcome (ok if it passes), followed by a test summary. Note that the actual test names and summary may vary depending on the contents of `tests/test_algorithms.py`.