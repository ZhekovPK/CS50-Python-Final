from datetime import date
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QScrollArea,
    QSizePolicy,
    QHBoxLayout, QVBoxLayout, QDateEdit, QLineEdit, QTextEdit,
    QPushButton, QDoubleSpinBox, QCheckBox, QMessageBox, QLabel
)
import sqlite3
from statistics import mean

PRODUCTION_LIST = []
CONNECTION_STRING = "database.db"

# MODELS
class ProductionDataModel():
    """
    Data model for ProductionData table entries
    """
    def __init__(self) -> None:
        self.id = 0
        self.name = ""
        self.portions_from_package = 0.0
        self.can_portion_partially = False
        self.remaining = 0.0
        self.discarded = 0.0
        self.produced = 0.0
        self.average = 0.0
        self.instructions = ""
        self.completed = False

    
    def from_tuple_new(self, data: tuple) -> None:
        """
        Takes data from the database query for a new production list and populates the variables accordingly
        """
        self.id = data[0]
        self.name = data[1]
        self.portions_from_package = data[2]
        self.can_portion_partially = data[3]
        self.remaining = data[4]
        self.discarded = data[5]
        self.produced = data[6]
        self.average = data[6]
        self.instructions = data[7]

    
    def from_tuple_old(self, data: tuple) -> None:
        """
        Takes data from the database query for an old production list and populates the variables accordingly
        """
        self.id = data[0]
        self.name = data[1]
        self.remaining = data[2]
        self.discarded = data[3]
        self.produced = data[4]
        

    def to_tuple(self) -> tuple:
        """
        Generates tuple from the variables, used for database entry
        """
        return (self.id, date.today(), self.remaining, self.discarded, self.produced)


class ProductModel():
    """
    Data model for ProductionData table entries
    """
    def __init__(self) -> None:
        self.id = int
        self.name = ""
        self.package_name = ""
        self.portions_from_package = 0.0
        self.can_portion_partially = False
        self.instructions = ""


    def from_tuple(self, data: tuple) -> None:
        """
        Takes data from the database query and populates the variables accordingly
        """
        self.id = data[0]
        self.name = data[1]
        self.package_name = data[2]
        self.portions_from_package = data[3]
        self.can_portion_partially = data[4]
        self.instructions = data[5]


    def to_tuple(self) -> tuple:
        """
        Generates a tuple from the variables
        """
        return (self.id, self.name, self.package_name, 
                self.portions_from_package, self.can_portion_partially,
                self.instructions)
    

    def to_tuple_update(self) -> tuple:
        """
        Generates a tuple from the variables used in database updates
        """
        return (self.name, self.package_name, 
                self.portions_from_package, self.can_portion_partially,
                self.instructions)
# MODELS

