import sqlite3
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QWidget,
    QDialog, QLineEdit, QListWidget,
    QVBoxLayout, QLabel, QHBoxLayout, QFileDialog,
    QPushButton, QMessageBox, QTextEdit,
    QTableWidget, QComboBox, QHeaderView,
    QTableWidgetItem, QAbstractItemView, QSizePolicy
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
import os
import csv

if getattr(sys, "frozen", False): # без этого у меня приложение не запускается(
    exe_dir = os.path.dirname(sys.executable)
    if exe_dir.endswith("Contents/MacOS"):
        exe_dir = os.path.dirname(os.path.dirname(os.path.dirname(exe_dir)))
    os.chdir(exe_dir) 


class RecipeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect('My_Recipes.db')
        self.cursor = self.con.cursor()
        self.current_recipe_name = None
        self.initUI()
        self.list_widget.itemClicked.connect(self.show_recipe_details)

    def initUI(self):
        self.setWindowTitle("Мои рецепты")
        self.setGeometry(100, 100, 800, 600)
        app.setWindowIcon(QIcon("Images/icon.png"))

        self.menuBar().setNativeMenuBar(False)
        menu_bar = self.menuBar()
        self.statusbar = self.statusBar()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Меню
        file_menu = menu_bar.addMenu("Файл")
        file_menu.addAction("Экспорт в CSV").triggered.connect(self.export_csv)
        file_menu.addAction("Выход").triggered.connect(self.closer)

        edit_menu = menu_bar.addMenu("Категории")
        edit_menu.addAction("Завтраки").triggered.connect(self.breakfast_click)
        edit_menu.addAction("Супы").triggered.connect(self.soup_click)
        edit_menu.addAction("Вторые блюда").triggered.connect(self.second_click)
        edit_menu.addAction("Салаты").triggered.connect(self.salad_click)
        edit_menu.addAction("Напитки").triggered.connect(self.drink_click)

        # Панель инструментов
        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(40, 40))
        actions = [
            ("Images/breakfast.png", "Завтраки", self.breakfast_click),
            ("Images/soup.png", "Супы", self.soup_click),
            ("Images/second.png", "Вторые блюда", self.second_click),
            ("Images/salad.png", "Салаты", self.salad_click),
            ("Images/drink.png", "Напитки", self.drink_click)
        ]

        for icon_name, text, method in actions:
            icon = QIcon(icon_name)
            action = QAction(icon, text, self)
            action.triggered.connect(method)
            toolbar.addAction(action)

        toolbar.addSeparator()

        favorite_icon = QIcon("Images/heart.png")
        favorite_action = QAction(favorite_icon, "Избранное", self)
        favorite_action.triggered.connect(self.favorite_click)
        toolbar.addAction(favorite_action)

        toolbar.addSeparator()

        add_icon = QIcon("Images/plus.png")
        add_recipe_action = QAction(add_icon, "Добавить рецепт", self)
        add_recipe_action.triggered.connect(self.add_recipe_click)
        toolbar.addAction(add_recipe_action)

        # Действия над рецептом
        self.toolbar_2 = QToolBar("Действия над рецептом")
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.toolbar_2)
        self.toolbar_2.setMovable(False)
        self.toolbar_2.setFloatable(False)
        self.toolbar_2.hide()

        self.back_button = QAction("Назад к списку", self)
        self.back_button.triggered.connect(self.show_recipe_details)

        self.add_button = QAction("Редактировать", self)
        self.add_button.triggered.connect(self.edit_recipe_click)

        self.delete_button = QAction("Удалить", self)
        self.delete_button.triggered.connect(self.delete_recipe)

        self.fav_button = QAction("В избранное", self)
        self.fav_button.triggered.connect(self.favorite)

        actions_2 = [self.back_button, self.add_button, self.delete_button, self.fav_button]

        for action in actions_2:
            widget = QWidget()
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.toolbar_2.addWidget(widget)
            self.toolbar_2.addAction(action)

        widget_2 = QWidget()
        widget_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar_2.addWidget(widget_2)

        self.list_widget = QListWidget(self)
        self.main_layout.addWidget(self.list_widget)

        self.recipe_title = QLabel()
        self.recipe_title.hide()
        self.main_layout.addWidget(self.recipe_title)

        self.ing_table = QTableWidget()
        self.ing_table.setColumnCount(2)
        self.ing_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ing_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ing_table.hide()
        self.main_layout.addWidget(self.ing_table)

        self.method_label = QLabel()
        self.method_label.hide()
        self.main_layout.addWidget(self.method_label)

    def favorite_click(self):
        self.recipe_title.hide()
        self.ing_table.hide()
        self.method_label.hide()
        self.toolbar_2.hide()
        self.list_widget.show()
        self.list_widget.clear()

        self.cursor.execute("SELECT name FROM Recipes WHERE is_favorite = 1")
        rows = self.cursor.fetchall()

        for row in rows:
            self.list_widget.addItem(row[0])

        self.statusbar.showMessage("Выбрано: Избранное")

    def breakfast_click(self):
        self.recipe_title.hide()
        self.ing_table.hide()
        self.method_label.hide()
        self.toolbar_2.hide()
        self.list_widget.show()
        self.cursor.execute("""
            SELECT name FROM Recipes 
            WHERE category_id = (
                SELECT id FROM Categories 
                WHERE id = 1
            )
        """)
        rows = self.cursor.fetchall()

        self.list_widget.clear()
        for row in rows:
            self.list_widget.addItem(row[0])
        self.statusbar.showMessage("Выбрано: Завтраки")

    def soup_click(self):
        self.recipe_title.hide()
        self.ing_table.hide()
        self.method_label.hide()
        self.toolbar_2.hide()
        self.list_widget.show()
        self.cursor.execute("""
            SELECT name FROM Recipes 
            WHERE category_id = (
                SELECT id FROM Categories 
                WHERE id = 2
            )
        """)
        rows = self.cursor.fetchall()

        self.list_widget.clear()
        for row in rows:
            self.list_widget.addItem(row[0])
        self.statusbar.showMessage("Выбрано: Супы")

    def second_click(self):
        self.recipe_title.hide()
        self.ing_table.hide()
        self.method_label.hide()
        self.toolbar_2.hide()
        self.list_widget.show()
        self.cursor.execute("""
            SELECT name FROM Recipes 
            WHERE category_id = (
                SELECT id FROM Categories 
                WHERE id = 3
            )
        """)
        rows = self.cursor.fetchall()

        self.list_widget.clear()
        for row in rows:
            self.list_widget.addItem(row[0])
        self.statusbar.showMessage("Выбрано: Вторые блюда")

    def salad_click(self):
        self.recipe_title.hide()
        self.ing_table.hide()
        self.method_label.hide()
        self.toolbar_2.hide()
        self.list_widget.show()
        self.cursor.execute("""
            SELECT name FROM Recipes 
            WHERE category_id = (
                SELECT id FROM Categories 
                WHERE id = 4
            )
        """)
        rows = self.cursor.fetchall()

        self.list_widget.clear()
        for row in rows:
            self.list_widget.addItem(row[0])
        self.statusbar.showMessage("Выбрано: Салаты")

    def drink_click(self):
        self.recipe_title.hide()
        self.ing_table.hide()
        self.method_label.hide()
        self.toolbar_2.hide()
        self.list_widget.show()
        self.cursor.execute("""
            SELECT name FROM Recipes 
            WHERE category_id = (
                SELECT id FROM Categories 
                WHERE id = 5
            )
        """)
        rows = self.cursor.fetchall()

        self.list_widget.clear()
        for row in rows:
            self.list_widget.addItem(row[0])
        self.statusbar.showMessage("Выбрано: Напитки")

    def add_recipe_click(self):
        dialog = AddRecipe(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.statusbar.showMessage("Рецепт успешно добавлен!")
        else:
            self.statusbar.showMessage("Добавление отменено")

    def show_recipe_details(self, item=None):
        if self.toolbar_2.isVisible():
            self.recipe_title.hide()
            self.ing_table.hide()
            self.method_label.hide()
            self.toolbar_2.hide()
            self.list_widget.show()
            self.list_widget.clear()
            self.cursor.execute("SELECT name FROM Recipes")
            rows = self.cursor.fetchall()
            for row in rows:
                self.list_widget.addItem(row[0])
            self.statusbar.showMessage("Все рецепты")
            return

        if item is None:
            return

        self.list_widget.hide()
        recipe_name = item.text()

        self.cursor.execute(
            """SELECT name, ingredients, method, is_favorite 
            FROM Recipes WHERE name = ?""", (recipe_name,)
        )
        recipe = self.cursor.fetchone()

        name, ingredients, method, is_fav = recipe

        self.current_recipe_name = name

        self.recipe_title.setText(f"<h2>{name}</h2>")
        self.recipe_title.show()

        self.ing_table.clear()
        self.ing_table.setRowCount(0)
        self.ing_table.setColumnCount(2)
        self.ing_table.setHorizontalHeaderLabels(["Ингредиент", "Количество"])
        self.ing_table.horizontalHeader().setVisible(True)
        self.ing_table.show()

        sp = [el.strip() for el in ingredients.split("#")]
        ing_list = []
        for i in range(0, len(sp), 2):
            if i + 1 < len(sp):
                ing_list.append((sp[i], sp[i + 1]))
            else:
                ing_list.append((sp[i], ""))

        self.ing_table.setRowCount(len(ing_list))
        for i, (name_part, qty_part) in enumerate(ing_list):
            self.ing_table.setItem(i, 0, QTableWidgetItem(name_part))
            self.ing_table.setItem(i, 1, QTableWidgetItem(qty_part))

        self.method_label.setText(f"<b>Способ приготовления:</b><br>{method}")
        self.method_label.setWordWrap(True)
        self.method_label.show()

        if is_fav == 1:
            self.fav_button.setText("Удалить из избранного")
        else:
            self.fav_button.setText("Добавить в избранное")

        self.toolbar_2.show()

        self.statusbar.showMessage(f"Рецепт: {name}")

    def edit_recipe_click(self):
        if not self.current_recipe_name:
            return

        self.cursor.execute("""
            SELECT name, category_id, ingredients, method, is_favorite
            FROM Recipes WHERE name = ?
        """, (self.current_recipe_name,))
        recipe = self.cursor.fetchone()
        if not recipe:
            QMessageBox.warning(self, "Ошибка", "Рецепт не найден!")
            return

        name, category_id, ingredients, method, is_fav = recipe

        self.cursor.execute("SELECT name FROM Categories WHERE id = ?", (category_id,))
        category_row = self.cursor.fetchone()
        category_name = category_row[0] if category_row else ""

        ing_list = []
        if ingredients:
            parts = ingredients.split("#")
            for i in range(0, len(parts), 2):
                ing = parts[i]
                qty = parts[i + 1] if i + 1 < len(parts) else ""
                ing_list.append(f"{ing} - {qty}")

        dialog = AddRecipe(self)
        dialog.name_edit.setText(name)
        dialog.category_combo.setCurrentText(category_name)
        dialog.method_edit.setPlainText(method)
        dialog.ingredients_list.clear()
        for item_text in ing_list:
            dialog.ingredients_list.addItem(item_text)
        dialog.is_editing = True
        dialog.original_name = self.current_recipe_name

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.name_edit.text()
            self.current_recipe_name = new_name

            self.cursor.execute("""
                SELECT name, ingredients, method, is_favorite
                FROM Recipes WHERE name = ?
            """, (new_name,))
            recipe = self.cursor.fetchone()

            if recipe:
                name, ingredients, method, is_fav = recipe

                self.recipe_title.setText(f"<h2>{name}</h2>")

                self.ing_table.clear()
                self.ing_table.setRowCount(0)
                self.ing_table.setColumnCount(2)
                self.ing_table.setHorizontalHeaderLabels(["Ингредиент", "Количество"])

                sp = [el.strip() for el in ingredients.split("#")]
                ing_rows = []
                for i in range(0, len(sp), 2):
                    if i + 1 < len(sp):
                        ing_rows.append((sp[i], sp[i + 1]))
                    else:
                        ing_rows.append((sp[i], ""))

                self.ing_table.setRowCount(len(ing_rows))
                for i, (n, q) in enumerate(ing_rows):
                    self.ing_table.setItem(i, 0, QTableWidgetItem(n))
                    self.ing_table.setItem(i, 1, QTableWidgetItem(q))

                self.method_label.setText(f"<b>Способ приготовления:</b><br>{method}")

                if is_fav == 1:
                    self.fav_button.setText("Удалить из избранного")
                else:
                    self.fav_button.setText("Добавить в избранное")

            self.statusbar.showMessage("Рецепт успешно обновлён!")

    def favorite(self):
        recipe_name = self.current_recipe_name
        if not recipe_name:
            return

        self.cursor.execute("""
            SELECT is_favorite 
            FROM Recipes 
            WHERE name = ?
        """, (recipe_name,))
        result = self.cursor.fetchone()
        if not result:
            return
        status = result[0]
        new_status = 1 if status == 0 else 0

        self.cursor.execute("""
            UPDATE Recipes 
            SET is_favorite = ? 
            WHERE name = ?
        """, (new_status, recipe_name))
        self.con.commit()

        if new_status == 1:
            self.fav_button.setText("Удалить из избранного")
            self.statusbar.showMessage(f'Рецепт "{recipe_name}" добавлен в избранное!')
        else:
            self.fav_button.setText("Добавить в избранное")
            self.statusbar.showMessage(f'Рецепт "{recipe_name}" удален из избранного!')

    def delete_recipe(self):
        recipe_name = self.current_recipe_name
        message = QMessageBox()
        message.setWindowTitle("Подтвердите удаление")
        message.setText(f'Вы точно хотите удалить рецепт "{recipe_name}"?')
        message.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message.button(QMessageBox.StandardButton.No).setText('Нет')
        message.button(QMessageBox.StandardButton.Yes).setText('Да')
        message.setDefaultButton(QMessageBox.StandardButton.No)
        message.setIcon(QMessageBox.Icon.Question)

        if message.exec() == QMessageBox.StandardButton.No:
            self.statusbar.showMessage('Удаление отменено')
        else:
            self.cursor.execute("""
            DELETE FROM Recipes 
            WHERE name = ?
            """, (recipe_name,))
            self.con.commit()
            self.statusbar.showMessage(f'Рецепт "{recipe_name}" успешно удален!')
            self.show_recipe_details()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить рецепты", "recipes.csv", "CSV файлы (*.csv)"
        )
        if not path:
            return

        self.cursor.execute("""
            SELECT Recipes.name, Categories.name, Recipes.ingredients,
                   Recipes.method, Recipes.is_favorite
            FROM Recipes JOIN Categories ON Recipes.category_id = Categories.id
        """)
        rows = self.cursor.fetchall()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Название", "Категория", "Ингредиенты", "Способ приготовления", "В избранном"])

            for name_rec, categ, ingredients, method, is_fav in rows:
                sp = [el.strip() for el in ingredients.split("#")]
                ing_text = []
                for i in range(0, len(sp), 2):
                    if i + 1 < len(sp):
                        ing_text.append(f"{sp[i]} - {sp[i + 1]}")
                    else:
                        ing_text.append(sp[i])
                writer.writerow([name_rec, categ, "; ".join(ing_text), method, "да" if is_fav == 1 else "нет"])
        self.statusbar.showMessage(f"Экспортировано в {path}")

    def closer(self):
        self.con.close()
        self.close()


