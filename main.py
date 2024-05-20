import time
import dearpygui.dearpygui as dpg

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

def update_time():
    current_time = time.strftime("%I:%M:%S %p")
    dpg.set_value("clock_label", current_time)

def on_medical_leave():
    print("Medical Leave button clicked")

def on_work_leave():
    print("Work Leave button clicked")

def on_log_overtime():
    print("Log Overtime button clicked")

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
        default_font = dpg.add_font("font.ttf", 20)
        bigfont = dpg.add_additional_font("font.ttf", 100)
    with dpg.window(tag="Digital Clock", width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        dpg.add_spacer(height=20)
        with dpg.group():
            dpg.bind_font(bigfont)
            dpg.add_text("12:00:00 PM", tag="clock_label", pos=(SCREEN_WIDTH//2 - 100, 50))
        
        with dpg.group():
            dpg.add_button(label="Medical Leave", callback=on_medical_leave, width=200, height=50, pos=(SCREEN_WIDTH//2 - 100, 150))
            dpg.add_button(label="Work Leave", callback=on_work_leave, width=200, height=50, pos=(SCREEN_WIDTH//2 - 100, 220))
            dpg.add_button(label="Log Overtime", callback=on_log_overtime, width=200, height=50, pos=(SCREEN_WIDTH//2 - 100, 290))
            dpg.bind_font(default_font)

    dpg.create_viewport(title='Digital Clock Application', width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Set up a timer to update the clock every second
    dpg.set_frame_callback(1, update_time)
    dpg.set_viewport_resize_callback(lambda sender, app_data: dpg.configure_item("clock_label", pos=(dpg.get_viewport_client_width()//2 - 70, 50)))

    dpg.set_viewport_pos([100, 100])
    dpg.set_primary_window("Digital Clock", True)

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        update_time()

    dpg.destroy_context()

if __name__ == "__main__":
    main()