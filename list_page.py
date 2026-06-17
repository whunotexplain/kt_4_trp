"""
Страница «Список заказов»: таблица заказов с подсветкой строк,
кнопками удаления и переходом к редактированию по клику на строку.
"""
from functools import partial

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView,
)

import data

COLUMNS = [
    "№ заказа", "Дата оформления", "Дата выполнения", "Услуга", "Категория",
    "Описание", "Исполнитель", "Статус", "Стоимость", "Скидка, %",
    "Способ оплаты", "Комментарий клиента", "",
]

COL_ID = 0
COL_COST = 8
COL_PAYMENT = 10
COL_ACTIONS = 12


class OrdersListPage(QWidget):
    add_requested = pyqtSignal()
    edit_requested = pyqtSignal(str)   
    orders_changed = pyqtSignal()      

    def __init__(self, parent=None):
        super().__init__(parent)
        self.orders = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Список заказов")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Кликните по строке, чтобы отредактировать заказ"))
        top_bar.addStretch()
        add_btn = QPushButton("Добавить заказ")
        add_btn.clicked.connect(self.add_requested.emit)
        top_bar.addWidget(add_btn)
        layout.addLayout(top_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(COL_ID, 80)
        self.table.setColumnWidth(5, 220)   # описание
        self.table.setColumnWidth(11, 220)  # комментарий
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)

    def refresh(self):
        """Перечитывает CSV-файл и перерисовывает таблицу."""
        self.orders = data.load_orders()
        self._populate_table()

    def _populate_table(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.orders))

        for row, order in enumerate(self.orders):
            color = QColor(data.row_color(order))

            plain_values = {
                COL_ID: order.order_id,
                1: order.date_created,
                2: order.date_due,
                3: order.service_name,
                4: order.service_category,
                5: order.description,
                6: order.executor,
                7: order.status,
                9: f"{order.discount_percent:.0f}%",
            }
            for col, text in plain_values.items():
                item = QTableWidgetItem(text)
                item.setBackground(color)
                self.table.setItem(row, col, item)

            # Стоимость: перечёркнутая базовая цена (если есть скидка) + итоговая
            cost_label = QLabel()
            cost_label.setStyleSheet(f"background-color: {color.name()}; padding: 2px;")
            if order.discount_percent > 0 and order.final_cost < order.base_cost:
                cost_label.setText(
                    f"<span style='color:#C62828; text-decoration: line-through;'>"
                    f"{order.base_cost:.2f}</span>&nbsp;"
                    f"<span style='color:black; font-weight:bold;'>{order.final_cost:.2f}</span>"
                )
            else:
                cost_label.setText(f"<span style='color:black;'>{order.final_cost:.2f}</span>")
            self.table.setCellWidget(row, COL_COST, cost_label)

            # Способ оплаты + маркер «При получении»
            payment_text = order.payment_method
            if order.payment_method == "При получении":
                payment_text += f"  {data.PAYMENT_ON_DELIVERY_MARK}"
            payment_item = QTableWidgetItem(payment_text)
            payment_item.setBackground(color)
            self.table.setItem(row, COL_PAYMENT, payment_item)

            # Кнопка удаления
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(partial(self._on_delete_clicked, order.order_id))
            self.table.setCellWidget(row, COL_ACTIONS, delete_btn)

        self.table.resizeRowsToContents()

    def _on_cell_clicked(self, row, column):
        if column == COL_ACTIONS:
            return
        order_id = self.table.item(row, COL_ID).text()
        self.edit_requested.emit(order_id)

    def _on_delete_clicked(self, order_id):
        reply = QMessageBox.question(
            self, "Удаление заказа",
            f"Удалить заказ {order_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        orders = data.load_orders()
        orders = [o for o in orders if o.order_id != order_id]
        data.save_orders(orders)
        self.refresh()
