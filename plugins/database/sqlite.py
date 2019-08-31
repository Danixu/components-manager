# -*- coding: utf-8 -*-

from . import __path__ as ROOT_PATH
from modules import imageResizeWX, compressionTools
import logging
import sqlite3
from os import path
import re
import tempfile
import wx

log = logging.getLogger('MainWindow')
MOD_PATH = list(ROOT_PATH)[0]

class dbase:
    def __init__(self, dbase_file, auto_commit = False, templates = False):
      self.auto_commit = auto_commit
      self.compiled_ac_search = re.compile('.*(INSERT|UPDATE|DELETE).*', re.IGNORECASE)
      self.templates = templates

      try:
        log.debug("Connecting to database")
        self.conn = sqlite3.connect(
            dbase_file, isolation_level='DEFERRED'
        )

        # Setting PRAGMA's
        self.conn.execute('''PRAGMA automatic_index = 1''')
        self.conn.execute('''PRAGMA foreign_keys = 1''')
        
        sql_file = "sqlite_templates.sql" if templates else "sqlite_components.sql"

        if path.isfile("{}/{}".format(MOD_PATH, sql_file)):
            log.debug("Running initialization script")
            with open("{}/{}".format(MOD_PATH, sql_file), 'r') as sql_file:
              cursor = self.conn.cursor()
              cursor.executescript(sql_file.read())
              cursor.close()
              self.conn.commit()
        else:
            log.debug("There's no startup script")

      except Exception as e:
        log.error("There was an error connecting to sqlite dbase: {}".format(e))
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
      log.debug("Running query on database: {}".format(query))
      log.debug("Arguments: {}".format(query_data))
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
            log.debug("Autocommit mode")
            with self.conn:
                for qd in self.conn.execute(*execution):
                    ret_data.append(qd)

        else:
            log.debug("Creating cursor")
            c = self.conn.cursor()
            log.debug("Executing query")
            c.execute(*execution)
            log.debug("Getting return data")
            for qd in c:
                ret_data.append(qd)
            if len(ret_data) == 0 and "insert" in query.lower():
                ret_data.append(c.lastrowid)
            log.debug("Closing cursor")
            c.close()

        return ret_data
      except Exception as e:
        log.error("There was an error executing the query: {}".format(e))
        raise Exception(e)


    def category_add(self, name, parent = -1):
      log.debug("Adding category: {}".format(name))
      try:
        category_id = self.query("INSERT INTO Categories(Parent, Name) VALUES (?, ?)", (parent, name))
        self.conn.commit()
        return category_id

      except Exception as e:
        log.error("There was an error adding the category: {}".format(e))
        self.conn.rollback()
        return False


    def category_rename(self, name, id):
      log.debug("Renaming category to {}".format(name))
      try:
        self.query("UPDATE Categories SET Name = ? WHERE id = ?", (name, id))
        self.conn.commit()
        return True

      except Exception as e:
        log.error("There was an error adding the category: {}".format(e))
        self.conn.rollback()
        return False

    def category_delete(self, id):
      log.debug("Deleting category {}".format(id))
      try:
        self.query("DELETE FROM Categories WHERE id = ?", (id,))
        self.conn.commit()
        return True

      except Exception as e:
        log.error("There was an error deleting the category: {}".format(e))
        self.conn.rollback()
        return False
        
        
    def template_add(self, name, parent = -1):
      if not self.templates:
            log.warning(
                "This function is not compatible with global" +
                " databases"
            )
            return False
    
      log.debug("Adding template: {}".format(name))
      try:
        template_id = self.query("INSERT INTO Templates(Category, Name) VALUES (?, ?)", (parent, name))
        self.conn.commit()
        return template_id

      except Exception as e:
        log.error("There was an error adding the template: {}".format(e))
        self.conn.rollback()
        return False


    def template_rename(self, name, id):
      if not self.templates:
            log.warning(
                "This function is not compatible with global" +
                " databases"
            )
            return False
    
      log.debug("Renaming template to {}".format(name))
      try:
        self.query("UPDATE Templates SET Name = ? WHERE id = ?", (name, id))
        self.conn.commit()
        return True

      except Exception as e:
        log.error("There was an error adding the template: {}".format(e))
        self.conn.rollback()
        return False

    def template_delete(self, id):
      if not self.templates:
            log.warning(
                "This function is not compatible with global" +
                " databases"
            )
            return False
    
      log.debug("Deleting template {}".format(id))
      try:
        self.query("DELETE FROM Templates WHERE id = ?", (id,))
        self.conn.commit()
        return True

      except Exception as e:
        log.error("There was an error deleting the template: {}".format(e))
        self.conn.rollback()
        return False
        
    
    def field_add(self, template, label, type, order, width = None):
      if not self.templates:
            log.warning(
                "This function is not compatible with global" +
                " databases"
            )
            return False
    
      log.debug("Adding field: {}".format(label))
      try:
          field_id = self.query("INSERT INTO Fields VALUES (NULL, ?, ?, ?, ?);",
              (
                  template,
                  label,
                  type,
                  order
              )
          )

          self.query("INSERT INTO Fields_data VALUES(NULL, ?, ?, ?);",
              (
                  field_id[0],
                  "width",
                  width
              )
          )
          self.conn.commit()
          return field_id

      except Exception as e:
          log.error("There was an error adding the field: {}".format(e))
          self.conn.rollback()
          return False


    def field_delete(self, id):
      if not self.templates:
            log.warning(
                "This function is not compatible with global" +
                " databases"
            )
            return False
    
      log.debug("Deleting group {}".format(id))
      try:
        self.query("DELETE FROM Fields WHERE ID = ?", (id,))
        self.conn.commit()
        return True

      except Exception as e:
        log.error("There was an error deleting the group: {}".format(e))
        self.conn.rollback()
        return False
        
        
    def field_get_data(self, id):
        try:
            query_f = """SELECT 
                        *
                      FROM 
                        Fields 
                      WHERE
                        ID = ?;
                    """
            query_fd = """SELECT 
                        *
                      FROM 
                        Fields_data 
                      WHERE
                        Field = ?;
                    """
            field = self.query(query_f, (id,))
            field_data = self.query(query_fd, (id,))
            
            field_return = {}
            for item in field:
                field_return['ID'] = id
                field_return['label'] = item[2]
                field_return['field_type'] = item[3]
                field_return['field_order'] = item[4]
                
            field_return['field_data'] = {}
            for item in field_data:
                field_return['field_data'][item[2]] = item[3]
                
            return field_return
        except Exception as e:
            log.error("There was an error processing field data: {}".format(e))
            return False


    def component_add(self, name, data, parent):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        log.debug("Adding component: {}".format(name))
        try:
            component_id = self.query(
                """INSERT INTO Components(
                    Category,
                    Name,
                    New_amount,
                    Recycled_amount,
                    Template
                ) VALUES (?, ?, ?, ?, ?)

                """,
                (
                    parent, 
                    name, 
                    data.get("new_amount", 0),
                    data.get("recycled_amount", 0),
                    data.get("template", None)
                )
            )
            if component_id:
                for item, data in data.get('component_data', {}).items():
                    if not item in ["name", "template", "new_amount", "recycled_amount"]:
                        self.query(
                            "INSERT INTO Components_Data(Component, Key, Value) VALUES (?, ?, ?);",
                            (
                              component_id[0],
                              item,
                              str(data)
                            )
                        )

                self.conn.commit()
                return component_id
            else:
                self.conn.rollback()
                return False

        except Exception as e:
            log.error("There was an error adding the component: {}".format(e))
            self.conn.rollback()
            return False


    def component_data_parse(self, id, text, component_data = None):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        pattern = re.compile("\%\((\w+)\)")

        if pattern.search(text):
            if not component_data:
                component_query = self.query(
                    "SELECT * FROM Components_Data WHERE Component = ?",
                    (
                        id,
                    )
                )

                component_data = {}
                for item in component_query:
                    component_data.update({ item[2]: item[3] })

            values = pattern.findall(text)
            for item in values:
                text = text.replace("%({})".format(item), component_data.get(item, ""))
        return text


    def image_add(self, image, size, parent, category, format = wx.BITMAP_TYPE_PNG, quality = None, compression = compressionTools.COMPRESSION_FMT.LZMA):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        log.debug("Adding image:")
        log.debug("   format: {}".format(format))
        log.debug("   quality: {}".format(quality))
        log.debug("   compression: {}".format(compression))
        try:
            color = (-1, -1, -1)
            if format == wx.BITMAP_TYPE_JPEG or format == wx.BITMAP_TYPE_BMP:
                log.debug("Image has not transparent support")
                color = (255, 255, 255)
            image = imageResizeWX.imageResizeWX(
                image, 
                nWidth=size[0], 
                nHeight=size[1], 
                out_format = format, 
                compression = quality, 
                color=color
            )
            image_data = compressionTools.compressData(image.getvalue(), compression)

        except IOError:
            wx.LogError("Cannot open file '%s'." % newfile)

        query = ""
        if category:
            query = "INSERT INTO Images(Category_id, Image, Imagecompression) VALUES (?, ?, ?);"
        else:
            query = "INSERT INTO Images(Component_id, Image, Imagecompression) VALUES (?, ?, ?);"
        try:
            self.query(query,
                (
                    parent,
                    sqlite3.Binary(image_data),
                    compression
                )
            )
            self.conn.commit()
            return True

        except Exception as e:
            log.error("There was an error adding the image: {}".format(e))
            self.conn.rollback()
            return False


    def image_delete(self, imageID):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        try:
            self.query(
                "DELETE FROM Images WHERE ID = ?",
                (
                    imageID,
                )
            )
            self.conn.commit()
            return True

        except Exception as e:
            log.error("There was an error deleting the image: {}".format(e))
            self.conn.rollback()
            return False


    def datasheet_view(self, componentID, fName = None):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        exists = self.query("SELECT ID FROM Files WHERE Component = ? AND Datasheet = 1", (componentID,))
        if len(exists) > 0:
            try:
                return self.file_export(exists[0][0])
            except Exception as e:
                log.error("There was an error writing datasheet temporary file: {}".format(e))
                return False
        else:
          return False


    def datasheet_clear(self, componentID):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        try:
            log.debug("Running clear datasheet query")
            self.query("UPDATE Files SET Datasheet = 0 WHERE Component = ? AND Datasheet = 1", (componentID,))
            log.debug("Dataset query executed correctly")
            self.conn.commit()
            return True

        except Exception as e:
            log.error("There was an error clearing the component datasheet: {}".format(e))
            self.conn.rollback()
            return False


    def datasheet_set(self, componentID, fileID):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        try:
            log.debug("Clearing datasheet info")
            self.datasheet_clear(componentID)
            log.debug("Setting the new datasheet File")
            self.query("UPDATE Files SET Datasheet = 1 where ID = ?", (fileID,))
            log.debug("Datasheet setted correctly")
            self.conn.commit()
            return True

        except Exception as e:
            log.error("There was an error clearing the component datasheet: {}".format(e))
            self.conn.rollback()
            return False


    def file_add(self, fName, componentID, datasheet = False, compression = compressionTools.COMPRESSION_FMT.LZMA):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        if path.isfile(fName):
            filename = path.basename(fName)
            try:
                with open(fName, 'rb') as fIn:
                    _blob = compressionTools.compressData(fIn.read(), compression)
                    file_id = self.query(
                        "INSERT INTO Files VALUES (?, ?, ?, ?);",
                        (
                            None,
                            componentID,
                            filename,
                            datasheet
                        )
                    )
                    file_data = self.query(
                        "INSERT INTO Files_blob VALUES (?, ?, ?);",
                        (
                            file_id[0],
                            sqlite3.Binary(_blob),
                            int(compression)
                        )
                    )

                    self.conn.commit()
                    return True

            except Exception as e:
                log.error("There was an error adding the file to database: {}".format(e))
                self.conn.rollback()
                return False

        else:
            log.error("The file {} does not exists".format(pdf))
            return False


    def file_del(self, fileID):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        try:
            self.query(
                "DELETE FROM Files WHERE ID = ?;",
                (
                    fileID,
                )
            )
            self.conn.commit()
            return True

        except Exception as e:
            log.error("There was an error deleting then file from database")
            self.conn.rollback()
            return False


    def file_export(self, fileID, fName = None):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        exists = self.query("SELECT Filename FROM Files WHERE ID = ?", (fileID,))
        if len(exists) > 0:
            try:
                blob_data = self.query("SELECT Filedata, Filecompression FROM Files_blob WHERE File_id = ?", (fileID,))
                if not fName:
                    tempName = next(tempfile._get_candidate_names())
                    tempFolder = tempfile._get_default_tempdir()

                    # La extensión la sacamos del nombre de fichero en la BBDD
                    filename, extension = path.splitext(exists[0][0])
                    fName = path.join(
                        tempFolder,
                        tempName +
                        extension
                    )

                with open(fName, 'wb') as fOut:
                    fOut.write(compressionTools.decompressData(blob_data[0][0], blob_data[0][1]))

                return fName
            except Exception as e:
                log.error("There was an error writing file temporary file: {}".format(e))
                return False
        else:
          return False

    def component_fields(self, id, components_db = None):
        if self.templates:
            log.warning(
                "This function is not compatible with templates" +
                " databases"
            )
            return False
    
        sql_data = self.query("""
            SELECT
                Components.Name, 
                Components.Template, 
                Components_Data.Key, 
                Components_Data.Value 
            FROM 
                Components 
            INNER JOIN 
                Components_Data 
            ON 
                Components.ID = Components_Data.Component 
            WHERE 
                Components.ID = ?
            ;""", (id,)
        )

        component_data = {
            "raw_data": {},
            "processed_data": {}
        }
        for item in sql_data:
            if not component_data.get('name', False):
                component_data['name'] = item[0]
            if not component_data.get('template', False):
                component_data['template'] = item[1]
                if not components_db.get(item[1], False):
                    log.warning(
                        "The component type {} was not found for component id {}.".format(
                            item[1],
                            id
                        )
                    )
                    return False

            component_data['raw_data'][item[2]] = item[3]

        for item, data in components_db.get(component_data['template']).get('data', {}).items():
            name = data.get("text")
            text = ""
            first = True
            for cont, cont_data in data.get('controls', {}).items():
                control_name = "{}_{}".format(item, cont)
                value = component_data['raw_data'].get(control_name, "")
                if not cont_data.get('nospace', False) and not first:
                    text += " - "

                if first:
                    first = False

                text += "{}".format(
                    value if value != "" else "-",
                )

            component_data['processed_data'][name] = text

        component_data['name'] = self.component_data_parse(
            id, 
            component_data['name'], 
            component_data = component_data['raw_data']
        )
        return component_data


    def selection_to_html(self, id, components_db = None, category = False):
        if self.templates:
            log.warning(
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
            component_data = self.component_fields(id, components_db)
            if not component_data:
                log.warning(
                    "The component type {} was not found for component {}.".format(
                        component[0][1],
                        component[0][0]
                    )
                )
                html += "<tr><td> Tipo de componente no encontrado. <br>Por favor, verifica si se borró el fichero JSON de la carpeta components.</td>/tr>"
            else:
                html += "<h1>{}</h1>\n<table>\n".format(component_data['name'])
                first = True

                for item, data in component_data.get('processed_data', {}).items():
                    if first:
                        html += "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">{}</td></tr>\n".format(item, data)
                        first = False
                    else:
                        html += "<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">{}</td></tr>\n".format(item, data)

            html += "</table>"

        html += "</center></body>"
        return html


    def vacuum(self):
        try:
            self.query("VACUUM;")

        except Exception as e:
            log.error("There was an error executing VACUUM: {}".format(e))