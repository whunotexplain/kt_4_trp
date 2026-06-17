"""
Страница «Добавление / Редактирование заказа».
Одна и та же форма используется и для добавления, и для редактирования —
режим задаётся методом set_order().
"""
from PyQt6.QtCore import pyqtSignal, QDate, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit, QPushButton,
    QMessageBox,
)

import data


class OrderFormPage(QWidget):
    saved = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editing_order_id = None  # None => режим добавления
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("Добавление заказа")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.title_label)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # № заказа — только для чтения, скрыт при добавлении
        self.order_id_row_label = QLabel("№ заказа")
        self.order_id_edit = QLineEdit()
        self.order_id_edit.setReadOnly(True)
        form.addRow(self.order_id_row_label, self.order_id_edit)

        self.date_created_edit = QDateEdit()
        self.date_created_edit.setCalendarPopup(True)
        self.date_created_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Дата оформления", self.date_created_edit)

        self.date_due_edit = QDateEdit()
        self.date_due_edit.setCalendarPopup(True)
        self.date_due_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Дата выполнения", self.date_due_edit)

        self.service_name_edit = QLineEdit()
        form.addRow("Наименование услуги", self.service_name_edit)

        self.category_combo = QComboBox()
        self.category_combo.addItems(data.CATEGORIES)
        form.addRow("Категория услуги", self.category_combo)

        self.description_edit = QTextEdit()
        self.description_edit.setFixedHeight(70)
        form.addRow("Описание услуги", self.description_edit)

        self.executor_combo = QComboBox()
        self.executor_combo.addItems(data.EXECUTORS)
        form.addRow("Исполнитель", self.executor_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(data.STATUSES)
        form.addRow("Статус заказа", self.status_combo)

        self.base_cost_spin = QDoubleSpinBox()
        self.base_cost_spin.setRange(0, 10_000_000)
        self.base_cost_spin.setDecimals(2)
        self.base_cost_spin.setSuffix(" руб.")
        self.base_cost_spin.valueChanged.connect(self._recalc_final_cost)
        form.addRow("Базовая стоимость", self.base_cost_spin)

        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setSuffix(" %")
        self.discount_spin.valueChanged.connect(self._recalc_final_cost)
        form.addRow("Размер скидки", self.discount_spin)

        self.final_cost_spin = QDoubleSpinBox()
        self.final_cost_spin.setRange(0, 10_000_000)
        self.final_cost_spin.setDecimals(2)
        self.final_cost_spin.setSuffix(" руб.")
        form.addRow("Итоговая стоимость", self.final_cost_spin)

        self.payment_combo = QComboBox()
        self.payment_combo.addItems(data.PAYMENT_METHODS)
        form.addRow("Способ оплаты", self.payment_combo)

        self.comment_edit = QTextEdit()
        self.comment_edit.setFixedHeight(70)
        form.addRow("Комментарий клиента", self.comment_edit)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QHBoxLayout()
        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.back_requested.emit)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._on_save)
        buttons.addWidget(back_btn)
        buttons.addStretch()
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

    def _recalc_final_cost(self):
        """Итоговая стоимость пересчитывается автоматически, но доступна для правки.
        Максимум поля ограничен базовой стоимостью — итоговая не может её превышать."""
        base = self.base_cost_spin.value()
        discount = self.discount_spin.value()
        self.final_cost_spin.setMaximum(max(base, 0))
        self.final_cost_spin.setValue(round(base * (1 - discount / 100), 2))

    def set_order(self, order):
        """order=None -> режим добавления нового заказа.
        order=Order -> режим редактирования существующего."""
        if order is None:
            self.editing_order_id = None
            self.title_label.setText("Добавление заказа")
            self.order_id_row_label.setVisible(False)
            self.order_id_edit.setVisible(False)
            self.order_id_edit.clear()

            today = QDate.currentDate()
            self.date_created_edit.setDate(today)
            self.date_due_edit.setDate(today)
            self.service_name_edit.clear()
            self.category_combo.setCurrentIndex(0)
            self.description_edit.clear()
            self.executor_combo.setCurrentIndex(0)
            self.status_combo.setCurrentText("Новый")
            self.base_cost_spin.setValue(0)
            self.discount_spin.setValue(0)
            self.payment_combo.setCurrentIndex(0)
            self.comment_edit.clear()
            self._recalc_final_cost()
        else:
            self.editing_order_id = order.order_id
            self.title_label.setText("Редактирование заказа")
            self.order_id_row_label.setVisible(True)
            self.order_id_edit.setVisible(True)
            self.order_id_edit.setText(order.order_id)

            self.date_created_edit.setDate(QDate.fromString(order.date_created, "yyyy-MM-dd"))
            self.date_due_edit.setDate(QDate.fromString(order.date_due, "yyyy-MM-dd"))
            self.service_name_edit.setText(order.service_name)
            self.category_combo.setCurrentText(order.service_category)
            self.description_edit.setPlainText(order.description)
            if order.executor not in data.EXECUTORS:
                self.executor_combo.addItem(order.executor)
            self.executor_combo.setCurrentText(order.executor)
            self.status_combo.setCurrentText(order.status)
            self.base_cost_spin.setValue(order.base_cost)
            self.discount_spin.setValue(int(order.discount_percent))
            self.final_cost_spin.setMaximum(max(order.base_cost, order.final_cost))
            self.final_cost_spin.setValue(order.final_cost)
            self.payment_combo.setCurrentText(order.payment_method)
            self.comment_edit.setPlainText(order.client_comment)

    def _on_save(self):
        # --- Валидация ---
        if not self.service_name_edit.text().strip():
            QMessageBox.warning(self, "Проверка данных", "Укажите наименование услуги.")
            return

        if self.date_due_edit.date() < self.date_created_edit.date():
            QMessageBox.warning(
                self, "Проверка данных",
                "Дата выполнения не может быть раньше даты оформления.",
            )
            return

        base_cost = self.base_cost_spin.value()
        final_cost = self.final_cost_spin.value()
        if final_cost > base_cost:
            QMessageBox.warning(
                self, "Проверка данных",
                "Итоговая стоимость не может быть больше базовой.",
            )
            return

        orders = data.load_orders()

        if self.editing_order_id is None:
            order_id = data.generate_order_id(orders)
            new_order = data.Order(
                order_id=order_id,
                date_created=self.date_created_edit.date().toString("yyyy-MM-dd"),
                date_due=self.date_due_edit.date().toString("yyyy-MM-dd"),
                service_name=self.service_name_edit.text().strip(),
                service_category=self.category_combo.currentText(),
                description=self.description_edit.toPlainText().strip(),
                executor=self.executor_combo.currentText(),
                status=self.status_combo.currentText(),
                base_cost=base_cost,
                discount_percent=self.discount_spin.value(),
                final_cost=final_cost,
                payment_method=self.payment_combo.currentText(),
                client_comment=self.comment_edit.toPlainText().strip(),
            )
            orders.append(new_order)
        else:
            for o in orders:
                if o.order_id == self.editing_order_id:
                    o.date_created = self.date_created_edit.date().toString("yyyy-MM-dd")
                    o.date_due = self.date_due_edit.date().toString("yyyy-MM-dd")
                    o.service_name = self.service_name_edit.text().strip()
                    o.service_category = self.category_combo.currentText()
                    o.description = self.description_edit.toPlainText().strip()
                    o.executor = self.executor_combo.currentText()
                    o.status = self.status_combo.currentText()
                    o.base_cost = base_cost
                    o.discount_percent = self.discount_spin.value()
                    o.final_cost = final_cost
                    o.payment_method = self.payment_combo.currentText()
                    o.client_comment = self.comment_edit.toPlainText().strip()
                    break

        data.save_orders(orders)
        self.saved.emit()
