# -*- coding: utf-8 -*-

from . import __path__ as ROOT_PATH
from logging import getLogger
from sqlite3 import connect, Binary
from os.path import isfile
from re import compile, IGNORECASE

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

    def __init__(self, dbase_file, auto_commit=False, templates=False, parent=None):
        self.auto_commit = auto_commit
        self.compiled_ac_search = compile(r'.*(INSERT|UPDATE|DELETE).*', IGNORECASE)
        self.compiled_field_detect = compile(r'^[\w\d\s\-_\.]+$', IGNORECASE)
        self.templates = templates
        self.log = getLogger('MainWindow')
        self.parent = parent

        try:
            self.log.debug("Connecting to database")
            self.conn = connect(
                dbase_file, isolation_level='DEFERRED'
            )

            # Setting PRAGMA's
            self.conn.execute('''PRAGMA automatic_index = 1''')
            self.conn.execute('''PRAGMA foreign_keys = 1''')

            sql_file = "sqlite_templates.sql" if templates else "sqlite_components.sql"

            if isfile("{}/{}".format(MOD_PATH, sql_file)):
                self.log.debug("Running initialization script")
                with open("{}/{}".format(MOD_PATH, sql_file), 'r') as sql_file:
                    cursor = self.conn.cursor()
                    cursor.executescript(sql_file.read())
                    cursor.close()
                    self.conn.commit()
            else:
                self.log.debug("There's no startup script")

        except Exception as e:
            self.log.error("There was an error connecting to sqlite dbase: {}".format(e))
            raise Exception(e)

    # Delete database object
    def __del__(self):
        try:
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
                    for qd in self.conn.execute(*execution):
                        ret_data.append(qd)

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

        query = "INSERT INTO [{}]".format(dbase)
        if items:
            query += "([{}])".format('], ['.join(items))
        query += " VALUES (?"
        query += ", ?" * (len(values)-1)
        query += ");"
        # print(query, values)
        return self.query(query, values, auto_commit=auto_commit)

    def _delete(self, dbase, where, auto_commit=None):
        query = "DELETE FROM [{}]".format(dbase)
        first = True
        values = []
        for item in where:
            values.append(item['value'])
            if first:
                query += " WHERE [{}] {} ?".format(
                    item['key'],
                    item.get('comparator', '=')
                )
                first = False
            else:
                if item.get('and', True):
                    query += " AND [{}] {} ?".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
                else:
                    query += " OR [{}] {} ?".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
        query += ";"
        # print(query, values)
        return self.query(query, values, auto_commit=auto_commit)

    def _update(self, dbase, updates, where, auto_commit=None):
        query = "UPDATE [{}] SET ".format(dbase)
        query += ", ".join("[{}] = ?".format(x['key']) for x in updates)
        values = [x['value'] for x in updates]

        first = True
        for item in where:
            values.append(item['value'])
            if first:
                query += " WHERE [{}] {} ?".format(
                    item['key'],
                    item.get('comparator', '=')
                )
                first = False
            else:
                if item.get('and', True):
                    query += " AND [{}] {} ?".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
                else:
                    query += " OR [{}] {} ?".format(
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
                        query += "[{}]".format(item)
                    else:
                        query += "{}".format(item)
                else:
                    query += "[{}]".format('].['.join(item))
        else:
            query += "*"

        query += " FROM [{}]".format(dbase)
        values = []
        if join:
            first = True
            query += " LEFT JOIN [{}]".format(join['table'])
            for item in join['where']:
                if first:
                    query += " ON"
                    first = False
                else:
                    query += " AND"

                if type(item['key']).__name__ == 'str':
                    query += ' "{}" ='.format(item['key'])
                else:
                    query += ' [' + '].['.join(item['key']) + '] ='

                if type(item['value']).__name__ == 'str':
                    query += ' ?'
                    values.append(item['value'])
                else:
                    query += ' [' + '].['.join(item['value']) + ']'

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
                    query += " [{}] {} ?".format(
                        item['key'],
                        item.get('comparator', '=')
                    )
                else:
                    query += " [{}] {} ?".format(
                        '].['.join(item['key']),
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
                    query += " [{}]".format(item['key'])
                else:
                    query += " [{}]".format(
                        '].['.join(item['key'])
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
