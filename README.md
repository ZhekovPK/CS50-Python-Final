# PREP COOK ASSISTANT
### Video Demo:  [Prep Cook Assistant](https://youtu.be/FcRC8lGEj9U)
### Description: An application that uses a local SQLite database to store and track products, production numbers, waste, leftovers and assist in the daily duties of a prep cook.

## 1. BACKGROUND
A while ago I had a job as a prep cook where I was responsible for preparing and portioning all of the ingredients that would be used in the restaurant.
A major part of the job was keeping track of what was left over and thrown away as well as keeping an eye on usage and adjusting production numbers accordingly,
as well as training new staff. The way we used to do this was just print out a list every morning, write down what was left over and/or thrown away and then
write down how much was going to be produced, based solely off of experience. Needless to say, with 52 products in  store along with the ocasionally changing seasonal specials  this was one of the hardes thing to teach to new hires, because it required experience and a little bit of an intuition which current employees have developed over time. It's easy to see how a software application, designed to handle these tasks can not only cut down on expenditure by providing more acurate usage data, but also cut down on man-hours both in terms of the work process and in terms of training new employees.

## 2. PROJECT OUTLINES
### 2.A  Core concept
The project would esssentially be a digital version of the paper lists we used and would have to do all the calculations we did by removing all of the guess work and
substituting it with production and usage data that would be stored every day. It would also provide additional information on product preparation, which in theory, a
new employee would use to avoid making mistakes and having to remember a lot of aditional information for every product.

### 2.B Functionality
For the above to work we would need the following:
#### Backend-wise:
* A relational database with two tables: one for products and one for daily production data
* Methods which will handle the calculation of average usage and production
* Methods which will handle the insertion and retrieval of relevant data from the database
#### Frontend-wise:
* A daily production list where we can fill in the relevant daily information and get the production numbers automatically calculated
* A page where we can view old production lists as a frame of refference
* A product list where we can keep track of all the products available, and correct their properties if needed
* A page where we can insert new products, as prep cooks were responsible for keeping track of adding seasonal specials to the list

## 3. EXECUTION
### 3.A Project file structure
The entire project is contained within **project.py** and is arranged as so:
* **Model classes** - one for production data and product each
* **UI elements** - a main window and widgets built using the **PyQT6** framework
* **Calculation methods** - the core 3 methods responsible for calculating average usage and production numbers
* **Database operations** - Methods that fetch specific data or insert new data into the database, built using **sqlite3**

The sections are divided using **#{SECTION NAME}**

### 3.B Database file and setup
As mentioned above, this project uses **SQLite** for its relational database and python's built-in **sqlite3** framework to carry out the querries.
The database is stored localy in a file called **database.db**. It contains two tables: **Products** and **ProductionData**
#### Products table:
This is where all the products available in the restaurant are stored. The table columns are as follows:
* **ID** - The primary key of the table, an integer that is set to auto-increment
* **Name** - The name of the product i.e.: Cooking cream
* **PackageName** - The name of the package the product comes in. This is additional information used for training new employees
* **PortionsFromPackage** - The number of portions we can get from a single package. This is a double used in calculating production numbers
* **CanPortionPartially** - Wether or not you have to use the entire contents of the package. Used in calculations and represented as an 0 ir 1 which is read as a bool
* **Instructions** - These are the instructions on how to prepare the product and is used for training purposes.
#### ProductionData table:
This table represents the daily production data for a product. The columns are as follows:
* **ID** - The primary key of the table, an integer that is set to auto-increment
* **ProductID** - Foreign key integer, referring to the ID of a product from the Products table.
* **Date** - The date to which this entry reffers. Used for looking up old lists.
* **Remaining** - A double representing the number of portions left over from yesterday. Used for calculating production numbers.
* **Discarded** - A double representing the number of portions discarded for any reason. Used for calculating production numbers.
* **Produced** - A double representing the number of portions produced by the prep cook. Used for calculating production numbers.

The tables were manually using a tool called **DB Browser for SQLite** as I didn't want the application to be able to write and edit tables, only data.
The dummy data inserted for testing was done so using a python script i've decided not to include with the project.

### 3.C CODE HIGHLIGHTS
#### Calculation functions
Calculating the number of portions we need to produce is done using 3 functions: **calculate_usage**, **calculate_production** and **adjust_for_packaging**.
```python
def calculate_usage(remaining: list, discarded: list,
                    produced: list, rounding_point: int = 1) -> float:
    """
    Calculates the average usage for a given product, rounded to a specific decimal point
    """
    usage = (mean(remaining) + mean(produced)) - mean(discarded)

    return round(usage, rounding_point)
```
**calculate_usage** returns the average usage for a product based on data acumulated over N ammount of days. It takes 3 lists of doubles, one for **remaining**, **discarded** and **produced** (see ProductionData table). It calculates the mean of each list,
adds **remaining** to **produced** and from that value substracts **discarded**. It then returns that result, rounded to the 1st decimal point (default).
**rounding_point** is a variable i plan to introduce later on as a way for restaurants to chose how specific they want to be with their calculations. The default
value of 1 is what we used at my old job.

