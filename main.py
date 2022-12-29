from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
import os, sys, kivy, kivymd
from kivy.resources import resource_add_path, resource_find
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from kivymd.uix.snackbar import Snackbar
from pyfirmata import Arduino
import sqlite3

Window.size = (414, 700)


class LoginScreen(Screen):
    login = ObjectProperty(None)
    password = ObjectProperty(None)

    def log_in(self):
        if self.login.text != "" and self.password.text != "":
            conn = sqlite3.connect('database_man-out-devs.db')
            c = conn.cursor()
            c.execute("SELECT login, password FROM users WHERE login=? AND password=?", (self.login.text, self.password.text))
            record = c.fetchone()

            if record:
                sm.current = "main_screen"
                self.reset()
            else:
                invalid_login()

            conn.commit()
            conn.close()

        else:
            invalid_form()

    def register_acc(self):
        self.reset()

    def reset(self):
        self.login.text = ""
        self.password.text = ""


class RegisterScreen(Screen):
    acc_name = ObjectProperty(None)
    login = ObjectProperty(None)
    password = ObjectProperty(None)

    def register_button(self):
        if self.acc_name.text != "" and self.login.text != "" and self.login.text.count("@") == 1 \
                and self.login.text.count(".") > 0:
            if self.password.text != "":
                conn = sqlite3.connect('database_man-out-devs.db')
                c = conn.cursor()
                temp = False
                try:
                    c.execute("INSERT INTO users (acc_name, login, password) VALUES (:acc_name, :login, :password)",
                                    {
                                      'acc_name': self.acc_name.text,
                                      'login': self.login.text,
                                      'password': self.password.text
                                    }
                              )
                except Exception:
                    temp = True

                if temp:
                    self.dialog_email_exist()
                else:
                    self.info_account_created()

                conn.commit()
                conn.close()

                self.reset()
            else:
                invalid_login()
        else:
            invalid_form()

    def log_in_button(self):
        self.reset()
        sm.current = "login_screen"

    # komunikat po poprawnym zalozeniu konta
    def info_account_created(self):
        self.snackbar = Snackbar(
            text="[color=#02d629]Konto zostało pomyślnie utworzone![/color]",
            bg_color=(1, 1, 1, .8),
            snackbar_y="5dp",
            )
        self.snackbar.open()

    # okno dialogowe z komunikatem o istnieniu adresu e-mail
    def dialog_email_exist(self):
        dialog = None
        if not dialog:
            dialog = MDDialog(
                title="Podany adres e-mail już istnieje.\nZaloguj się",
                radius=[10, 10, 10, 10])
        dialog.open()

    def reset(self):
        self.login.text = ""
        self.password.text = ""
        self.acc_name.text = ""


class MainScreen(Screen):
    pass


class ProfileScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class AddDeviceScreen(Screen):
    add_device = ObjectProperty(None)
    quantity_of_devices = ObjectProperty(None)

    def add_new_device(self):
        if self.ids.add_device.text != "" and self.ids.quantity_of_devices.text != "":
            conn = sqlite3.connect('database_man-out-devs.db')
            c = conn.cursor()
            if self.ids.quantity_of_devices.text > str(0):
                temp = False
                try:
                    c.execute("INSERT INTO devices (device, quantity) VALUES (:device, :quantity)",
                             {
                               'device': self.add_device.text,
                               'quantity': self.quantity_of_devices.text
                             }
                          )
                except Exception:
                    temp = True

                if temp:
                    self.dialog_device_exist()
                else:
                    self.info_device_added()

                conn.commit()
                conn.close()

                self.reset()
            else:
                invalid_data()
        else:
            invalid_form()

    # komunikat po poprawnym dodaniu urzadzenia
    def info_device_added(self):
        self.snackbar = Snackbar(
            text="[color=#000]Urządzenie zostało dodane![/color]",
            bg_color=(1, 1, 1, .8),
            snackbar_y="5dp",
            )
        self.snackbar.open()

    # okno dialogowe z komunikatem o istnieniu urzadzenia
    def dialog_device_exist(self):
        dialog = None
        if not dialog:
            dialog = MDDialog(
                title="Takie urządzenie zostało już dodane",
                radius=[10, 10, 10, 10])
        dialog.open()

    def reset(self):
        self.ids.add_device.text = ""
        self.ids.quantity_of_devices.text = ""


