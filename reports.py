"""A few plain-text reports for workers and shift payments."""
from collections import defaultdict


def payment_summary(shifts):
    """Summarize paid and unpaid amounts from a list of shift dictionaries."""
    summary = {"shift_count": len(shifts), "paid_count": 0, "unpaid_count": 0,
               "paid_amount": 0.0, "unpaid_amount": 0.0}
    for shift in shifts:
        amount = float(shift.get("wage", 0) or 0)
        if shift.get("status") == "PAID":
            summary["paid_count"] += 1
            summary["paid_amount"] += amount
        else:
            summary["unpaid_count"] += 1
            summary["unpaid_amount"] += amount
    summary["paid_amount"] = round(summary["paid_amount"], 2)
    summary["unpaid_amount"] = round(summary["unpaid_amount"], 2)
    return summary


def worker_totals(shifts):
    """Return hours and wages grouped by worker ID."""
    totals = defaultdict(lambda: {"worker_name": "", "hours": 0.0, "wages": 0.0})
    for shift in shifts:
        item = totals[shift.get("worker_id", "")]
        item["worker_name"] = shift.get("worker_name", "")
        item["hours"] += float(shift.get("hours", 0) or 0)
        item["wages"] += float(shift.get("wage", 0) or 0)
    return {key: {**value, "hours": round(value["hours"], 2),
                  "wages": round(value["wages"], 2)} for key, value in totals.items()}


def format_payment_report(shifts):
    """Create a report that can be printed or saved as a text file."""
    summary = payment_summary(shifts)
    lines = [
        "SHRAMIK SETU - PAYMENT SUMMARY",
        "=" * 34,
        f"Shifts recorded: {summary['shift_count']}",
        f"Paid shifts: {summary['paid_count']} (₹{summary['paid_amount']:.2f})",
        f"Unpaid shifts: {summary['unpaid_count']} (₹{summary['unpaid_amount']:.2f})",
        "",
        "WORKER-WISE TOTALS",
        "-" * 34,
    ]
    for worker_id, data in worker_totals(shifts).items():
        lines.append(f"{worker_id} | {data['worker_name']} | {data['hours']:.2f} hours | ₹{data['wages']:.2f}")
    if not shifts:
        lines.append("No shifts have been recorded yet.")
    return "\n".join(lines)
