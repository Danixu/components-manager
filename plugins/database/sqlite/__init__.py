# -*- coding: utf-8 -*-

from . import __path__ as ROOT_PATH
import logging
import sqlite3
from os import path

import re
import wx

MOD_PATH = list(ROOT_PATH)[0]



class dbase:
    # Importing external functions
    from .category import category_add, category_rename, category_delete
    from .component import component_data
    from .datasheet import datasheet_clear, datasheet_set, datasheet_view
    from .field import field_add, field_delete, field_get_data
    from .file import file_add, file_del, file_export
    from .image import image_add, image_del
    from .template import template_add, template_del, template_get, template_ren

    def __init__(self, dbase_file, auto_commit = False, templates = False, parent = None):
      self.auto_commit = auto_commit
      self.compiled_ac_search = re.compile('.*(INSERT|UPDATE|DELETE).*', re.IGNORECASE)
      self.templates = templates
      self.log = logging.getLogger('MainWindow')
      self.parent = parent

      try:
        self.log.debug("Connecting to database")
        self.conn = sqlite3.connect(
            dbase_file, isolation_level='DEFERRED'
        )

        # Setting PRAGMA's
        self.conn.execute('''PRAGMA automatic_index = 1''')
        self.conn.execute('''PRAGMA foreign_keys = 1''')

        sql_file = "sqlite_templates.sql" if templates else "sqlite_components.sql"

        if path.isfile("{}/{}".format(MOD_PATH, sql_file)):
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


    def selection_to_html(self, id, template_data = None, category = False):
        if self.templates:
            self.log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False

        html = """
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

        if category:
            category = self.query(
                "SELECT Name FROM Categories WHERE id = ?",
                (
                    id,
                )
            )

            parentOfCats = self.query(
                "SELECT COUNT(id) FROM Categories WHERE Parent = ?",
                (
                    id,
                )
            )
            parentOfComp = self.query(
                "SELECT COUNT(id) FROM Components WHERE Category = ?",
                (
                    id,
                )
            )

            html += "<h1>{}</h1>\n<table>\n".format(category[0][0])

            html += "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">{}</td></tr>\n".format("Subcategorías", parentOfCats[0][0])
            html += "<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">{}</td></tr>\n".format("Componentes", parentOfComp[0][0])

            html += "</table>"

        else:
            component_data = self.component_data(self.parent, id)
            if not component_data:
                self.log.warning(
                    "The component type {} was not found for component {}.".format(
                        component[0][1],
                        component[0][0]
                    )
                )
                html += "<tr><td> Tipo de componente no encontrado. <br>Por favor, verifica si se borró el fichero JSON de la carpeta components.</td>/tr>"
            else:
                html += "<h1>{}</h1>\n<table>\n".format(component_data['name'])
                first = True

                for item, data in component_data.get('data_real', {}).items():
                    if first:
                        html += "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">{}</td></tr>\n".format(data['key'], data['value'])
                        first = False
                    else:
                        html += "<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">{}</td></tr>\n".format(data['key'], data['value'])

            html += "</table>"

        html += "</center></body>"
        return html


    def vacuum(self):
        try:
            self.query("VACUUM;")

        except Exception as e:
            self.log.error("There was an error executing VACUUM: {}".format(e))