class SingleDeviceScreen(Screen):
    def on_save(self, instance, value, date_range):
        if not date_range:
            self.ids.date_label.text = "Nie wybrano zakresu dat!"
        else:
            self.ids.date_label.text = f'Wybrano zakres dat: {str(date_range[0])} - {str(date_range[-1])}'

    def get_time(self, instance, time):
        self.ids.time_label.text = str(time)

    def get_default_time(self, instance, time):
        self.ids.time_label.text = str(time)

    def on_cancel_date(self, instance, value):
        self.ids.date_label.text = "Nie wybrano żadnej daty!"

    def on_cancel_time(self, instance, value):
        self.ids.time_label.text = "Nie ustawiono czasu!"

    def show_date_picker(self):
        date_dialog = MDDatePicker(mode="range")
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel_date)
        date_dialog.open()

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_cancel=self.on_cancel_time, on_save=self.get_default_time, time=self.get_time)
        time_dialog.open()

    def save_device_options(self):
        pass


class WindowManager(ScreenManager):
    pass


# menu i elementy w menu
class ContentNavigationDrawer(BoxLayout):
    nav_drawer = ObjectProperty()


# popup'y
def invalid_login():
    pop = Popup(title='Błąd podczas logowania',
                background='atlas://data/images/defaulttheme/button')
    pop.open()


def invalid_form():
    pop = Popup(title='Pusty formularz',
                background='atlas://data/images/defaulttheme/button')
    pop.open()


def invalid_data():
    pop = Popup(title='Wprowadzono niepoprawne dane',
                background='atlas://data/images/defaulttheme/button')
    pop.open()


# ekrany
sm = WindowManager()
screens = [MainScreen(name="main_screen"), RegisterScreen(name="register_screen"), LoginScreen(name="login_screen"),
           ProfileScreen(name="profile_screen"), SettingsScreen(name="settings_screen"),
           AddDeviceScreen(name="add_device_screen"), SingleDeviceScreen(name="single_device_screen")]
for screen in screens:
    sm.add_widget(screen)

# ustawienia plytki Arduino
port = "COM3"
board = Arduino(port)
pin_13 = 13
pin_12 = 12
pin_11 = 11
pin_10 = 10
pin_9 = 9
pin_8 = 8
pin_7 = 7
pin_6 = 6
pin_5 = 5
pin_4 = 4
pin_3 = 3
pin_2 = 2


class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Man-out-devs"
        super().__init__(**kwargs)

    # przycisk dodaj/usun urzadzenia
    data = {
        'Dodaj urządzenie': 'plus-box-multiple',
        'Usuń urządzenie': 'delete',
    }

    # otwieranie widoku dodawania urzadzenia
    def callback(self, instance):
        if instance.icon == "plus-box-multiple":
            self.root.current = "add_device_screen"

        # usuniecie urzadzenia po oznaczeniu checkbox
        if instance.icon == "delete":
            if self.on_checkbox_active(checkbox="", value=True):
                pass

    # komunikat o usunieciu urzadzenia po oznaczeniu checkbox
    def on_checkbox_active(self, checkbox, value):
        if value:
            self.info_device_deleted()

    def info_device_deleted(self):
        self.snackbar = Snackbar(
            text="[color=#000]Urządzenie zostało usunięte[/color]",
            bg_color=(1, 1, 1, .8),
            snackbar_y="5dp",
            size_hint_x=.6
        )
        self.snackbar.open()

    # symulacja wlaczania/wylaczania urzadzenia na plytce Arduino
    def on_switch_active(self, switch, value):
        if value:
            board.digital[pin_13].write(1)
            board.digital[pin_12].write(0)
        else:
            board.digital[pin_12].write(1)
            board.digital[pin_13].write(0)

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.accent_palette = "BlueGray"

        # tworzenie bazy lub nawiazywanie polaczenia z istniejaca
        conn = sqlite3.connect('database_man-out-devs.db')

        # tworzenie kursora
        c = conn.cursor()

        # tworzenie tabeli
        try:
            c.execute("""CREATE TABLE if not exists users(
                                id integer PRIMARY KEY,
                                acc_name text,
                                login text unique,
                                password text)
                      """
                      )
            c.execute("""CREATE TABLE if not exists devices(
                                id integer PRIMARY KEY,
                                device text unique,
                                quantity number)
                      """
                      )
        except Exception as e:
            print("Tabela już istnieje -", e)

        # zapisanie zmian
        conn.commit()
        # zakonczenie polaczenia
        conn.close()

        self.root = Builder.load_file('interface.kv')


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()