class AddIngredient(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить ингредиент")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        ingredient_layout = QHBoxLayout()
        ingredient_layout.addWidget(QLabel("Ингредиент:"))
        self.ingredient_edit = QLineEdit()
        ingredient_layout.addWidget(self.ingredient_edit)
        layout.addLayout(ingredient_layout)

        kol_layout = QHBoxLayout()
        kol_layout.addWidget(QLabel("Количество:"))
        self.kol_edit = QLineEdit()
        kol_layout.addWidget(self.kol_edit)
        layout.addLayout(kol_layout)

        self.save_button = QPushButton("Добавить")
        self.save_button.clicked.connect(self.accept)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def get_ingredient(self):
        return self.ingredient_edit.text().strip()

    def get_quantity(self):
        return self.kol_edit.text().strip()


class AddRecipe(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить рецепт")
        self.setFixedWidth(400)
        layout = QVBoxLayout()

        self.name_label = QLabel("Название рецепта:")
        layout.addWidget(self.name_label)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        self.category_label = QLabel("Категория:")
        layout.addWidget(self.category_label)
        self.category_combo = QComboBox()
        layout.addWidget(self.category_combo)

        self.parent().cursor.execute("SELECT name FROM Categories")
        rows = self.parent().cursor.fetchall()
        for row in rows:
            self.category_combo.addItem(row[0])

        self.ingredients_list = QListWidget()
        layout.addWidget(self.ingredients_list)

        self.add_ingredient_button = QPushButton("Добавить ингредиент")
        self.add_ingredient_button.clicked.connect(self.add_ingredient)
        layout.addWidget(self.add_ingredient_button)

        self.del_ingredient_button = QPushButton("Удалить ингредиент")
        self.del_ingredient_button.clicked.connect(self.del_ingredient)
        layout.addWidget(self.del_ingredient_button)

        self.method_label = QLabel("Способ приготовления:")
        layout.addWidget(self.method_label)
        self.method_edit = QTextEdit()
        layout.addWidget(self.method_edit)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_recipe)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.is_editing = False  # по умолчанию — обычное добавление
        self.original_name = None

    def add_ingredient(self):
        dialog = AddIngredient(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ingredient = dialog.get_ingredient()
            quantity = dialog.get_quantity()
            if ingredient:
                self.ingredients_list.addItem(f"{ingredient}:  {quantity}")

    def del_ingredient(self):
        selected = self.ingredients_list.currentItem()
        if selected is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите ингредиент из списка")
            return
        row = self.ingredients_list.row(selected)
        self.ingredients_list.takeItem(row)

    def save_recipe(self):
        name = self.name_edit.text()
        category = self.category_combo.currentText()
        method = self.method_edit.toPlainText()

        parts = []
        for index in range(self.ingredients_list.count()):
            item = self.ingredients_list.item(index)
            if ":  " in item.text():
                ingredient, quantity = item.text().split(":  ", 1)
            else:
                ingredient, quantity = item.text(), ""
            parts.append(ingredient)
            parts.append(quantity)

        ingredients_str = "#".join(parts)

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название рецепта")
            return

        self.parent().cursor.execute("""
            SELECT id FROM Categories 
            WHERE name = ?
        """, (category,))
        category_id = self.parent().cursor.fetchone()

        category_id = category_id[0]

        if self.is_editing and self.original_name:
            self.parent().cursor.execute("""
                UPDATE Recipes
                SET name = ?, category_id = ?, ingredients = ?, method = ?
                WHERE name = ?
            """, (name, category_id, ingredients_str, method, self.original_name))
            msg = "Рецепт успешно обновлён!"
        else:
            self.parent().cursor.execute("""
                INSERT INTO Recipes (name, category_id, ingredients, method, is_favorite)
                VALUES (?, ?, ?, ?, 0)
            """, (name, category_id, ingredients_str, method))
            msg = "Рецепт успешно добавлен!"

        self.parent().con.commit()

        QMessageBox.information(self, "Успех", msg)
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecipeApp()
    ex.show()
    sys.exit(app.exec())