# UI
class MainWindow(QMainWindow):
    """
    The main window containing a sidebar with navigation controlls and a second widget
    which serves as navigation.
    """
    def __init__(self) -> None:
        super().__init__()
        self.central_widget = QFrame()
        self.base_layout = QHBoxLayout()
        self.sidebar_layout = QVBoxLayout()

        # Sidebar setup
        self.current_list_button = QPushButton("CURRENT LIST")
        self.current_list_button.setVisible(False)
        self.new_list_button = QPushButton("START NEW LIST")
        self.view_list_button = QPushButton("VIEW OLD LIST")
        self.products_button = QPushButton("VIEW PRODUCTS")
        self.new_product_button = QPushButton("NEW PRODUCT")
        self.quit_button = QPushButton("QUIT")
        self.sidebar_layout.addWidget(self.current_list_button)
        self.sidebar_layout.addWidget(self.new_list_button)
        self.sidebar_layout.addWidget(self.view_list_button)
        self.sidebar_layout.addWidget(self.products_button)
        self.sidebar_layout.addWidget(self.new_product_button)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.quit_button)

        # Button functions setup
        self.current_list_button.clicked.connect(self.on_current_list_button_clicked)
        self.new_list_button.clicked.connect(self.on_new_list_button_clicked)
        self.view_list_button.clicked.connect(self.on_view_list_button_clicked)
        self.products_button.clicked.connect(self.on_products_button_clicked)
        self.new_product_button.clicked.connect(self.on_new_product_button_clicked)
        self.quit_button.clicked.connect(self.on_quit_button_clicked)

        # Central widget setup
        self.base_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.base_layout.addLayout(self.sidebar_layout)
        self.central_widget.setLayout(self.base_layout)
        self.setCentralWidget(self.central_widget)


    def on_current_list_button_clicked(self) -> None:
        """
        Displays the current daily production list.
        """
        self.current_list_button.setVisible(False)

        try:
            self.base_layout.itemAt(1).widget().deleteLater()
        except Exception as e:
            print(e)
            pass

        self.base_layout.addWidget(ListDisplayWidget())


    def on_new_list_button_clicked(self) -> None:
        """
        Creates a new list and displays it using the List Display widget
        """
        # If a list has been started already prompt the user wether to start a new one 
        if len(PRODUCTION_LIST) != 0:
            button = QMessageBox.question(self, "Start new list", 
                                          "A list has been started already. Start a new one anyway?")

            if button == QMessageBox.StandardButton.Yes:
                PRODUCTION_LIST.clear()
            else:
                return
            
        data = []
        try: 
            data = get_data_for_new_list(CONNECTION_STRING, 30) 
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return

        if len(data) > 0:
            for d in data:
                data_model = ProductionDataModel()
                data_model.from_tuple_new(d)
                PRODUCTION_LIST.append(data_model)
       
        try:
            self.base_layout.itemAt(1).widget().deleteLater()
        except Exception as e:
            print(e)
            pass
        
        self.base_layout.addWidget(ListDisplayWidget())


    def on_view_list_button_clicked(self) -> None:
        """
        Displays the List Display widget in a configuration
        for browsing old lists.
        """
        # If a new daily list has been created display the current list button
        if len(PRODUCTION_LIST) > 0:
            self.current_list_button.setVisible(True)

        try:
            self.base_layout.itemAt(1).widget().deleteLater()
        except Exception as e:
            print(e)
            pass
        
        self.base_layout.addWidget(ListDisplayWidget(old_list=True))


    def on_products_button_clicked(self) -> None:
        """
        Fetches all products from the database and toggles them in the Products Display widget
        """
        # If a new daily list has been created display the current list button
        if len(PRODUCTION_LIST) > 0:
            self.current_list_button.setVisible(True)

        try:
            data = get_all_products(CONNECTION_STRING)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        model_list = []
        if len(data) > 0:
            for d in data:
                model = ProductModel()
                model.from_tuple(d)
                model_list.append(model)
        
        try:
            self.base_layout.itemAt(1).widget().deleteLater()
        except Exception as e:
            print(e)
            pass
        
        self.base_layout.addWidget(ProductsDisplayWidget(model_list))


    def on_new_product_button_clicked(self) -> None:
        """
        Displays the new product creation widget.
        """
        if len(PRODUCTION_LIST) > 0:
            self.current_list_button.setVisible(True)

        try:
            self.base_layout.itemAt(1).widget().deleteLater()
        except Exception as e:
            print(e)
            pass

        self.base_layout.addWidget(AddProductWidget(ProductModel()))


    def on_quit_button_clicked(self) -> None:
        """
        Exits the application
        """
        # If there is a new list open prompt the user to make sure they don't lose it
        if len(PRODUCTION_LIST) > 0:
            button = QMessageBox.question(self, "Quit application", 
                                          "Current production list not finished. Quit anyway?")

            if button == QMessageBox.StandardButton.Yes:
                pass
            else:
                return

        QApplication.quit()


