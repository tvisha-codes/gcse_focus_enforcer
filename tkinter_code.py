import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, date, timedelta


LOG_FILE = "study_log.json"

# MY FIRST EXAM DATE
EXAM_DATE = date(2026, 5, 8)

# Load log
try:
    with open(LOG_FILE, "r") as f:
        log = json.load(f)
except:
    log = []

# SESSION RESUME OPTION
session_score = 0  # default

if log:  # if there is previous work
    answer = input("Do you want to continue your last session? (y/n): ").lower()
    if answer == "y":
        # calculate session_score as sum of today's logs
        from datetime import date, datetime
        today = date.today()
        session_score = sum(
            entry["score"] for entry in log
            if datetime.strptime(entry["time"], "%Y-%m-%d %H:%M").date() == today
        )
        print(f"Continuing session. Current session score: {int(session_score)}")
    else:
        session_score = 0

def save_log():
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def calculate_score(method, amount):
    if method == "Flashcards":
        return amount * 1
    elif method == "Notes":
        return amount * 2
    elif method == "Questions":
        return amount * 5
    elif method == "Essay Question":
        return amount * 2
    elif method == "Past Paper":
        return amount * 75
    elif method == "Timed (minutes)":
        return amount * 0.7
    return 0

def fatigue_check():
    today = date.today()
    total = 0

    for entry in log:
        entry_date = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M").date()
        if entry_date == today:
            total += entry["score"]

    return total > 220


# ---------------- STREAK SYSTEM ----------------

def get_streak():
    if not log:
        return 0

    days = set()
    for entry in log:
        d = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M").date()
        days.add(d)

    streak = 0
    today = date.today()

    if today not in days and (today - timedelta(days=1)) not in days:
        return 0

    check_day = today
    if today not in days:
        check_day = today - timedelta(days=1)

    while check_day in days:
        streak += 1
        check_day -= timedelta(days=1)

    return streak

# ---------------- UI ----------------

root = tk.Tk()
root.title("EXAM DISCIPLINE ENFORCER")
root.geometry("650x560")
root.resizable(False, False)

# Countdown + Streak
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

countdown_label = tk.Label(top_frame, text="", font=("Arial", 18, "bold"))
countdown_label.pack()

streak_label = tk.Label(top_frame, text="", font=("Arial", 14, "bold"))
streak_label.pack()

def update_top_info():
    today = date.today()
    days_left = (EXAM_DATE - today).days

    if days_left < 0:
        countdown_label.config(text="❗ EXAMS HAVE STARTED.")
    else:
        countdown_label.config(text=f"⏳ {days_left} days until your FIRST EXAM.")

    streak = get_streak()
    streak_label.config(text=f"🔥 Current study streak: {streak} days")

    root.after(60000, update_top_info)

update_top_info()

# Form
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Subject:").grid(row=0, column=0, sticky="w")
subject_entry = tk.Entry(frame, width=40)
subject_entry.grid(row=0, column=1)

tk.Label(frame, text="Topic:").grid(row=1, column=0, sticky="w")
topic_entry = tk.Entry(frame, width=40)
topic_entry.grid(row=1, column=1)

tk.Label(frame, text="Method:").grid(row=2, column=0, sticky="w")
method_box = ttk.Combobox(frame, values=[
    "Flashcards", "Notes", "Questions", "Essay Question", "Past Paper", "Timed (minutes)"
])
method_box.grid(row=2, column=1)
method_box.current(0)

tk.Label(frame, text="How many?(Marks?)").grid(row=3, column=0, sticky="w")
amount_entry = tk.Entry(frame, width=20)
amount_entry.grid(row=3, column=1, sticky="w")

# Status box
status_text = tk.Text(root, height=12, width=75, font=("Arial", 11))
status_text.pack(pady=15)

def write_status(msg):
    status_text.delete("1.0", tk.END)
    status_text.insert(tk.END, msg)


def log_work():
    global session_score

    subject = subject_entry.get().strip()
    topic = topic_entry.get().strip()
    method = method_box.get().strip()

    try:
        amount = int(amount_entry.get())
    except:
        messagebox.showerror("Invalid", "Amount must be a number.")
        return

    if not subject or not topic or amount <= 0:
        messagebox.showerror("No cheating", "Fill everything properly.")
        return

    score = calculate_score(method, amount)
    session_score += score

    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "subject": subject,
        "topic": topic,
        "method": method,
        "amount": amount,
        "score": score
    }

    log.append(entry)
    save_log()

    update_top_info()

    msg = f"Logged: {subject} - {topic}\nMethod: {method}\nAmount: {amount}\nScore: {int(score)}\n\n"
    msg += f"SESSION TOTAL SCORE: {int(session_score)}\n\n"

    if session_score < 80:
        msg += "❌ THIS IS WEAK. YOU ARE NOT DONE.\nDo more. Now."
    elif session_score < 150:
        msg += "⚠️ BARELY ACCEPTABLE. You should do more."
    elif session_score < 250:
        msg += "✅ SOLID SESSION. Still push further."
    else:
        msg += "🔥 ELITE SESSION. This is how top students work."

    if fatigue_check():
        msg += "\n\n⚠️ FATIGUE DETECTED.\nYOU SHOULD TAKE A BREAK."

    write_status(msg)

def attempt_end():
    if session_score < 150:
        messagebox.showwarning(
            "Not allowed",
            "You have NOT done enough work. Keep going."
        )
        return

    if fatigue_check():
        messagebox.showwarning(
            "Break required",
            "Fatigue detected. Take a break before continuing."
        )
        return

    if messagebox.askyesno("End Session", "Are you SURE you are done?"):
        root.destroy()

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack()

log_btn = tk.Button(btn_frame, text="LOG WORK", font=("Arial", 12, "bold"), command=log_work)
log_btn.grid(row=0, column=0, padx=10)

end_btn = tk.Button(btn_frame, text="END SESSION", font=("Arial", 12, "bold"), command=attempt_end)
end_btn.grid(row=0, column=1, padx=10)

# Startup message
write_status(
    "EXAM DISCIPLINE MODE ACTIVE.\n\n"
    "🔥 Protect your streak.\n"
    "❌ No zero-work days.\n"
    "⏳ Your exams are coming.\n\n"
    "Earn the right to stop."
)

root.mainloop()