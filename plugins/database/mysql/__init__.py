# -*- coding: utf-8 -*-

from . import __path__ as ROOT_PATH
from logging import getLogger
from pymysql import connect, Binary
from re import compile, IGNORECASE
from collections import Iterable

MOD_PATH = list(ROOT_PATH)[0]


class dbase:
    # Importing external functions
    from ..common.category import category_add, category_rename, category_delete
    from ..common.component import component_data
    from ..common.datasheet import datasheet_clear, datasheet_set, datasheet_view
    from ..common.field import field_add, field_delete, field_get_data
    from ..common.file import file_add, file_del, file_export
    from ..common.image import image_add, image_del
    from ..common.template import template_add, template_del, template_get, template_ren

    def __init__(
        self,
        host,
        user,
        passwd,
        database,
        auto_commit=False,
        templates=False,
        parent=None
    ):
        self.auto_commit = auto_commit
        self.compiled_ac_search = compile(r'.*(INSERT|UPDATE|DELETE).*', IGNORECASE)
        self.compiled_field_detect = compile(r'^[\w\d\s\-_\.]+$', IGNORECASE)
        self.templates = templates
        self.log = getLogger('MainWindow')
        self.parent = parent

        # Inicializing all tables if not exists
        try:
            self.log.debug("Connecting to database")
            self.conn = connect(host, user, passwd, database)

        except Exception as e:
            self.log.error("There was an error connecting to sqlite dbase: {}".format(e))
            raise Exception(e)

        if not templates:
            # Inicializing components tables if not exists
            self.log.debug("Initializing components database")
            # Categories table
            try:
                self.log.debug("Checking Categories table")
                exists = self.query("SHOW TABLES LIKE 'Categories';")
                if len(exists) == 0:
                    self.log.debug("Categories table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE
                            `Categories`(
                              `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                              `Parent` INTEGER NOT NULL,
                              `Name` TEXT NOT NULL,
                              `Expanded` BOOLEAN,
                              `Template` INTEGER DEFAULT NULL,
                              FOREIGN KEY (`Parent`)
                                REFERENCES `Categories`(`ID`)
                                ON DELETE CASCADE
                            );
                        """
                    )
                    self.query(
                        """
                          INSERT INTO
                            `Categories`
                          VALUES
                          (
                            -1,
                            -1,
                            "Root category (to be ignored)",
                            0,
                            null
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `Categories_parent`
                          ON
                            `Categories`(`Parent` ASC);
                        """
                    )
                else:
                    self.log.debug("Categories table already exists. Continuing...")

            except Exception as e:
                self.log.error("There was an error creating the Categories table: {}".format(e))
                self.conn.rollback()
                raise Exception(e)
            # Components table
            try:
                self.log.debug("Checking Components table")
                exists = self.query("SHOW TABLES LIKE 'Components';")
                if len(exists) == 0:
                    self.log.debug("Components table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Components` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Category` INTEGER NOT NULL,
                            `Stock` INTEGER NOT NULL DEFAULT 0,
                            `Template` INTEGER NOT NULL,
                            FOREIGN KEY (`Category`)
                              REFERENCES `Categories`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `components_category`
                          ON
                            `Components`(`Category` ASC);
                        """
                    )
                else:
                    self.log.debug("Components table already exists. Continuing...")

            except Exception as e:
                self.log.error("There was an error creating the Components table: {}".format(e))
                self.conn.rollback()
                raise Exception(e)
            # Components_data table
            try:
                self.log.debug("Checking Components_data table")
                exists = self.query("SHOW TABLES LIKE 'Components_data';")
                if len(exists) == 0:
                    self.log.debug("Components_data table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Components_data` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Component` INTEGER NOT NULL,
                            `Field_ID` INTEGER NOT NULL,
                            `Value` TEXT NOT NULL,
                            UNIQUE (
                              `Component`,
                              `Field_ID`
                            ),
                            FOREIGN KEY (`Component`)
                              REFERENCES `Components`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `components_data_component`
                          ON
                            `Components_data`(`Component` ASC);
                        """
                    )
                else:
                    self.log.debug("Components_data table already exists. Continuing...")

            except Exception as e:
                self.log.error(
                    "There was an error creating the Components_data table: {}".format(e)
                )
                self.conn.rollback()
                raise Exception(e)
            # Images table
            try:
                self.log.debug("Checking Images table")
                exists = self.query("SHOW TABLES LIKE 'Images';")
                if len(exists) == 0:
                    self.log.debug("Images table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Images` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Component_id` INTEGER DEFAULT NULL,
                            `Category_id` INTEGER DEFAULT NULL,
                            `Image` MEDIUMBLOB NOT NULL,
                            `Imagecompression` INTEGER DEFAULT 0,
                            FOREIGN KEY (`Component_id`)
                              REFERENCES `Components`(`ID`)
                              ON DELETE CASCADE,
                            FOREIGN KEY (`Category_id`)
                              REFERENCES `Categories`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `images_component_id`
                          ON
                            `Images`(`Component_id` ASC);
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `images_category_id`
                          ON
                            `Images`(`Category_id` ASC);
                        """
                    )
                else:
                    self.log.debug("Images table already exists. Continuing...")

            except Exception as e:
                self.log.error("There was an error creating the Images table: {}".format(e))
                self.conn.rollback()
                raise Exception(e)
            # Files table
            try:
                self.log.debug("Checking Files table")
                exists = self.query("SHOW TABLES LIKE 'Files';")
                if len(exists) == 0:
                    self.log.debug("Files table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Files`(
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Component` INTEGER NOT NULL,
                            `Filename` TEXT(8) NOT NULL,
                            `Datasheet` BOOLEAN DEFAULT 0,
                            FOREIGN KEY (`Component`)
                              REFERENCES `Components`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                            CREATE INDEX
                              `Files_component`
                            ON
                              `Files`(`Component`);
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `Files_datasheet`
                          ON
                            `Files`(`Datasheet`);
                        """
                    )
                else:
                    self.log.debug("Files table already exists. Continuing...")

            except Exception as e:
                self.log.error("There was an error creating the Files table: {}".format(e))
                self.conn.rollback()
                raise Exception(e)
            # Files_blob table
            try:
                self.log.debug("Checking Files_blob table")
                exists = self.query("SHOW TABLES LIKE 'Files_blob';")
                if len(exists) == 0:
                    self.log.debug("Files_blob table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Files_blob` (
                            `File_id` INTEGER NOT NULL,
                            `Filedata` LONGBLOB NOT NULL,
                            `Filecompression` INTEGER DEFAULT 0,
                            FOREIGN KEY (`File_id`)
                              REFERENCES `Files`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                else:
                    self.log.debug("Files_blob table already exists. Continuing...")

            except Exception as e:
                self.log.error("There was an error creating the Files_blob table: {}".format(e))
                self.conn.rollback()
                raise Exception(e)

            try:
                # Commiting all work
                self.conn.commit()
            except Exception as e:
                self.log.error("There was an error commiting all: {}".format(e))
                self.conn.rollback()
                raise Exception(e)
        else:
            # Inicializing templates tables if not exists
            self.log.debug("Initializing templates database")
            # Categories Table
            try:
                self.log.debug("Checking Categories table")
                self.log.debug("Checking Categories table")
                exists = self.query("SHOW TABLES LIKE 'Categories';")
                if len(exists) == 0:
                    self.log.debug("Categories table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE
                          `Categories` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Parent` INTEGER NOT NULL,
                            `Name` TEXT NOT NULL,
                            `Expanded` BOOLEAN DEFAULT 0,
                            FOREIGN KEY (`Parent`)
                              REFERENCES `Categories`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          INSERT INTO
                            `Categories`
                          VALUES
                          (
                            -1,
                            -1,
                            "Root category (to be ignored)",
                            0
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `categories_parent`
                          ON
                            `Categories`(`Parent` ASC);
                        """
                    )
                else:
                    self.log.debug("?? table already exists. Continuing...")
            except Exception as e:
                self.log.error("There was an error creating the ?? table: {}".format(e))
                raise Exception(e)
            # Templates Table
            try:
                self.log.debug("Checking Templates table")
                self.log.debug("Checking Templates table")
                exists = self.query("SHOW TABLES LIKE 'Templates';")
                if len(exists) == 0:
                    self.log.debug("Templates table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Templates` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Category` INTEGER NOT NULL,
                            `Name` TEXT NOT NULL,
                            FOREIGN KEY (`Category`)
                              REFERENCES `Categories`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `templates_category`
                          ON
                            `Templates`(`Category` ASC);
                        """
                    )
                else:
                    self.log.debug("Templates table already exists. Continuing...")
            except Exception as e:
                self.log.error("There was an error creating the Templates table: {}".format(e))
                raise Exception(e)
            # Fields Table
            try:
                self.log.debug("Checking Fields table")
                self.log.debug("Checking Fields table")
                exists = self.query("SHOW TABLES LIKE 'Fields';")
                if len(exists) == 0:
                    self.log.debug("Fields table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Fields` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Template` INTEGER NOT NULL,
                            `Label` TEXT NOT NULL,
                            `Field_type` INT NOT NULL,
                            `Order` INTEGER NOT NULL,
                            FOREIGN KEY (`Template`)
                              REFERENCES `Templates`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `fields_template`
                          ON
                            `Fields`(`Template` ASC);
                        """
                    )
                else:
                    self.log.debug("Fields table already exists. Continuing...")
            except Exception as e:
                self.log.error("There was an error creating the Fields table: {}".format(e))
                raise Exception(e)
            # Fields_data Table
            try:
                self.log.debug("Checking Fields_data table")
                self.log.debug("Checking Fields_data table")
                exists = self.query("SHOW TABLES LIKE 'Fields_data';")
                if len(exists) == 0:
                    self.log.debug("Fields_data table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Fields_data` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Field` INTEGER NOT NULL,
                            `Key` VARCHAR(100) NOT NULL,
                            `Value` TEXT,
                            UNIQUE (
                              `Field`,
                              `Key`
                            ),
                            FOREIGN KEY (`Field`)
                              REFERENCES `Fields`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `items_data_field`
                          ON
                            `Fields_data`(`Field` ASC);
                        """
                    )
                else:
                    self.log.debug("Fields_data table already exists. Continuing...")
            except Exception as e:
                self.log.error("There was an error creating the Fields_data table: {}".format(e))
                raise Exception(e)
            # Values_group Table
            try:
                self.log.debug("Checking Values_group table")
                self.log.debug("Checking Values_group table")
                exists = self.query("SHOW TABLES LIKE 'Values_group';")
                if len(exists) == 0:
                    self.log.debug("Values_group table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Values_group` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Name` TEXT NOT NULL
                          );
                        """
                    )
                else:
                    self.log.debug("Values_group table already exists. Continuing...")
            except Exception as e:
                self.log.error("There was an error creating the Values_group table: {}".format(e))
                raise Exception(e)
            # Values Table
            try:
                self.log.debug("Checking Values table")
                self.log.debug("Checking Values table")
                exists = self.query("SHOW TABLES LIKE 'Values';")
                if len(exists) == 0:
                    self.log.debug("Values table doesn't exists. Creating...")
                    self.query(
                        """
                          CREATE TABLE `Values` (
                            `ID` INTEGER PRIMARY KEY AUTO_INCREMENT,
                            `Group` INTEGER NOT NULL,
                            `Value` TEXT NOT NULL,
                              `Order` INTEGER NOT NULL,
                            FOREIGN KEY (`Group`)
                              REFERENCES `Values_group`(`ID`)
                              ON DELETE CASCADE
                          );
                        """
                    )
                    self.query(
                        """
                          CREATE INDEX
                            `values_grp`
                          ON
                            `Values`(`Group` ASC);
                        """
                    )
                else:
                    self.log.debug("Values table already exists. Continuing...")
            except Exception as e:
                self.log.error("There was an error creating the Values table: {}".format(e))
                raise Exception(e)

            try:
                # Commiting all work
                self.conn.commit()
            except Exception as e:
                self.log.error("There was an error commiting all: {}".format(e))
                self.conn.rollback()
                raise Exception(e)

    # Delete database object
    def __del__(self):
        try:
            # Ping to reconnect if lost
            self.conn.ping()
            self.conn.commit()
            self.conn.close()
            return True
        except Exception as e:
            print("There was an error closing the database: {}".format(e))
            raise Exception(e)

    # Close database object
    def close(self):
        del self
        return True

    # Function to query to database
    def query(self, query, query_data=None, auto_commit=None):
        self.log.debug("Running query on database: {}".format(query))
        self.log.debug("Arguments: {}".format(query_data))
        # Ping to reconnect if lost
        self.conn.ping()
        if auto_commit is None:
            auto_commit = self.auto_commit

        try:
            ret_data = []

            execution = [
                query
            ]

            if query_data:
                execution.append(query_data)

            if auto_commit:
                self.log.debug("Autocommit mode")
                with self.conn:
                    c = self.conn.cursor()
                    data = c.execute(*execution)
                    self.conn.commit()
                    if isinstance(data, Iterable):
                        for qd in data:
                            ret_data.append(qd)
                    else:
                        ret_data.append([data])
                    c.close()

            else:
                self.log.debug("Creating cursor")
                c = self.conn.cursor()
                self.log.debug("Executing query")
                c.execute(*execution)
                self.log.debug("Getting return data")
                for qd in c:
                    ret_data.append(qd)
                if len(ret_data) == 0 and "insert" in query.lower():
                    ret_data.append(c.lastrowid)
                self.log.debug("Closing cursor")
                c.close()
                self.log.debug("Closed...")

            self.log.debug("Returning data: {}".format(ret_data))
            return ret_data
        except Exception as e:
            self.log.error("There was an error executing the query: {}".format(e))
            raise Exception(e)

    def _insert(self, dbase, items=None, values=None, auto_commit=None):
        if not values:
            return False

        query = "INSERT INTO `{}`".format(dbase)
        if items:
            query += "(`{}`)".format('`, `'.join(items))
        query += " VALUES (%s"
        query += ", %s" * (len(values)-1)
        query += ");"
        # print(query, values)
        return self.query(query, values, auto_commit=auto_commit)

    def _delete(self, dbase, where, auto_commit=None):
        query = "DELETE FROM `{}`".format(dbase)
        first = True
        values = []
        for item in where:
            values.append(item['value'])
            if first:
                query += " WHERE `{}` {} %s".format(
                    item['key'],
                    item.get('comparator', '=')
                )
                first = False
            else:
                if item.get('and', True):
                    query += " AND `{}` {} %s".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
                else:
                    query += " OR `{}` {} %s".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
        query += ";"
        # print(query, values)
        return self.query(query, values, auto_commit=auto_commit)

    def _update(self, dbase, updates, where, auto_commit=None):
        query = "UPDATE `{}` SET ".format(dbase)
        query += ", ".join("`{}` = %s".format(x['key']) for x in updates)
        values = [x['value'] for x in updates]

        first = True
        for item in where:
            values.append(item['value'])
            if first:
                query += " WHERE `{}` {} %s".format(
                    item['key'],
                    item.get('comparator', '=')
                )
                first = False
            else:
                if item.get('and', True):
                    query += " AND `{}` {} %s".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
                else:
                    query += " OR `{}` {} %s".format(
                        item['key'],
                        item.get('comparator', '=')
                    )

        query += ";"
        # print(query, values)
        return self.query(query, values, auto_commit=auto_commit)

    def _select(self, dbase, items=None, join=None, where=None, order=None):
        query = "SELECT "
        if items:
            first = True
            for item in items:
                if first:
                    first = False
                else:
                    query += ", "

                if type(item).__name__ == 'str':
                    if self.compiled_field_detect.match(item):
                        query += "`{}`".format(item)
                    else:
                        query += "{}".format(item)
                else:
                    query += "`{}`".format('`.`'.join(item))
        else:
            query += "*"

        query += " FROM `{}`".format(dbase)
        values = []
        if join:
            first = True
            query += " LEFT JOIN `{}`".format(join['table'])
            for item in join['where']:
                if first:
                    query += " ON"
                    first = False
                else:
                    query += " AND"

                if type(item['key']).__name__ == 'str':
                    query += ' "{}" ='.format(item['key'])
                else:
                    query += ' `' + '`.`'.join(item['key']) + '` ='

                if type(item['value']).__name__ == 'str':
                    query += ' %s'
                    values.append(item['value'])
                else:
                    query += ' `' + '`.`'.join(item['value']) + '`'

        if where:
            first = True
            for item in where:
                values.append(item['value'])
                if first:
                    query += " WHERE"
                    first = False
                else:
                    if item.get('and', True):
                        query += " AND"
                    else:
                        query += " OR"

                if type(item['key']).__name__ == 'str':
                    query += " `{}` {} %s".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
                else:
                    query += " `{}` {} %s".format(
                        '`.`'.join(item['key']),
                        item.get('comparator', '=')
                    )
        if order:
            first = True
            for item in order:
                if first:
                    query += " ORDER BY"
                    first = False
                else:
                    query += " ,"

                if type(item['key']).__name__ == 'str':
                    query += " `{}`".format(item['key'])
                else:
                    query += " `{}`".format(
                        '`.`'.join(item['key'])
                    )

                if item.get('asc', True) is True:
                    query += " ASC"
                elif item.get('asc', True) is False:
                    query += " DESC"
                else:
                    query += item.get('asc')
        query += ";"
        # print(query, values)
        return self.query(query, values, auto_commit=False)

    def _insert_or_update(self, dbase, items=None, values=None, conflict=None, auto_commit=None):
        if conflict is None:
            return False

        where = []
        for item in conflict:
            if item not in items:
                return False
            for i, v in enumerate(items):
                if v == item:
                    where.append({'key': item, 'value': values[i]})
        exists = self._select(
             dbase,
             items=conflict,
             where=where
        )

        if len(exists) > 0:
            updates = []
            for i, item in enumerate(items):
                updates.append({'key': item, 'value': values[i]})
            self._update(
                dbase,
                updates,
                where,
                auto_commit
            )
        else:
            self._insert(
                dbase,
                items=items,
                values=values,
                auto_commit=auto_commit
            )

    def file_to_blob(self, file_data):
        return Binary(file_data)

    def vacuum(self):
        try:
            self.query("VACUUM;")

        except Exception as e:
            self.log.error("There was an error executing VACUUM: {}".format(e))