class ListDisplayWidget(QFrame):
    """
    A widget that displays a production list along with relevant controlls
    """
    def __init__(self, old_list: bool=False, data_list: list=PRODUCTION_LIST) -> None:
        super().__init__()
        self.base_layout = QVBoxLayout()
        self.list_box = QScrollArea()
        self.list_box_layout = QVBoxLayout()
        self.list_headers_layout = QHBoxLayout()
        self.top_bar_layout = QHBoxLayout()
        self.bottom_bar_layout = QHBoxLayout()

        # Top bar setup
        self.suggest_label = QLabel("SUGGESTED PRODUCTION AVERAGE:")
        if old_list == False:
            self.suggest_label.setText("SUGGESTED PRODUCTION AVERAGE:")
        else:
            self.suggest_label.setText("SHOWING PRODUCTION LIST FOR:")
        self.monthly_button = QPushButton("MONTHLY")
        self.biweekly_button = QPushButton("BIWEEKLY")
        self.weekly_button = QPushButton("WEEKLY")
        self.yesterday_button = QPushButton("YESTERDAY")
        self.date_picker = QDateEdit()
        self.go_button = QPushButton("GO")
        self.date_picker.setFixedWidth(150)
        self.date_picker.setDate(date.today())
        self.date_picker.setCalendarPopup(True)
        self.top_bar_layout.addWidget(self.suggest_label)
        self.top_bar_layout.addStretch()
        if old_list == False:
            self.top_bar_layout.addWidget(self.monthly_button)
            self.top_bar_layout.addWidget(self.biweekly_button)
            self.top_bar_layout.addWidget(self.weekly_button)
            self.top_bar_layout.addWidget(self.yesterday_button)
        else:
            self.top_bar_layout.addWidget(self.date_picker)
            self.top_bar_layout.addWidget(self.go_button)
        # Top bar button event handling
        self.monthly_button.clicked.connect(self.on_monthly_button_clicked)
        self.biweekly_button.clicked.connect(self.on_biweekly_button_clicked)
        self.weekly_button.clicked.connect(self.on_weekly_button_clicked)
        self.yesterday_button.clicked.connect(self.on_yesterday_button_clicked)
        self.go_button.clicked.connect(self.on_go_button_clicked)
        
        # List headers setup
        self.header_name = QLabel("NAME:")
        self.header_name.setFixedSize(105, 50)
        self.header_remaining = QLabel("REMAINING:")
        self.header_remaining.setFixedSize(115, 50)
        self.header_discarded = QLabel("DISCARDED:")
        self.header_discarded.setFixedSize(115, 50)
        self.header_produced = QLabel("PRODUCED:")
        self.header_produced.setFixedSize(115, 50)
        self.list_headers_layout.addStretch()
        self.list_headers_layout.addWidget(self.header_name)
        self.list_headers_layout.addStretch()
        self.list_headers_layout.addWidget(self.header_remaining)
        self.list_headers_layout.addWidget(self.header_discarded)
        self.list_headers_layout.addWidget(self.header_produced)

        # Scrollable list setup
        self.container = QWidget()
        if old_list == False:
            for item in data_list:
                self.list_box_layout.addWidget(ProductionDataWidget(item, old_list=old_list))
        self.container.setLayout(self.list_box_layout)
        self.container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.list_box.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_box.setWidgetResizable(True)
        self.list_box.setWidget(self.container)

        # Bottom bar layout
        self.complete_list_button = QPushButton("COMPLETE LIST")
        self.bottom_bar_layout.addStretch()
        self.bottom_bar_layout.addWidget(self.complete_list_button)
        self.bottom_bar_layout.addStretch()
        # Bottom bar button event handling
        self.complete_list_button.clicked.connect(self.on_complete_list_button_clicked)

        self.base_layout.addLayout(self.top_bar_layout)
        self.base_layout.addLayout(self.list_headers_layout)
        self.base_layout.addWidget(self.list_box)
        if old_list == False:
            self.base_layout.addLayout(self.bottom_bar_layout)
        self.setLayout(self.base_layout)


    def on_weekly_button_clicked(self) -> None:
        """
        Fetches and calculates usage data from the database for the last 7 days
        and updates the displayed numbers and the model
        """
        button = QMessageBox.question(self, "Adjust production numbers", 
                                          "Do you want to adjust production numbers to a weekly average?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return
        
        try:
            data = get_average_usage(CONNECTION_STRING, 7)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        for n in range(self.list_box_layout.count()):
            value = data[n] - self.list_box_layout.itemAt(n).widget().remaining_field.value()
            self.list_box_layout.itemAt(n).widget().produce_field.setValue(value)
            PRODUCTION_LIST[n].average = data[n]


    def on_biweekly_button_clicked(self) -> None:
        """
        Fetches and calculates usage data from the database for the last 14 days
        and updates the displayed numbers and the model
        """
        button = QMessageBox.question(self, "Adjust production numbers", 
                                          "Do you want to adjust production numbers to a biweekly average?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return
        
        try:
            data = get_average_usage(CONNECTION_STRING, 14)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        for n in range(self.list_box_layout.count()):
            value = data[n] - self.list_box_layout.itemAt(n).widget().remaining_field.value()
            self.list_box_layout.itemAt(n).widget().produce_field.setValue(value)
            PRODUCTION_LIST[n].average = data[n]

    
    def on_monthly_button_clicked(self) -> None:
        """
        Fetches and calculates usage data from the database for the last 30 days
        and updates the displayed numbers and the model
        """
        button = QMessageBox.question(self, "Adjust production numbers", 
                                          "Do you want to adjust production numbers to a monthly average?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return
        
        try:
            data = get_average_usage(CONNECTION_STRING, 30)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        for n in range(self.list_box_layout.count()):
            value = data[n] - self.list_box_layout.itemAt(n).widget().remaining_field.value()
            self.list_box_layout.itemAt(n).widget().produce_field.setValue(value)
            PRODUCTION_LIST[n].average = data[n]


    def on_yesterday_button_clicked(self) -> None:
        """
        Fetches and calculates usage data from the database for the last day
        and updates the displayed numbers and the model
        """
        button = QMessageBox.question(self, "Adjust production numbers", 
                                          "Do you want to adjust production numbers to yesterday's average?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return
        
        try:
            data = get_average_usage(CONNECTION_STRING, 1)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        for n in range(self.list_box_layout.count()):
            value = data[n] - self.list_box_layout.itemAt(n).widget().remaining_field.value()
            self.list_box_layout.itemAt(n).widget().produce_field.setValue(value)
            PRODUCTION_LIST[n].average = data[n]


    def on_complete_list_button_clicked(self) -> None:
        """
        Prompts the user wether or not they want to complete the list
        If so, checks that all models have their completed value set to true
        before writing the new production data to the database
        """
        for p in PRODUCTION_LIST:
            if p.completed == False:
                button = QMessageBox.critical(self, "Cannot complete list", 
                                                 "List cannot be completed untill all items have been checked off")
                return
            
        button = QMessageBox.question(self, "Complete list", 
                                          "Are you sure you want complete the production list?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return
        
        data = []

        for item in PRODUCTION_LIST:
            data.append(item.to_tuple())
        
        try:
            insert_production_data(CONNECTION_STRING, data)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return

        PRODUCTION_LIST.clear()
        self.deleteLater()


    def on_go_button_clicked(self) -> None:
        """
        If an old list is displayed, fetches the relevant production data from the databse
        and displays it.
        If there is no data, displays a message in the list box
        """
        if self.list_box_layout.count() > 0:
            for n in range(self.list_box_layout.count()):
                self.list_box_layout.itemAt(n).widget().deleteLater()

        data = get_old_list(CONNECTION_STRING, self.date_picker.date().toPyDate())

        if data:
            for d in data:
                data_model = ProductionDataModel()
                data_model.from_tuple_old(d)
                self.list_box_layout.addWidget(ProductionDataWidget(data_model, old_list=True))
        else:
            label = QLabel(f"THERE IS NO PRODUCTION DATA FOR {self.date_picker.date().toPyDate()}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_box_layout.addWidget(label)


class ProductionDataWidget(QFrame):
    """
    A widget that displays production data for a product
    and has controlls for editingand 
    """
    def __init__(self, data_model: ProductionDataModel, old_list: bool = False) -> None:
        super().__init__()
        self.base_layout = QHBoxLayout()
        self.instructions_button = QPushButton("?")
        self.name_label = QLabel(data_model.name)
        self.remaining_field = QDoubleSpinBox()
        self.discarded_field = QDoubleSpinBox()
        self.produce_field = QDoubleSpinBox()
        self.completed_checkbox = QCheckBox()
        self.model = data_model

        #Double fields setup:
        self.remaining_field.setSingleStep(0.1)
        self.remaining_field.setDecimals(1)
        self.remaining_field.setValue(self.model.remaining)
        self.remaining_field.setEnabled(not old_list)
        self.remaining_field.setFixedSize(100, 40)
        self.discarded_field.setSingleStep(0.1)
        self.discarded_field.setDecimals(1)
        self.discarded_field.setValue(self.model.discarded)
        self.discarded_field.setEnabled(not old_list)
        self.discarded_field.setFixedSize(100, 40)
        if self.model.can_portion_partially == False:
            self.produce_field.setSingleStep(self.model.portions_from_package)
        else:
            self.produce_field.setSingleStep(0.1)
        self.produce_field.setDecimals(1)
        self.produce_field.setValue(self.model.produced)
        self.produce_field.setEnabled(not old_list)
        self.produce_field.setFixedSize(100, 40)

        # Bind value changed event handlers
        self.remaining_field.valueChanged.connect(self.on_remaining_value_changed)
        self.discarded_field.valueChanged.connect(self.on_discarded_value_changed)
        self.produce_field.valueChanged.connect(self.on_produced_value_changed)
        self.completed_checkbox.checkStateChanged.connect(self.on_completed_value_changed)

        self.instructions_button.setFixedSize(25, 25)
        self.instructions_button.clicked.connect(self.on_instructions_button_clicked)

        #Layout setup
        if old_list == False:
            self.base_layout.addWidget(self.instructions_button)
        self.base_layout.addWidget(self.name_label)
        self.base_layout.addStretch()
        self.base_layout.addWidget(self.remaining_field)
        self.base_layout.addWidget(self.discarded_field)
        self.base_layout.addWidget(self.produce_field)
        if old_list == False:
            self.base_layout.addWidget(self.completed_checkbox)

        self.setLayout(self.base_layout)


    def on_remaining_value_changed(self) -> None:
        """
        When the value of "remaining" changes, corrects the "produced" value and updates the model
        """
        new_value = calculate_production(self.remaining_field.value(), self.model.average)
        new_value = adjust_for_packaging(new_value, self.model.can_portion_partially, self.model.portions_from_package)
        self.produce_field.setValue(new_value)

        self.model.produced = new_value
        self.model.remaining = self.remaining_field.value()


    def on_discarded_value_changed(self) -> None:
        """
        When the value of "discarded" changes, updates the model
        """
        self.model.discarded = round(self.discarded_field.value(), 1)


    def on_produced_value_changed(self) -> None:
        """
        When the value of "produced" changes, updates the model
        """
        self.model.produced = round(self.produce_field.value(), 1)


    def on_completed_value_changed(self) -> None:
        """
        When the value of "discarded" changes, updates the model
        """
        if self.completed_checkbox.isChecked():
            self.remaining_field.setEnabled(False)
            self.discarded_field.setEnabled(False)
            self.produce_field.setEnabled(False)
        else:
            self.remaining_field.setEnabled(True)
            self.discarded_field.setEnabled(True)
            self.produce_field.setEnabled(True)

        self.model.completed = self.completed_checkbox.isChecked()


    def on_instructions_button_clicked(self) -> None:
        """
        Displays a pop-up with the instructions for portioning the current product.
        """
        button = QMessageBox.information(self, "Preparation instructions", self.model.instructions)


class ProductsDisplayWidget(QFrame):
    """
    Displays a list of widgets for every product in the database
    """
    def __init__(self, model_list: list) -> None:
        super().__init__()
        self.base_layout = QHBoxLayout()
        self.list_box = QScrollArea()
        self.list_box_layout = QVBoxLayout()
        
        # Set up product list 
        self.container = QWidget()
        for model in model_list:
            self.list_box_layout.addWidget(ProductDataWidget(model))
        self.list_box_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container.setLayout(self.list_box_layout)
        self.container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.list_box.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_box.setWidgetResizable(True)
        self.list_box.setWidget(self.container)

        self.base_layout.addWidget(self.list_box)
        self.setLayout(self.base_layout)
    

class ProductDataWidget(QFrame):
    """
    A widget that displays the details of a single product from the database
    Contains controlls for editing, updating and deleting
    """
    def __init__(self, model: ProductModel) -> None:
        super().__init__()
        self.base_layout = QVBoxLayout()
        self.top_bar = QHBoxLayout()
        self.bottom_bar = QHBoxLayout()
        self.model = model
        self.backup_model = ProductModel()
        self.backup_model.from_tuple(self.model.to_tuple())

        # Top bar setup
        self.name_edit = QLineEdit(f"{self.model.name}")
        self.details_button = QPushButton("DETAILS")
        self.details_button.setCheckable(True)
        self.top_bar.addWidget(self.name_edit)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.details_button)
        # Button event handler setup
        self.details_button.clicked.connect(self.on_details_button_clicked)

        # Bottom bar setup
        self.bottom_bar_widget = QWidget()
        self.left_section = QVBoxLayout()
        self.package_bar = QHBoxLayout()
        self.package_label = QLabel("PACKAGING NAME:")
        self.package_name_edit = QLineEdit(f"{self.model.package_name}")
        self.portions_bar = QHBoxLayout()
        self.portions_label = QLabel("PORTIONS IN PACKAGE:")
        self.portions_double_box = QDoubleSpinBox()
        self.portions_double_box.setValue(self.model.portions_from_package)
        self.partial_bar = QHBoxLayout()
        self.partial_label = QLabel("CAN BE PORTIONED PARTIALY:")
        self.partial_checkbox = QCheckBox()
        self.partial_checkbox.setChecked(self.model.can_portion_partially)
        self.right_section = QVBoxLayout()
        self.instructions_label = QLabel("INSTRUCTIONS:")
        self.instructions_edit = QTextEdit(f"{self.model.instructions}")
        self.edit_bar = QHBoxLayout()
        self.edit_label = QLabel("ALLOW EDITING")
        self.edit_checkbox = QCheckBox()
        self.save_button = QPushButton("SAVE")
        self.delete_button = QPushButton("DELETE")

        # Combining elements to build the interface
        self.package_bar.addWidget(self.package_label)
        self.package_bar.addWidget(self.package_name_edit)
        self.portions_bar.addWidget(self.portions_label)
        self.portions_bar.addWidget(self.portions_double_box)
        self.partial_bar.addWidget(self.partial_label)
        self.partial_bar.addWidget(self.partial_checkbox)
        self.edit_bar.addWidget(self.edit_label)
        self.edit_bar.addWidget(self.edit_checkbox)
        self.edit_bar.addStretch()
        self.edit_bar.addWidget(self.save_button)
        self.edit_bar.addWidget(self.delete_button)
        self.left_section.addLayout(self.package_bar)
        self.left_section.addLayout(self.portions_bar)
        self.left_section.addLayout(self.partial_bar)
        self.left_section.addStretch()
        self.left_section.addLayout(self.edit_bar)
        self.left_section.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_section.addWidget(self.instructions_label)
        self.right_section.addWidget(self.instructions_edit)
        self.right_section.addLayout(self.edit_bar)
        self.right_section.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bottom_bar.addLayout(self.left_section)
        self.bottom_bar.addLayout(self.right_section)
        self.bottom_bar_widget.setLayout(self.bottom_bar)

        # Hide editing controlls unless editing is allowed
        self.set_edit_enabled()
        self.save_button.setVisible(False)
        self.delete_button.setVisible(False)

        # Event binding
        self.edit_checkbox.checkStateChanged.connect(self.set_edit_enabled)
        self.save_button.clicked.connect(self.on_save_button_pressed)
        self.delete_button.clicked.connect(self.on_delete_button_pressed)
        self.name_edit.textChanged.connect(self.on_name_changed)
        self.package_name_edit.textChanged.connect(self.on_package_name_changed)
        self.portions_double_box.valueChanged.connect(self.on_portions_from_package_changed)
        self.partial_checkbox.checkStateChanged.connect(self.on_can_portion_partially_changed)
        self.instructions_edit.textChanged.connect(self.on_instructions_changed)
        
        self.base_layout.addLayout(self.top_bar)
        self.base_layout.addWidget(self.bottom_bar_widget)
        self.bottom_bar_widget.setHidden(True)
        self.setLayout(self.base_layout)


    def set_edit_enabled(self) -> None:
        """
        When the edit checkbox is clicked, enables or disables editing fields.
        When editing is disabled the values are reset using the backup model
        """
        enabled = self.edit_checkbox.isChecked()
        self.name_edit.setEnabled(enabled)
        self.package_name_edit.setEnabled(enabled)
        self.portions_double_box.setEnabled(enabled)
        self.partial_checkbox.setEnabled(enabled)
        self.instructions_edit.setEnabled(enabled)
        self.save_button.setVisible(enabled)
        self.delete_button.setVisible(enabled)

        if enabled == False:
            self.model.from_tuple(self.backup_model.to_tuple())
            self.name_edit.setText(self.model.name)
            self.package_name_edit.setText(self.model.package_name)
            self.portions_double_box.setValue(self.model.portions_from_package)
            self.partial_checkbox.setChecked(self.model.can_portion_partially)
            self.instructions_edit.setText(self.model.instructions)


    def on_details_button_clicked(self) -> None:
        """
        Togles the botom bar (details) on and off.
        When togled off, editing is also disabled
        """
        if self.details_button.isChecked() == True:
            self.bottom_bar_widget.setHidden(False)
        else:
            self.bottom_bar_widget.setHidden(True)
            if self.edit_checkbox.isChecked():
                self.edit_checkbox.setChecked(False)


    def on_save_button_pressed(self) -> None:
        """
        Prompts the user to confirm their choice to save
        If confirmed, updates the product details in the database and the backup model
        """
        button = QMessageBox.question(self, "Save changes", 
                                          "Are you sure you want to save the changes you made?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return
        
        try:
            update_product(CONNECTION_STRING, self.model.to_tuple_update(), self.model.id)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        self.backup_model.from_tuple(self.model.to_tuple())


    def on_delete_button_pressed(self) -> None:
        """
        Prompts the user to confirm their choice to delete
        If confirmed, deletes the product from the database and removes the widget
        """
        button = QMessageBox.question(self, "Delete product", 
                                          "Are you sure you want to delete this product?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return
        
        try:
            delete_product(CONNECTION_STRING, self.model.id)
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        self.deleteLater()


    def on_name_changed(self) -> None:
        """
        Updates the name in the model
        """
        self.model.name = self.name_edit.text()    

    
    def on_package_name_changed(self) -> None:
        """
        Updates the package name in the model
        """
        self.model.package_name = self.package_name_edit.text()

    
    def on_portions_from_package_changed(self) -> None:
        """
        Updates the number of portions from one package in the model
        """
        self.model.portions_from_package = round(self.portions_double_box.value(), 1)


    def on_can_portion_partially_changed(self) -> None:
        """
        Updates wether or not the product can be portioned partially in the model
        """
        self.model.can_portion_partially = self.partial_checkbox.isChecked()


    def on_instructions_changed(self) -> None:
        """
        Updates the instructions in the model
        """
        self.model.instructions = self.instructions_edit.toPlainText()


class AddProductWidget(QFrame):
    """
    A widget for creating new products with relevant controls for 
    field editing and writing to the database
    """
    def __init__(self, model: ProductModel) -> None:
        super().__init__()
        self.base_layout = QVBoxLayout()
        self.name_label = QLabel("PRODUCT NAME:")
        self.name_field = QLineEdit("NAME")
        self.package_label = QLabel("PACKAGE NAME:")
        self.package_field = QLineEdit("PACKAGE")
        self.portions_label = QLabel("PORTIONS CONTAINED IN PACKAGE:")
        self.portions_field = QDoubleSpinBox()
        self.partial_layout = QHBoxLayout()
        self.partial_label = QLabel("CAN BE PORTIONED PARTIALLY:")
        self.partial_field = QCheckBox()
        self.instructions_label = QLabel("PORTIONING INSTRUCTIONS:")
        self.instructions_field = QTextEdit("INSTRUCTIONS")
        self.create_button = QPushButton("CREATE")
        self.model = model

        self.base_layout.addWidget(self.name_label)
        self.base_layout.addWidget(self.name_field)
        self.base_layout.addWidget(self.package_label)
        self.base_layout.addWidget(self.package_field)
        self.base_layout.addWidget(self.portions_label)
        self.base_layout.addWidget(self.portions_field)
        self.partial_layout.addWidget(self.partial_label)
        self.partial_layout.addWidget(self.partial_field)
        self.base_layout.addLayout(self.partial_layout)
        self.base_layout.addWidget(self.instructions_label)
        self.base_layout.addWidget(self.instructions_field)
        self.base_layout.addWidget(self.create_button)

        self.name_field.textChanged.connect(self.on_name_value_changed)
        self.package_field.textChanged.connect(self.on_package_value_changed)
        self.portions_field.valueChanged.connect(self.on_portions_value_changed)
        self.partial_field.checkStateChanged.connect(self.on_partial_value_changed)
        self.instructions_field.textChanged.connect(self.on_instructions_value_changed)
        self.create_button.clicked.connect(self.on_create_button_clicked)

        self.hlayout = QHBoxLayout()
        self.hlayout.addStretch()
        self.hlayout.addLayout(self.base_layout)
        self.hlayout.addStretch()
        self.setLayout(self.hlayout)


    def on_name_value_changed(self) -> None:
        """
        Updates the model value for name
        """
        self.model.name =self.name_field.text()


    def on_package_value_changed(self) -> None:
        """
        Updates the model value for package name
        """
        self.model.package_name = self.package_field.text()
    
    
    def on_portions_value_changed(self) -> None:
        """
        Updates the model value for portions from package
        """
        self.model.portions_from_package = self.portions_field.value()

        
    def on_partial_value_changed(self) -> None:
        """
        Updates the model value for partial portioning
        """
        self.model.can_portion_partially = self.partial_field.isChecked()


    def on_instructions_value_changed(self) -> None:
        """
        Updates the model value for portioning instructions
        """
        self.model.instructions = self.instructions_field.toPlainText()


    def on_create_button_clicked(self) -> None:
        """
        Prompts the user to confirm the creation
        and writes the ne product to the database
        """
        button = QMessageBox.question(self, "Create new product", 
                                          "Are you sure you want add this product to the database?")
        if button == QMessageBox.StandardButton.Yes:
            pass
        else:
            return

        try:
            insert_product(CONNECTION_STRING, self.model.to_tuple_update())
        except Exception as error:
            button = QMessageBox.information(self,f"{error}")
            return
        
        self.deleteLater()
# UI

# CALCULATIONS
def calculate_usage(remaining: list, discarded: list,
                    produced: list, rounding_point: int = 1) -> float:
    """
    Calculates the average usage for a given product, rounded to a specific decimal point
    """
    usage = (mean(remaining) + mean(produced)) - mean(discarded)

    return round(usage, rounding_point)


def calculate_production(remaining: float, average: float, 
                         safety_margin: float = 1, rounding_point: int = 1) -> float:
    """
    Calculates the sugested production numbers for the day, based on a safety margin
    and rounded to a specific decimal point
    """
    produce = (average - remaining) * safety_margin
    if produce < 0:
        produce = 0

    return round(produce, rounding_point)


def adjust_for_packaging(production: float, can_portion_partially: bool, 
                         portions_per_package: float, rounding_point: int = 1) -> float:
    """
    Adjusts the production number based on:
    * the number of portions derived from one packaging
    * wether or not the whole packaging must be used
    """
    result = 0
    if not can_portion_partially:
        while result < production:
            result += portions_per_package
        return round(result, rounding_point)
    
    return round(production, rounding_point)
# CALCULATIONS

# DATABASE OPS
def get_all_products(conn_string: str,) -> list:
    """
    Retrieves all the products from the database and returns them as an array of tuples
    """
    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().execute("SELECT * FROM Products")
            return result.fetchall()
    except sqlite3.OperationalError as error:
        raise Exception(error)
        

def insert_product(conn_string: str, product_data: tuple) -> None:
    """
    Adds a new product to the database
    """
    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().execute("""
                INSERT INTO Products 
                (Name, PackageName, PortionsFromPackage, CanPortionPartially, Instructions)
                VALUES (?, ?, ?, ?, ?)
            """, product_data)
    except sqlite3.OperationalError as error:
        raise Exception(error)


def delete_product(conn_string: str, product_id: int) -> None:
    """
    Removes a product from the database
    """
    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().execute("DELETE FROM Products WHERE ID=?", (product_id,))
    except sqlite3.OperationalError as error:
        raise Exception(error)


def update_product(conn_string: str, product_data: tuple, product_id: int):
    """
    Updates an existing product in the database
    """
    try:
        with sqlite3.connect(conn_string) as conn:
            data = product_data + (product_id,)
            result = conn.cursor().execute("""
                UPDATE Products
                SET Name = ?, PackageName = ?,
                    PortionsFromPackage = ?, 
                    CanPortionPartially = ?,
                    Instructions = ?
                WHERE ID = ?
            """, data)
    except sqlite3.OperationalError as error:
        raise Exception(error)


def insert_production_data(conn_string: str, production_list: list) -> None:
    """
    Adds production data for the entire new list to the database
    """
    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().executemany("""
                INSERT INTO ProductionData 
                (ProductID, Date, Remaining, Discarded, Produced)
                VALUES (?, ?, ?, ?, ?)
            """, production_list)
    except sqlite3.OperationalError as error:
        raise Exception(error)


def get_data_for_new_list(conn_string: str, days: int) -> list:
    """
    Retrieve the production data for all products over an N-day period
    Calculate average usage and return a tuple for every product
    """
    return_data = []
    data = []

    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().execute("""
                SELECT Products.ID, Products.Name, 
                Products.PortionsFromPackage, Products.CanPortionPartially,
                ProductionData.Remaining, ProductionData.Discarded, 
                ProductionData.Produced, Products.Instructions
                FROM Products
                LEFT JOIN ProductionData
                ON Products.ID = ProductionData.ProductID
                WHERE ProductionData.Date 
                IN (SELECT ProductionData.Date FROM ProductionData ORDER BY ProductionData.ProductID DESC LIMIT (?))
                ORDER BY Products.ID ASC
            """, (days,))
            data = result.fetchall()
    except sqlite3.OperationalError as error:
        raise Exception(error)
    
    id = data[0][0]
    name = data[0][1]
    portions_from_package = data[0][2]
    can_portion_partially = data[0][3]
    remaining = []
    discarded = []
    produced = []
    instructions = data[0][7]

    for d in data:
        # Different ID than the initial means the next entries concern a different product
        if d[0] != id:
            # If id is different, then create the tuple for this product before reading next set of data
            usage = calculate_usage(remaining, discarded, produced, 1)
            adjusted = adjust_for_packaging(usage, can_portion_partially, portions_from_package)
            return_data.append((id, name, portions_from_package, can_portion_partially, 0, 0, adjusted, instructions))
            # Set variables to new data
            id = d[0]
            name = d[1]
            portions_from_package = d[2]
            can_portion_partially = d[3]  
            # Clear lists for remaining, discarded and produced before adding new data
            remaining.clear()
            discarded.clear()
            produced.clear()
            remaining.append(d[4])
            remaining.append(d[5])
            remaining.append(d[6])
            instructions = d[7]
        # If ID is the same just append data for remaining, discarded and produced
        else:
            remaining.append(d[4])
            discarded.append(d[5])
            produced.append(d[6])

    # Add the final data tuple to the result set
    usage = calculate_usage(remaining, discarded, produced, 1)
    adjusted = adjust_for_packaging(usage, can_portion_partially, portions_from_package)
    return_data.append((id, name, portions_from_package, can_portion_partially, 0, 0, adjusted, instructions))

    return return_data
        

def get_old_list(conn_string: str, date: date) -> list:
    """
    Retrieve production data for a previous date
    """
    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().execute("""
                SELECT Products.ID, Products.Name, ProductionData.Remaining,
                ProductionData.Discarded, ProductionData.Produced
                FROM Products
                LEFT JOIN ProductionData
                ON Products.ID = ProductionData.ProductID
                WHERE ProductionData.Date == (?)
                ORDER BY Products.ID ASC
            """, (date,))
            return result.fetchall()
    except sqlite3.OperationalError as error:
        raise Exception(error)


def get_average_usage(conn_string: str, days) -> list:
    """
    Fetches production data for N number of days for each product,
    recalculates average usage and returns it as a list
    """
    return_data = []
    data = []
    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().execute("""
                SELECT Products.ID, Products.PortionsFromPackage, 
                Products.CanPortionPartially, ProductionData.Remaining,
                ProductionData.Discarded, ProductionData.Produced
                FROM Products
                LEFT JOIN ProductionData
                ON Products.ID = ProductionData.ProductID
                WHERE ProductionData.Date IN 
                (SELECT ProductionData.Date FROM ProductionData ORDER BY ID DESC LIMIT (?))
            """, (days,))
            data = result.fetchall()
    except sqlite3.OperationalError as error:
        raise Exception(error)

    id = data[0][0]
    portions_from_package = data[0][1]
    can_portion_partially = data[0][2]
    remaining = []
    discarded = []
    produced = []

    for d in data:
        if id != d[0]:
            usage = calculate_usage(remaining, discarded, produced)
            adjusted = adjust_for_packaging(usage, can_portion_partially, portions_from_package)
            return_data.append(adjusted)
            remaining.clear()
            discarded.clear()
            produced.clear()
            
            id = d[0]
            portions_from_package = d[1]
            can_portion_partially = d[2]
            remaining.append(d[3])
            discarded.append(d[4])
            produced.append(d[5])
        else:
            remaining.append(d[3])
            discarded.append(d[4])
            produced.append(d[5])
    
    usage = calculate_usage(remaining, discarded, produced)
    adjusted = adjust_for_packaging(usage, can_portion_partially, portions_from_package)
    return_data.append(adjusted)
    return return_data
# DATABASE OPS

def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.setMinimumSize(800, 500)
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()