```python
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
```
**calculate_production** returns the sugested production number by substracting the **remaining** portions from the **average** usage and then multiplying that value by the **safety margin**. The **safety_margin** variable was put in as something to be implemented later, as a way to ensure that enough portions are produced so that the prep cook
doesn't have to start from scratch on the next day. This however is not applicable to all restaurants so I decided to leave it out for now.

```python
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
```
**adjust_for_packaging** - ensures that if the the entare package of the product has to be used, the production number is calculated accordingly. It helps with training since
the new employees no longer have to remember what must be fully used and what can be portioned partially when calculating production numbers. It takes the **production** number
calculated with **calculate_production**, checks if **can_portion_partially** is false, and if so, returns the first number equalt to or higher than the **production** number but divisible by **portions_per_package**
#### Fetching data and generating a production list
```python
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
            return_data.append((id, name, portions_from_package,
                               can_portion_partially, 0, 0, adjusted, instructions))
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
            instructions = d[5]
        # If ID is the same just append data for remaining, discarded and produced
        else:
            remaining.append(d[4])
            discarded.append(d[5])
            produced.append(d[6])

    # Add the final data tuple to the result set
    usage = calculate_usage(remaining, discarded, produced, 1)
    adjusted = adjust_for_packaging(usage, can_portion_partially, portions_from_package)
    return_data.append((id, name, portions_from_package,
                       can_portion_partially, 0, 0, adjusted, instructions))

    return return_data
```
Generating a daily production list entails 3 major parts: fetching production data from the database, calculating recomended production numbers and building a list of tuples to return. Using **sqlite3** we establish a connection to the databse file and retrieve our relevant fields by preforming a left join on the primary key of **Products** and the foreign key of **ProductionData**. Esentially what we want is the last N ammount of **ProductionData** entries (defined by **days**) for each product, ordered by the **ProductID**.

If the data is fetched successfully, we start iterrating through the result set while tracking the primary key, and for every **ProductionData** entry we add the values for **remaining**. **discarded** and **produced** in 3 lists. Once a different **ProductID** is detected, we calculate the recomended production number using the calculation functions outlined above. Finaly, we combine all of the current data into a tuple and apend it to the **return data**
```python

    return_data.append((id, name, portions_from_package,
                       can_portion_partially, 0, 0, adjusted, instructions))
```
After that, all temporary values are set to the next ones, the lists are cleared and the calculation starts anew. After the entire result set has been iterated through we build
a tuple one more time so that the final data can be apended to **return_data**, which is then returned.
#### Fetching recalculated production values
```python
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
```
Getting recalculated production numbers data from the database works similarly to fetching a new production list data with two notable differences. While the SQL querry logic is the same, this time we have no need for the product names and instructions. All we need is to run the calculations the same way we did above. The second notable difference is that the returned list is no longer a list of tuples, but a list of doubles. This is because once we have that information we only need to edit the **produced** values in the relevant models and UI elements.
#### Other database operations
The rest of the database operations are nothing fancy, just a handfull of standart CRUD queries for the Products and ProductionData tables. That being said, two things are worthy of mentioning.
* There are no UPDATE and DELETE querries  for the **ProductionData** table as the only thing we need to do here is insert entries to represent a daily production list. The user should not have the ability to edit or delete entries in  the same way they should not be allowed to do anything with the tables themselves.
* Due to the nature of **sqlite3**, all INSERT and UPDATE functions use tuples or lists of tuples for the data that needs to be inserted or updated. Example below:
```python
def insert_product(conn_string: str, product_data: tuple) -> None:
```
#### Model classes
While the model classes themselves are pretty straightforward, the reason I want to mention them is because of the heavy use of tuples for database ops. This is why each of the two model classes, **ProdutionDataModel** and **ProductModel** have a number of functions that either take a tuple and use it to asign values to all the fields, or build and return a tuple from the values of the fields. Not only that, but in some cases there are multiple versions that return tuples from the model class fields, because the SQL operation may require only a few of the values that the model tracks. The **ProdutionDataModel** for instance has 2 different "from tuple" type functions, based on wether we are generating a new production list or viewing an old one.
```python
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
```
#### User interface using PyQt6
Oh boy am I both proud and a bit ashamed of this part. A bit ashamed because I know it's a hodge podge of code that will probably cause some professional developer looking at it a migrane. Proud, however, becuase it is my first comple and functioning hodge podge of code and I stand by it. I was aware of the fact that PyQt has a designer tool which I could have used, instead of coding the UI manually. I also know I can style it using CSS but that is a rabbit hole I deliberately decided not to go down, for the sake of time.
The interface boils down three separate types of elements.
* A **MainWindow** class, which extends PyQt's **QMainWindow**. This is what the user sees constantly. It contains a sidebar with navigation buttons and a quit button.
The second element is an interchangable **QWidget** that serves as navigation and is replaced based on the user's actions.
Aside from the obvious swapping of interchangable widgets when different sidebar navigation buttons are clicked, the main window keeps track of wether a new list has already been created. If the user has created a new list, upon clicking **START NEW LIST** a promt will apear, informing that a list already exists and asking wether that list should be dropped and a new one created in its place.
```python
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
                ...
```
Another function of the main window that has to do with tracking wether there is an existing production list or not is the **current list** button. This button is hidden by default and if the user has already started the daily list, yet chose to navigate elsewhere, the button will be displayed, allowing the user to return to the current daily list.
This is checked every time a navigation button other than **START NEW LIST** is pressed.
```python
# If a new daily list has been created display the current list button
if len(PRODUCTION_LIST) > 0:
    self.current_list_button.setVisible(True)
```
* Three navigation widgets, extending PyQt's **QFrame**: **ListDisplayWidget**, **ProductsDisplayWidget** and **AddProductWidget** which are the above mentioned interchangable widgets.
**ListDisplayWidget** is the most complex of the  three. The reason for this is that it is designed to be used both for displaying the new daily list, allowing for all the editing, recalculation and saving and displaying an old list, where the user can pick a date and view the production data for that day, if available. This is why when a **ListDisplayWidget** is created it takes in two parameters, namely **old_list**, a boolean defining wether this is a new or old list and **data_list** which is a list of **ProductionDataModels**.
```python
def __init__(self, old_list: bool = False, data_list: list = PRODUCTION_LIST) -> None:
    super().__init__()
```
By default those values are set so that if no parameters are given, a new list is opened. Certain UI elements are shown or hidden based on the **old_list** parameter, because we need different controlls for each scenario. The core of the widget remains the same, a scrollable area that is populated with **ProductionDataWidget** instances, for every product in the database.
**ProductsDisplayWidget**, similarly to **ListDisplayWidget** is, at it's core, a scrollable area populated with instances of the **ProductDataWidget**.
**AddProductWidget** contains fields and controlls responsible for adding new products to the database, as well as a save button, which when clicked, adds the new product to the database and closes the widget.

