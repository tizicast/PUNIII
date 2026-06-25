from ui.login_ui import ventana_login
from main import main_menu


def main():
    ventana_login(on_success=main_menu)


if __name__ == "__main__":
    main()
