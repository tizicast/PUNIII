from ui.login_ui import ventana_login
from main import init_db, main_menu


def main():
    init_db()
    ventana_login(on_success=main_menu)


if __name__ == "__main__":
    main()
