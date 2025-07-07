
import sys
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt

class TodoDatabase:
    def __init__(self, db_name="tasks.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                position INTEGER
            )
        """)
        self.conn.commit()

    def add_task(self, title, priority, category, position):
        self.conn.execute("INSERT INTO tasks (title, priority, category, position) VALUES (?, ?, ?, ?)",
                          (title, priority, category, position))
        self.conn.commit()

    def get_tasks(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, priority, category, position FROM tasks ORDER BY position ASC")
        return cur.fetchall()

    def delete_task(self, task_id):
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def update_position(self, task_id, position):
        self.conn.execute("UPDATE tasks SET position = ? WHERE id = ?", (position, task_id))
        self.conn.commit()


class TodoApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("todo_final.ui", self)
        self.setWindowTitle("مدیریت وظایف با رابط گرافیکی")

        self.db = TodoDatabase()
        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        self.priorityBox.addItems(["کم", "متوسط", "زیاد"])
        self.categoryBox.addItems(["عمومی", "کار", "شخصی", "یادآوری", "ایده"])
        self.filterPriority.addItem("همه اولویت‌ها")
        self.filterPriority.addItems(["کم", "متوسط", "زیاد"])
        self.filterCategory.addItem("همه دسته‌ها")
        self.filterCategory.addItems(["عمومی", "کار", "شخصی", "یادآوری", "ایده"])

        self.addButton.clicked.connect(self.add_task)
        self.searchInput.textChanged.connect(self.load_tasks)
        self.filterPriority.currentIndexChanged.connect(self.load_tasks)
        self.filterCategory.currentIndexChanged.connect(self.load_tasks)
        self.taskList.itemDoubleClicked.connect(self.delete_task)
        self.taskList.setDragDropMode(QtWidgets.QListWidget.InternalMove)
        self.taskList.model().rowsMoved.connect(self.save_new_positions)
        self.themeToggleButton.clicked.connect(self.toggle_theme)

        self.dark_mode = False

    def toggle_theme(self):
        if not self.dark_mode:
            self.setStyleSheet("QWidget { background-color: #2b2b2b; color: white; }")
            self.dark_mode = True
        else:
            self.setStyleSheet("")
            self.dark_mode = False

    def add_task(self):
        title = self.taskInput.text().strip()
        priority = self.priorityBox.currentText()
        category = self.categoryBox.currentText()
        position = self.taskList.count()
        if title:
            self.db.add_task(title, priority, category, position)
            self.taskInput.clear()
            self.load_tasks()

    def load_tasks(self):
        self.taskList.clear()
        keyword = self.searchInput.text().lower()
        sel_priority = self.filterPriority.currentText()
        sel_category = self.filterCategory.currentText()

        for task_id, title, priority, category, pos in self.db.get_tasks():
            if ((keyword in title.lower() or keyword in category.lower()) and
                (sel_priority == "همه اولویت‌ها" or sel_priority == priority) and
                (sel_category == "همه دسته‌ها" or sel_category == category)):
                item = QtWidgets.QListWidgetItem(f"{title} [{priority} | {category}]")
                item.setData(Qt.UserRole, task_id)
                if priority == "زیاد":
                    item.setForeground(Qt.red)
                elif priority == "متوسط":
                    item.setForeground(Qt.darkYellow)
                else:
                    item.setForeground(Qt.darkGreen)
                self.taskList.addItem(item)

    def delete_task(self, item):
        task_id = item.data(Qt.UserRole)
        reply = QtWidgets.QMessageBox.question(self, "حذف", "آیا این کار حذف شود؟",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.delete_task(task_id)
            self.load_tasks()

    def save_new_positions(self):
        for i in range(self.taskList.count()):
            item = self.taskList.item(i)
            task_id = item.data(Qt.UserRole)
            self.db.update_position(task_id, i)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())
