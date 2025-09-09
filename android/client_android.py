from kivy.metrics import dp
from kivymd.uix.screen import MDScreen      # , ScreenManager
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDRectangleFlatIconButton
from kivy.core.window import Window

# Example: 360x640 (like a small Android phone screen)
Window.size = (360, 600)

import requests
BASE_URL = "http://127.0.0.1:8000"  # ton API FastAPI


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

    def show_credits(self):
        """
        Charger les crédits depuis l'API et afficher dans un tableau
        """
        # self.ids.client_table_box.clear_widgets()
        try:
            resp = requests.get(f"{BASE_URL}/credits")
            self.all_data = resp.json()
        except Exception as e:
            self.all_data = []
            print("Erreur API:", e)
        else:
            self.build_table(self.all_data)

    def filter_credits(self, query):
        """
        Filtrer les crédits en fonction de la requête
        """
        # query = self.ids.search_credit_client.text
        if not hasattr(self, 'all_data'):
            return
        if query.strip() == "":
            filtered_data = self.all_data
        else:
            filtered_data = [d for d in self.all_data if query.lower() in d["client"].lower()]

        self.build_table(filtered_data)

    def build_table(self, data):
        """Charger les crédits depuis l'API et afficher dans un tableau"""

        self.ids.credit_table_box.clear_widgets()
        rows = [(d["id"], d["credit_date"], d["client"], f"{d['montant']:.2f}") for d in data]

        # Créer le tableau
        table = MDDataTable(
            size_hint=(1, 1),
            background_color_header=("#227093"),
            column_data=[
                ("ID", dp(10)),
                ("Date", dp(20)),
                ("Nom", dp(40)),
                ("Crédit", dp(30)),
            ],
            row_data=rows,
            use_pagination=True,
        )

        table.bind(on_row_press=self.on_row_press)
        # Vider le conteneur avant de recréer la table
        self.ids.credit_table_box.add_widget(table)

    def on_row_press(self, instance_table, instance_row):
        """
        Gérer l'événement de pression sur une ligne du tableau
        """
        print(f"Ligne sélectionnée: {instance_row}")
        try:
            start_index, end_index = instance_row.table.recycle_data[instance_row.index]["range"]
            credit_id = instance_row.table.recycle_data[start_index]
            client_name = instance_row.table.recycle_data[start_index + 2]
        except Exception as e:
            print("Erreur lors de la récupération de l'ID du crédit:", e)
            return
        else:
            print(f"ID du crédit sélectionné: {credit_id['text']}, Client: {client_name['text']}")


class VersementScreen(MDScreen):
    def show_versements(self):
        print("Loading versements...")   # put your real logic here

    def search_versement(self, search_word):
        print(f"Searching versements for: {search_word}")


class CreditApp(MDApp):
    def build(self):
        # Enable dark mode
        self.theme_cls.theme_style = "Dark"
        # Choose an accent color palette (blue, green, red, etc.)
        # palette
        # ['Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal',
        # 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray']
        self.theme_cls.primary_palette = "BlueGray"

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
