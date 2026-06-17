"""
Учёт заказов в интернет-магазине услуг.
Точка входа в приложение: главное окно со стеком из двух страниц
(список заказов и форма добавления/редактирования).
"""
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

import data
from list_page import OrdersListPage
from form_page import OrderFormPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учёт заказов")
        self.resize(1200, 650)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.list_page = OrdersListPage()
        self.form_page = OrderFormPage()

        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.form_page)

        self.list_page.add_requested.connect(self.show_add_form)
        self.list_page.edit_requested.connect(self.show_edit_form)
        self.form_page.saved.connect(self.show_list)
        self.form_page.back_requested.connect(self.show_list)

        self.show_list()

    def show_list(self):
        self.list_page.refresh()
        self.stack.setCurrentWidget(self.list_page)

    def show_add_form(self):
        self.form_page.set_order(None)
        self.stack.setCurrentWidget(self.form_page)

    def show_edit_form(self, order_id: str):
        orders = data.load_orders()
        order = next((o for o in orders if o.order_id == order_id), None)
        if order is not None:
            self.form_page.set_order(order)
            self.stack.setCurrentWidget(self.form_page)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
