# SimpleSQL
SimpleSQL does a very simple job. It lets you to use MySQL database like it was a dictionary ('HashMap' of python).
## Requirements
- Python 3.5+
- pymysql
- pickle
## Installation
We don't have any official installation yet. You can download the library's folder and use it directly.
## Basic Tutorial
### First of all, You have to connect  to the database

    from SimpleSQL import DataBase

    database = DataBase(
	    "host",
	    "username",
	    "password",
	    "database"
	)
### Get the table you want to modify

    table = database["table"]
**Note:** Every table automatically has an id column.
### Set information to a column

    table["column1"] = "blah blah blah"
The column is created automatically!

**Note:** Every time you use it, it **inserts** a new value, not replaces it. It doesn't remove the old values.
### And multiple columns...

    table["column1, column2"] = "blah blah", "blah"
The both values are going to be in the same row.
### Update an existing value

    table["column1", "WHERE column2='something'"] = "Another blah"
### Removing value

    table.remove("column1") # Removes all the values in the column
    table.remove("column1", "WHERE column2='something') # Removes all the values where the WHERE returns true

### Getting values
First, you have to know that the values comes as a SQL-like data.
Basically, It returns a list of all of the results. Every result is a list that contains all of the values you asked for.

**Code example:**

    print(table["column1, column2"])

**Output example**

    [["Column1 Info (Row 1)", "Column2 Info (Row 1)"], ["Column1 Info (Row 2)", "Column2 Info (Row 2)"]...]


You can also specify additional statements for better selection of values. **For example:**

    table["column1, column2", "WHERE column3='NODER'"]

## Serialization Tutorial
This library can auto-serialize your data. If you want that to happen, You just have to give your table another parameter.

    serializable_table = database["table", True]
And from here you can use it as a normal table. You can insert, update and read objects.
### Inserting Example

    serializable_table["myobject"] = MyObject(1,2)
### Reading Example

    myobject = serializable_table["myobject"]
    print(myobject.sum())
    # Output > 3
**A BIG NOTE:** You cannot use the 'remove' function on this type of table. If you want to remove a serializabled object, use a normal table for that mission.
## Notes
- Everything is saved as a String on the table if you use SimpleSQL.
- This library creates and removes tables and columns automatically. **You don't have to decide what your table looks like** or what tables you want to create. Just use it and the library will do everything for you.
- You can specify to the DataBase object another default value for the database. You can do it by adding to its parameters `NONE="Something"`
- This library is great for personal use and small-data. But can be a little slow for big-data projects. I recommend you to understand what's going on its files before you use it.

Have a great day.
