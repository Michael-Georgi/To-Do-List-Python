import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QScrollArea, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import sys
import json

class EditTaskLabel(QLineEdit):
    editingDone = pyqtSignal()
    def __init__(self, text=""):
        super().__init__(text)
        self.setReadOnly(True)
        self.editing = False

    def mousePressEvent(self, event):
        if not self.editing:
            self.editing = True
            if self.isReadOnly():
                self.setReadOnly(False)
                self.setFocus()
                self.selectAll()
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        if self.editing:
            self.editing = False
            if not self.isReadOnly():
                self.setReadOnly(True)
                self.editingDone.emit()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if self.editing:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.editing = False
                self.setReadOnly(True)
                self.editingDone.emit()
        super().keyPressEvent(event)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List")
        self.task_count = 0
        
        # UI Creation
        self.title_label = QLabel("To-Do List", self)
        self.title_label.setObjectName("Title_Label")

        self.task_input_box = QLineEdit(self)
        self.task_input_box.setObjectName("Task_Input_Box")

        self.add_task_btn = QPushButton("ADD", self)
        self.add_task_btn.setObjectName("Add_Task_Btn")

        self.error_msg_label = QLabel(self)
        self.error_msg_label.setObjectName("Error_Msg_Label")

        self.no_tasks_label = QLabel("No Tasks Yet...", self)
        self.no_tasks_label.setObjectName("No_tasks_Label")

        self.clear_all_tasks = QPushButton("Clear All", self)
        self.clear_all_tasks.setObjectName("Clear_All_Tasks")

        self.task_counter_label = QLabel(self)
        self.task_counter_label.setObjectName("Task_Counter_Label")

        self.design_window()

        self.load_tasks()

    def save_tasks(self):
        tasks = []
        for item_pos in range(self.task_items_list.count()):
            item = self.task_items_list.itemAt(item_pos)
            layout = item.layout()
            if layout and layout.count() >= 2:
                checkbox = layout.itemAt(0).widget()
                label = layout.itemAt(1).widget()

                if checkbox and label:
                    tasks.append({
                    "text": label.text(),
                    "checked": checkbox.isChecked()
                    })
        
        with open("tasks.json", "w") as f:
            json.dump(tasks, f, indent=4)

    def load_tasks(self):
        try:
            if os.path.exists("tasks.json"):
                with open("tasks.json", "r") as f:

                    tasks = json.load(f)

                    for task in tasks:
                        self.add_task(task["text"], loading=True)
                        
                        layout = self.task_items_list.itemAt(self.task_items_list.count()-1)

                        if layout:
                            checkbox = layout.itemAt(0).widget()
                            checkbox.setChecked(task["checked"])

                    self.task_count = len(tasks)
                    self.task_counter_label.setText(f"{self.task_count} Tasks Remaining...")

        except (KeyError, json.decoder.JSONDecodeError, FileNotFoundError):
            tasks = []
            print("{Nothing To Load}")

    def design_window(self):
        # UI Vertical Layout
        self.setMinimumSize(400,400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label, alignment=Qt.AlignLeft)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        vbox.addLayout(header_layout)
        vbox.addWidget(self.error_msg_label, alignment=Qt.AlignHCenter)
        vbox.addWidget(self.task_counter_label)

        # UI Horizontal Layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.clear_all_tasks, alignment=Qt.AlignLeft)
        hbox.addWidget(self.task_input_box, stretch=1)
        hbox.addWidget(self.add_task_btn)
        hbox.setSpacing(4)
        hbox.setContentsMargins(0,0,0,0)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)

        # Scrolling Area
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout()
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_container.setLayout(self.task_layout)

        self.task_layout.addWidget(self.no_tasks_label, alignment=Qt.AlignCenter)


        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("Scroll_Area")
        self.scroll_area.setWidget(self.task_container)
        self.scroll_area.setMinimumHeight(300)

        vbox.addWidget(self.scroll_area)
        self.task_items_list = self.task_layout

        # UI Design
        self.task_input_box.setMinimumHeight(25)
        self.task_input_box.setPlaceholderText("Add Your Task")

        self.setStyleSheet("""
                    /* INPUT CSS */
                            
                    QLabel#Title_Label{
                                font-size: 20px;
                                font-family: san-serif;
                                      }

                    QLineEdit#Task_Input_Box{
                                border: 1px solid;
                                border-radius: 12px;
                                font-size: 12px;
                                font-family: san-serif;
                                padding: 0px 10px
                                            }
                            
                    QPushButton#Add_Task_Btn{
                                border: 1px solid;
                                background-color: hsl(0, 100%, 70%);
                                color: white;
                                font-size: 12px;
                                font-family: san-serif;
                                font-weight: bold;
                                border-radius: 12px;
                                padding: 5.3px 25px;
                                                  }
                            
                    QPushButton#Add_Task_Btn:Hover{
                                background-color: hsl(0, 50%, 50%);
                                                  }
                            
                    QPushButton#Clear_All_Tasks{
                                border: 1px solid;
                                background-color: hsl(360, 100%, 50%);
                                color: white;
                                font-size: 12px;
                                font-family: san-serif;
                                font-weight: bold;
                                border-radius: 5px;
                                padding: 1px 5px;
                                               }
                            
                    QPushButton#Clear_All_Tasks:Hover{
                                background-color: hsl(0, 0%, 22%);
                                                      }
                            
                    /* TASK CSS */
                            
                    QLineEdit#Task_Label{
                                padding: 0px,0px;
                                background: transparent;
                                border: none;
                                font-size: 11px;
                                font-family: san-serif;
                                          }
                            
                    QCheckBox#Task_Checkbox::indicator{
                                border: 1px solid;
                                border-radius: 10px;
                                            }
                                
                    QCheckBox#Task_Checkbox::indicator:checked{
                                background-color: hsl(0, 100%, 70%);
                                                              }
                            
                    QCheckBox#Task_Checkbox::indicator:hover{
                                border-color: hsl(0, 50%, 50%);
                                                            } 
                            
                    QPushButton#Task_Delete_Btn{
                                border: 1px solid;
                                background-color: hsl(0, 100%, 70%);
                                color: white;
                                font-size: 11px;
                                font-family: san-serif;
                                font-weight: bold;
                                border-radius: 8px;
                                padding: 4px 15px;
                                                 }
                            
                    QPushButton#Task_Delete_Btn:Hover{
                                background-color: hsl(0, 50%, 50%);
                                                      }     

                    /* SCROLL CSS */
                            
                    #Scroll_Area {
                                border: none;
                                background-color: hsl(0, 0%, 12%);
                                 }

                        
                    #Scroll_Area QScrollBar:vertical {
                                border: none;
                                background: transparent;
                                width: 6px;
                                margin: 0px;
                                                      }

                    #Scroll_Area QScrollBar::handle:vertical {
                                background: hsl(0, 100%, 70%);
                                min-height: 20px;
                                border-radius: 4px;
                                margin: 1px;
                                                              }

                    #Scroll_Area QScrollBar::handle:vertical:hover {
                                background: hsl(0, 50%, 50%);
                                                                    }


                    #Scroll_Area QScrollBar::add-line:vertical, 
                    #Scroll_Area QScrollBar::sub-line:vertical {
                                height: 0px;
                                                                }                   

""")
        
        self.task_input_box.returnPressed.connect(
            lambda: self.add_task(self.task_input_box.text())
            )
        
        self.add_task_btn.clicked.connect(
            lambda: self.add_task(self.task_input_box.text())
        )

        self.clear_all_tasks.clicked.connect(
                    lambda: self.clear_tasks()
        )

    def create_task_layout(self, text):
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)

        task_checkbox = QCheckBox()
        task_checkbox.setMinimumHeight(30)
        task_checkbox.setObjectName("Task_Checkbox")

        task_label = EditTaskLabel(text)
        task_label.editingDone.connect(lambda: self.handle_edit_finished(task_label))
        task_label.setObjectName("Task_Label")
        task_label.setPlaceholderText("Click To Edit..")
        task_label.setReadOnly(True)
        task_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        task_delete_btn = QPushButton("x")
        task_delete_btn.setObjectName("Task_Delete_Btn")
        task_delete_btn.setMinimumHeight(24)
        task_delete_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        hbox.addWidget(task_checkbox)
        hbox.addWidget(task_label)
        hbox.addWidget(task_delete_btn)

        # Signals
        
        task_checkbox.stateChanged.connect(lambda state: self.checked_task(state, task_label))
        task_delete_btn.clicked.connect(lambda: self.delete_task(hbox))

        return hbox
        

    def add_task(self, text, loading=False):
        if not text.strip():
            self.display_error("Invalid.. No Characters")
            return

        self.task_input_box.clear()
        self.no_tasks_label.hide()
        
        # FIX: Ensure alignment is top and update geometry
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_layout.update() 

        if not loading:
            self.task_count += 1

        self.task_counter_label.setText(f"{self.task_count} Tasks Remaining...")

        task_layout = self.create_task_layout(text) # Create new task
        self.task_items_list.addLayout(task_layout) # Add it to vertical layout
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

        self.save_tasks()

    def handle_edit_finished(self, label):
        if not label.text().strip():
            self.display_error("Task cannot be empty!")
        else:
            self.save_tasks()

    def delete_task(self, layout):
        self.task_count -= 1
        self.task_counter_label.setText(f"{self.task_count} Tasks Remaining...")      

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        if self.task_count <= 0:
            self.task_count = 0
            self.task_counter_label.setText("No Tasks Remaining.")
            self.show_no_tasks_label()

        self.save_tasks()

    def clear_tasks(self):
        while self.task_items_list.count():
            item = self.task_items_list.takeAt(0)
            layout = item.layout()

            if layout:
                self.delete_task(layout)

        if self.task_count == 0:
            self.show_no_tasks_label()
            self.save_tasks()

    def show_no_tasks_label(self):
        self.no_tasks_label.show()
      
        self.task_layout.setAlignment(Qt.AlignCenter)
        self.task_layout.update()

    def checked_task(self, state, label):
        if state == Qt.Checked:
            label.setStyleSheet("text-decoration: line-through; color: gray;")
        elif not state == Qt.Checked:
            label.setStyleSheet("text-decoration: none;")

        remaining = 0

        for i in range(self.task_items_list.count()):
            item = self.task_items_list.itemAt(i)
            layout = item.layout()

            if layout:
                checkbox = layout.itemAt(0).widget()

                if checkbox and not checkbox.isChecked():
                    remaining += 1

        self.task_counter_label.setText(f"{remaining} Tasks Remaining...")

        self.save_tasks()

    def display_error(self, message):
        self.error_msg_label.setText(message)
        QTimer.singleShot(3000, self.reset_error)

    def reset_error(self):
        self.error_msg_label.clear()
        

def run_app():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    application = QApplication(sys.argv)
    window = App()

    window.show()
    sys.exit(application.exec_())

if __name__ == "__main__":
    run_app()
