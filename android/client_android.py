from kivy.metrics import dp
from kivymd.uix.screen import MDScreen      # , ScreenManager
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDRectangleFlatIconButton
from kivy.core.window import Window

# Example: 360x640 (like a small Android phone screen)
Window.size = (360, 640)

import sys, os
# Go up one directory (from app/ to my_project/) and add to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_handler  # Ensure database handler is imported



class MenuButton(MDRectangleFlatIconButton):
    pass


class MenuScreen(MDScreen):
    pass


class CreditScreen(MDScreen):
    """
    Credit Screen to display credits in a table
    1. Show all credits
    2. Search credits by client name
    3. Refresh the table
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db_handler.Database()

    def show_credits(self):
        rows = self.db.dump_credits()
        self.add_table(rows)

    def add_table(self, rows):
        # Clear old table if it exists
        self.ids.credit_table_box.clear_widgets()
        
        # ID, Date, Client, Reste
        rows = [(str(row[0]), row[1], row[2], str(row[6])) for row in rows] # Adjust based on your table structure

        table = MDDataTable(
            size_hint=(1, 0.7),
            use_pagination=True,
            column_data=[
                ("ID", dp(10)),
                ("Date", dp(20)),
                ("Client", dp(40)),
                ("Credit", dp(30)),
            ],
            row_data=[row for row in rows],
        )        
        self.ids.credit_table_box.add_widget(table)
    
    def search_credit(self, search_word):
        search_word = f"%{search_word.strip()}%"
        if search_word == "":
            rows = self.db.dump_credits()
        else:
            rows = self.db.search_credits(search_word)
        self.add_table(rows)


class VersementScreen(MDScreen):
    def show_versements(self):
        print("Loading versements...")   # put your real logic here

    def search_versement(self, search_word):
        print(f"Searching versements for: {search_word}")


class CreditApp(MDApp):
    def build(self):
         # Enable dark mode
        self.theme_cls.theme_style = "Light"
        # Choose an accent color palette (blue, green, red, etc.)
        # palette 
        # ['Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal', 
        # 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray']
        self.theme_cls.primary_palette = "Indigo"

        # self.theme_cls.accent_palette = "Amber"
        # Optional: change accent hue (like "A400")
        # self.theme_cls.primary_hue = "500"
    
    def change_screen(self, screen_name, callback, direction="left"):
        sm = self.root
        sm.transition.direction = direction
        sm.current = screen_name

        # auto-call a method if screen has a matching "show_xxx"
        screen = sm.get_screen(screen_name)
        if hasattr(screen, callback):
            getattr(screen, callback)()
    

if __name__ == "__main__":
    CreditApp().run()