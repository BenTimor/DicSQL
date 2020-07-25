from logging import info, debug
import pymysql.cursors
import pickle

class Table(list):
    """
    This object represents a table in a mysql database
    You don't have to call it. The MYSQL object calls it when it's needed.
    """

    def __init__(self, db, table, serialization=False):
        self.db = db
        self.table = table
        self.serialization = serialization

    def __setitem__(self, keys, values):
        """
        Sets an item via a list style.
        :param keys: The first key represents the column. The second one represents the where in a replace.
        :param values: The values you want to put in the column.
        """
        # If table not exist, create table
        if self.table not in self.db:
            self.db.create_table(self.table)

        # If you move more than one argument into the function, you have to split it
        # The first argument is going to be the selectors of the SQL statement.
        # The second is going to be a suffix to the SQL statement. Useful for adding 'WHERE' statement.
        selectors, suffix = "", ""
        if isinstance(keys, tuple):
            selectors = keys[0]
            suffix = keys[1]
        else:
            selectors = keys

        # Create the missing columns
        for selector in selectors.split(","):
            selector = selector.strip()
            try:
                # If the column doesn't exist, it throws an exception
                self[selector]
            except Exception as e:
                # After reading online I understood that LONGTEXT doesn't really more 'heavy' than small types.
                # So I'm using ONLY LONGTEXT for saving data.
                self.db.execute(f"ALTER TABLE {self.table} ADD {selector} LONGTEXT DEFAULT {self.db.NONE};")

        if not suffix:
            # SET command
            # When you only got only the selectors, You want to run the INSERT command.
            # When using serialization we want to serialize everything.
            s, values = Table.values_to_serialization(values) if self.serialization else Table.values_to_str(values)
            self.db.execute(f"INSERT INTO {self.table} ({keys}) VALUES ({s})", values)
        else:
            # UPDATE command
            # When you got suffix, You want to update the table.
            # When using serialization we want to serialize everything.
            s, values = Table.values_to_serialization(values) if self.serialization else Table.values_to_str(values)
            keys_set = ', '.join([f"{a} = {b}" for a, b in zip(keys[0].split(","), s.split(","))])
            self.db.execute(f"UPDATE {self.table} SET {keys_set} {keys[1]}", values)

        for select in selectors.split(","):
            if not self[select, f"WHERE {select} != '{self.db.NONE}'"]:
                try:
                    self.db.execute(f"ALTER TABLE {self.table} DROP COLUMN {select};")
                except:
                    del self.db[self.table]

    def __getitem__(self, data):
        """
        Getting items from the table like a dictionary
        :param data: [Column, Optional: Suffix Statement (Like WHERE)]
        :return: List of lists of the data. Literally returning the fetchall of the SQL.
        """
        selectors, suffix = '', ''
        if isinstance(data, tuple):
            # If it's a tuple, we want to get the suffix
            selectors = data[0]
            suffix = data[1]
        else:
            selectors = data

        data = self.db.execute(f"SELECT {selectors} FROM {self.table} {suffix}")
        newdata = []

        # If we are using serialization, we want to de-serialize everything.
        if self.serialization:
            for i in range(len(data)):
                newdata.append([])
                for item in data[i]:
                    if not item:
                        newdata[i].append(None)
                    else:
                        newdata[i].append(pickle.loads(item.encode("latin1")))
            data = newdata

        return data

    def __delitem__(self, column):
        """
        Same as remove
        """
        if isinstance(column, tuple):
            self.remove(column[0], column[1])
        else:
            self.remove(column)

    def remove(self, column, suffix=None):
        """
        Removing a column / a cell
        :param column: The column
        :param suffix: A 'Where' if that's a cell
        """
        if suffix:
            self[column, suffix] = self.db.NONE
        else:
            self.db.execute(f"ALTER TABLE {self.table} DROP COLUMN {column};")

    @staticmethod
    def values_to_serialization(values):
        """
        Getting values and serialize it.
        :return: List of %s, The values
        """
        new_values = []
        parameters = []

        if isinstance(values, str):
            values = values.split(",")
            values = tuple([x.strip() for x in values])

        if not isinstance(values, tuple):
            values = tuple([values])

        s = ["%s"] * len(values)
        values = [pickle.dumps(value).decode("latin1") for value in values]

        return ', '.join(s), values

    @staticmethod
    def values_to_str(values):
        """
        Getting values and str() it.
        :return: List of %s, The values
        """
        new_values = []
        parameters = []

        if isinstance(values, str):
            values = values.split(",")
            values = tuple([x.strip() for x in values])

        if not isinstance(values, tuple):
            values = tuple([values])

        s = ["%s"] * len(values)
        values = [str(value) for value in values]

        return ', '.join(s), values

class DataBase(list):
    """
    A list-like object which allows you to execute queries on a DataBase.
    """

    def __init__(self, host, user, password, database, NONE="NULL"):
        info("Trying to connect the SQL database")
        self.db = pymysql.connect(
            host=host,
            user=user,
            passwd=password,
            database=database,
        )
        info("Connected!")
        self.database = database
        self.cursor = self.db.cursor()
        self.NONE = NONE

    def __getitem__(self, key):
        """
        Getting a Table object which you can add items to / read items from
        :param key: [The table name. Optional: Serialization]
        """
        if isinstance(key, tuple):
            return Table(self, key[0], key[1])
        return Table(self, key)

    def __contains__(self, item):
        """
        Checks if the table exists
        :param item: Table name
        :return: Boolean
        """
        if self.execute(f"SHOW TABLES LIKE '{item}'"):
            return True
        return False

    def create_table(self, table):
        """
        Creating a table. You don't have to use it directly, it's called when you need a new table.
        :param table: The table name.
        """
        self.execute(f"CREATE TABLE {table} (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))")

    def __delitem__(self, key):
        """
        Deleting a table
        :param key: Table name
        """
        self.execute(f"DROP TABLE {key}")

    def execute(self, query, parameters=[]):
        """
        Executing SQL queries. You don't have to use it directly.
        :return: Fetchall of the query if there's one.
        """
        info(f"Executing query > {query} | With parameters {str(parameters)}")
        self.cursor.execute(query, parameters)
        # Try to fetch the data if it has some. If not, add None.
        data = None
        try:
            debug("Strting to fetch data")
            data = self.cursor.fetchall()
            debug("Data has been fetched")
        except:
            debug("There's no data / Data couldn't read")

        # It throws error if I don't close and reopen the cursor
        self.db.commit()
        self.cursor.close()
        self.cursor = self.db.cursor()

        return data
