"""Small calculations used by Shramik Setu.

The functions are kept separate from the screen so they can be tested on their own.
"""


def skill_from_experience(years):
    """Return a simple skill category based on years of experience."""
    years = float(years)
    if years < 0:
        raise ValueError("Experience cannot be negative.")
    if years <= 1:
        return "Unskilled"
    if years <= 3:
        return "Semi-Skilled"
    return "Skilled"


def working_hours(check_in_minutes, check_out_minutes):
    """Calculate a shift's length from minutes after midnight."""
    if check_out_minutes <= check_in_minutes:
        raise ValueError("Check-out must be later than check-in.")
    return (check_out_minutes - check_in_minutes) / 60


def calculate_wage(daily_rate, hours, standard_hours=8):
    """Pay a proportional part of the daily rate for the hours worked."""
    daily_rate, hours, standard_hours = float(daily_rate), float(hours), float(standard_hours)
    if daily_rate <= 0 or hours <= 0 or standard_hours <= 0:
        raise ValueError("Wage, hours, and standard hours must be positive.")
    return round(daily_rate * hours / standard_hours, 2)
