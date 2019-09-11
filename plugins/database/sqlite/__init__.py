# -*- coding: utf-8 -*-

from . import __path__ as ROOT_PATH
from logging import getLogger
from sqlite3 import connect
from os.path import isfile
from re import compile, IGNORECASE

MOD_PATH = list(ROOT_PATH)[0]


class dbase:
    # Importing external functions
    from .category import category_add, category_rename, category_delete, category_data_html
    from .component import component_data, component_data_html
    from .datasheet import datasheet_clear, datasheet_set, datasheet_view
    from .field import field_add, field_delete, field_get_data
    from .file import file_add, file_del, file_export
    from .image import image_add, image_del
    from .template import template_add, template_del, template_get, template_ren

    header = """
        <head>
          <style>
            body {background-color: powderblue;}
            table {
              border-spacing: 5px; 
              width: 90%;
            }
            td.left-first
            {
              border-top: 2px dotted black;
              border-bottom: 2px dotted black;
              width: 35%;
            }
            td.right-first
            {
              border-top: 2px dotted black;
              border-bottom: 2px dotted black;
              width: 65%;
            }
            td.left
            {
              border-bottom: 2px dotted black;
              width: 35%;
            }
            td.right
            {
              border-bottom: 2px dotted black;
              width: 65%;
            }
            tr:nth-child(even)
            {
              background: #CCC;
            }
          </style>
        </head>
      <body>
        <center>

    """
    footer = """
            </table>
          </center>
        </body>
    """

    def __init__(self, dbase_file, auto_commit = False, templates = False, parent = None):
      self.auto_commit = auto_commit
      self.compiled_ac_search = compile('.*(INSERT|UPDATE|DELETE).*', IGNORECASE)
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


    ## Delete database object
    def __del__(self):
      try:
        self.conn.commit()
        self.conn.close()
        return True
      except Exception as e:
        print("There was an error closing the database: {}".format(e))
        raise Exception(e)


    ## Close database object
    def close(self):
      del self
      return True


    ## Function to query to database
    def query(self, query, query_data = None, auto_commit = None):
      self.log.debug("Running query on database: {}".format(query))
      self.log.debug("Arguments: {}".format(query_data))
      if auto_commit == None:
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


    def vacuum(self):
        try:
            self.query("VACUUM;")

        except Exception as e:
            self.log.error("There was an error executing VACUUM: {}".format(e))