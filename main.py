import time
import dearpygui.dearpygui as dpg
import queue
import threading
from datetime import datetime, timedelta
import pygame
from api import get_employee_schedule

pygame.init()

access_denied = pygame.mixer.Sound("AccessDenied.mp3")
access_granded = pygame.mixer.Sound("AccessGranted.mp3")

nfc_queue = queue.Queue()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
users_times = {1234: datetime.now()}

API_URL = "http://127.0.0.1:8000/api/get-schedule/"

def nfc_reader():
    while True:
        uid = int(input("uid: "))
        nfc_queue.put(uid)


def update_time():
    current_time = time.strftime("%I:%M:%S %p")
    dpg.set_value("clock_label", current_time)

def update_text():
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
    print("Log Overtime button clicked")

def check_nfc_queue():
    global message, last_time
    while not nfc_queue.empty():
        last_time = datetime.now()
        card_uid = nfc_queue.get()
        res = get_employee_schedule(API_URL, card_uid)
        if res:
            current_time = datetime.now()
            starttime = res["starttime"]
            endtime = res["endtime"]
            if abs(starttime - current_time) < timedelta(hours=2) or abs(endtime - current_time) < timedelta(hours=2):
                pass
            message = f"you came {(current_time - res["starttime"])} late."
            access_granded.play()
            message += "\nAccess Granted"
            return
        else:
            access_denied.play()
            message = "Access Denied"


message = ""
last_time = None

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

    dpg.set_viewport_pos([100, 100])
    dpg.set_primary_window("Digital Clock", True)

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        check_nfc_queue()
        update_time()
        update_text()

    dpg.destroy_context()

if __name__ == "__main__":
    main()