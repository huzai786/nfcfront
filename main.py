import time
import dearpygui.dearpygui as dpg
import queue
import threading
from datetime import datetime, timedelta
import pygame
from api import get_employee_schedule, create_clockin, create_clockout

pygame.init()

access_denied = pygame.mixer.Sound("AccessDenied.mp3")
access_granded = pygame.mixer.Sound("AccessGranted.mp3")
message = ""
last_time = None
nfc_queue = queue.Queue()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
overtime_selected = False
time_after_overtime_start = 15

API_URL_GET_SCHEDULE = "http://127.0.0.1:8000/api/get-schedule/"
API_URL_CREATE_CLOCKIN = "http://127.0.0.1:8000/api/create-clockin/"
API_URL_CREATE_CLOCKOUT = "http://127.0.0.1:8000/api/create-clockout/"


def nfc_reader():
    while True:
        uid = int(input("uid: "))
        nfc_queue.put(uid)

def update():
    current_time = time.strftime("%I:%M:%S %p")
    dpg.set_value("clock_label", current_time)
    global message, last_time
    # Check if the message should be cleared
    if last_time and (datetime.now() - last_time) > timedelta(seconds=5):
        message = ""
    dpg.set_value("message", message)

def on_medical_leave():
    print("Medical Leave button clicked")

def on_work_leave():
    print("Work Leave button clicked")

def on_log_overtime():
    global overtime_selected
    change_window("Over Time Window", "Digital Clock")
    overtime_selected = True

def change_window(to_id, from_id):
    dpg.configure_item(to_id, show=True)
    dpg.configure_item(from_id, show=False)

def check_nfc_queue():
    global message, last_time
    while not nfc_queue.empty():
        last_time = datetime.now()
        card_uid = nfc_queue.get()
        res = get_employee_schedule(API_URL_GET_SCHEDULE, card_uid)
        
        if not res:
            access_denied.play()
            message = "Access Denied"
            continue
        current_time = last_time
        employee_name = res["employee_name"]
        starttime = res["starttime"]
        endtime = res["endtime"]
        employee_flexibility = res["employee_flexibility"]

        message = f"{employee_name}\n"

        if overtime_selected:
            # its not the time for over time for that employee
            if current_time < (endtime + timedelta(minutes=time_after_overtime_start)):
                access_denied.play()
                message = "Access Denied"
                message += f"\nOver Time Not Started Yet, \nwill start after {endtime + timedelta(minutes=time_after_overtime_start)}."
            
            # its is a clock out of over time.
            elif current_time > (endtime + timedelta(minutes=time_after_overtime_start + 60)):
                created = create_clockout(API_URL_CREATE_CLOCKOUT, card_uid, True)
                if created:
                    access_granded.play()
                    message += "Access Granted!"
                else:
                    access_denied.play()
                    message = "Access Denied!\nUnable to create clock out for over time."
            
            # its is a clock in of over time.
            elif current_time > (endtime + timedelta(minutes=time_after_overtime_start)):
                created = create_clockin(API_URL_CREATE_CLOCKIN, card_uid, True)
                if not created:
                    access_denied.play()
                    message = "Access Denied!\nUnable to create clock in for over time."
                else:
                    access_granded.play()
                    message += "Access Granted!"

        # usual clock in or clock out
        else:
            # this is a clock in
            if abs(starttime - current_time) < timedelta(hours=1):
                if current_time < starttime:
                    # user is not late
                    created = create_clockin(API_URL_CREATE_CLOCKIN, card_uid, False) # create a clock in in the database.
                    if created:
                        message += "Access Granted!"
                        access_granded.play()
                    
                    else:
                        message = "Access Denied\nunable to create clock in."
                        access_denied.play()

                if current_time > starttime:
                    deltatime = current_time - starttime
                    message += f"\nyou came {deltatime} late."
                    created = create_clockin(API_URL_CREATE_CLOCKIN, card_uid)
                    if created:
                        message += "Access Granted!"
                        access_granded.play()
                    else:
                        message = "Access Denied\nunable to create clock in."
                        access_denied.play()
            
            # this is a clock out
            elif abs(endtime - current_time) < timedelta(hours=1):
                # user clock out early
                if current_time < endtime:
                    deltatime = endtime - current_time
                    message = f"you are clocking out {deltatime} minutes early!"
                    created = create_clockout(API_URL_CREATE_CLOCKOUT, card_uid, False) # create a clock out in the database.
                    if created:
                        message = "Clock Out Successful"
                        access_granded.play()
    
                    else:
                        message = "unable to create clock out."
                        access_denied.play()
                
                # user clock out on time
                if current_time > endtime:
                    created = create_clockout(API_URL_CREATE_CLOCKOUT, card_uid, False) # create a clock out in the database.
                    if created:
                        message = "Clock Out Successful"
                        access_granded.play()

                    else:
                        message = "unable to create clock out."
                        access_denied.play()



def main():
    dpg.create_context()
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvInputText, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 68), category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvInputInt, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 68), category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (30, 30, 30, 68), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 68), category=dpg.mvThemeCat_Core)
    
    dpg.bind_theme(global_theme)
    with dpg.font_registry():
        default_font = dpg.add_font("font.ttf", 40)
        medium_font = dpg.add_font("font.ttf", 30)
        bigfont = dpg.add_font("font.ttf", 100)

    with dpg.window(tag="Over Time Window", width=SCREEN_WIDTH, height=SCREEN_HEIGHT, show=False, no_collapse=True, no_title_bar=True, no_close=True, no_move=True):
        dpg.add_text("You have Selected Overtime")
        dpg.add_button(label="BACK", pos=[SCREEN_WIDTH//2-70, SCREEN_HEIGHT-100], callback=lambda: change_window("Digital Clock", "Over Time Window"))

    with dpg.window(tag="Digital Clock", width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        dpg.add_spacer(height=20)
        dpg.bind_font(default_font)
        msg = dpg.add_text(message, tag="message", pos=[SCREEN_WIDTH//2 - 300, 230])
        dpg.bind_item_font(msg, medium_font)

        with dpg.group():
            dpg.add_text("12:00:00 PM", tag="clock_label", pos=(SCREEN_WIDTH//2 - 300, 50))
            dpg.bind_item_font("clock_label", bigfont)
        with dpg.group():
            dpg.add_button(label="Log Overtime", callback=on_log_overtime, width=300, height=80, pos=(SCREEN_WIDTH//2 - 160, 360))
            dpg.add_button(label="Medical Leave", callback=on_medical_leave, width=300, height=80, pos=(20, SCREEN_HEIGHT - 140))
            dpg.add_button(label="Work Leave", callback=on_work_leave, width=300, height=80, pos=(SCREEN_WIDTH - 340, SCREEN_HEIGHT - 140))  
        
        
    dpg.create_viewport(title='Digital Clock Application', width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    threading.Thread(target=nfc_reader, daemon=True).start()

    # dpg.set_viewport_pos([100, 100])
    dpg.set_primary_window("Digital Clock", True)
    # dpg.render_dearpygui_frame()
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        check_nfc_queue()
        update()


    dpg.destroy_context()

if __name__ == "__main__":
    main()