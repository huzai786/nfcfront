import requests
from datetime import datetime

employee_flexibility = ["Flexible", "Strict"]
def get_employee_schedule(api_url, uid):
    payload = {"uid": uid}
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("schedule") is None:
                print("Employee does not exist.")
                return None
            else:
                return {
                    "employee_name": data["schedule"]["employee_name"],
                    "employee_flexibility": data["schedule"]["employee_flexibility"],
                    "starttime":datetime.combine(datetime.today(), datetime.strptime(data["schedule"]["starttime"], "%H:%M:%S").time())  ,
                    "endtime":datetime.combine(datetime.today(), datetime.strptime(data["schedule"]["endtime"], "%H:%M:%S").time())  ,
                    "breaktime":datetime.combine(datetime.today(), datetime.strptime(data["schedule"]["breaktime"], "%H:%M:%S").time())  ,
                }
        else:
            # Handle other HTTP errors
            print(f"Failed to retrieve schedule: {response.status_code}")
            return None

    except requests.RequestException as e:
        # Handle any request exceptions
        print(f"Request error: {e}")
        return None
    

def create_clockin(api_url, uid, overtime=False):
    payload = {"uid": uid, "overtime": overtime, "time": datetime.now().strftime("%H:%M:%S")}
    try:
        res = requests.post(api_url, json=payload)
        if res.status_code == 200:
            return True
            
    except requests.RequestException as e:
        print(e)
        return None
    

def create_clockout(api_url, uid, overtime=False):
    payload = {"uid": uid, "overtime": overtime, "time": datetime.now().strftime("%H:%M:%S")}
    try:
        res = requests.post(api_url, json=payload)
        if res.status_code == 200:
            return True
        else:
            return False        
    
    except requests.RequestException as e:
        print(e)
        return None