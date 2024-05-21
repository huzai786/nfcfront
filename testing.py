from api import get_employee_schedule

api_url = "http://127.0.0.1:8000/api/get-schedule/"
uid = "1234"
schedule = get_employee_schedule(api_url, uid)
if schedule:
    print(f"Schedule: {schedule}")
else:
    print("No schedule found.")

