"""Input checks shared by the Shramik Setu project."""
from datetime import datetime


def validate_name(name):
    name = str(name).strip()
    if not name:
        raise ValueError("Please enter the worker's name.")
    return name


def validate_experience(value):
    try:
        years = float(value)
    except (TypeError, ValueError):
        raise ValueError("Experience must be a number.")
    if years < 0:
        raise ValueError("Experience cannot be negative.")
    return years


def validate_daily_rate(value):
    try:
        rate = float(value)
    except (TypeError, ValueError):
        raise ValueError("Daily wage must be a number.")
    if rate <= 0:
        raise ValueError("Daily wage must be greater than zero.")
    return rate


def validate_date(value):
    try:
        return datetime.strptime(str(value).strip(), "%d-%m-%Y").strftime("%d-%m-%Y")
    except (TypeError, ValueError):
        raise ValueError("Enter the date as DD-MM-YYYY, for example 30-09-2026.")


def validate_time(value):
    try:
        parsed = datetime.strptime(str(value).strip(), "%H:%M")
        return parsed.strftime("%H:%M")
    except (TypeError, ValueError):
        raise ValueError("Enter the time in 24-hour HH:MM format, for example 08:30.")