* Two "data" widgets, also extending PyQt's **QFrame**: **ProductionDataWidget** and **ProductDataWidget**, which serve as an UI representation of an individual production data or product and are used in their respective display widgets mentioned above.
**ProductionDataWidget** is meant to represent the production data UI element for a single product from the database. It contains fields with relevant production data information such as **remaining**, **discarded** and **produced**, as well as product data information such as the product **name** and **instructions** and a check box to signify that that that product has been produced. The widget takes two parameters one being a model instance containing the data the widget needs to display.Similarly to the **ListDisplayWidget**, here we also have a parameter tracking wheter we are dealing with a new list or not.
```python
def __init__(self, data_model: ProductionDataModel, old_list: bool = False) -> None:
    super().__init__()
```
If the data being displayed reffers to an old list, certain controlls will not be available, such as the task completed checkbox and the instructions button. The editing controlls for **remaining**, **discarded** and **produced** will also be disabled in this case for obvious reasons. The checkbox used for marking wether the product has been produced also disables the editing controlls. A user can complete the list only if every **ProductionDataWidget** has it's checkbox checked.

**ProductDataWidget** is the UI element that displays a product and all its relevant information. It also contains controlls for editing, saving and deleting the product. Similarly to the widget for production data, it takes an instance of **ProductModel** containing the relevant product information. The wiget is designed with a top bar, containing the product name and a **DETAILS** button, which when clicked displays a bottom section with all the relevant data and editing controlls. One thing to note is that we have two instances of the model here which are set to the same values upon initialization.
```python
self.model = model
self.backup_model = ProductModel()
self.backup_model.from_tuple(self.model.to_tuple())
```
This is done so that if editing is enabled and we have changed around the values, once we disable editing, the values will be reverted using the **backup_model**. Editing is also not available by  default. The widget's "allow editing" checkbox must be checked, which will display an additional two buttons, **SAVE** which updates the product with the new values and **DELETE** which deletes the product from the database and removes the instance of **ProductDataWidget**

When building all UI element classes, I tried to stick to a specific order in which the class' **__init__** function is written.
* Initialize the base layout and core elements.
* Combine elements and set element properties when needed
* Asign event handler functions for button clicks and value changes
* Combine all components in the base layout and asign it to the widget
```python
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
```
## 4. Final Thoughts
My initial focus when writing this project was on the backend. Building an user interface for it was a bit of an afterthought, but as work progressed I decided to try my hand at building a rudimentary UI in order to showcase its functionality in a more cohesive way. Naturally a lot of  this could've been acomplished at a much higher quality, both coding and design-wise (for instance, adhering to a propper MVC structure with the UI and properly separating concerns when it comes to UI and business logic) however, this being my first ever "application" I decided that it would be better to make it a working one first and foremost. There are a number of elements, such as the **rounding_point** variable which were and still are something that could be further expanded upon (for instance, having a common setting for the aplication or making it a column in the Products table, where every individual product can have its own specific precision) but ultimately I chose to leave it as is. I was largely surprised by how the more I built, the more little tweaks I wanted to put here and there, but perhaps this is what feature creep is. All in all I had an absolute blast working on my **hodge podge** of a final project. It was one hell of a journey and now, at the end of with, I can say with the biggest smile on my face: "THIS WAS CS50"
