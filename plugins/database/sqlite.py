# -*- coding: utf-8 -*-

from . import __path__ as ROOT_PATH
import logging
import sqlite3
import globals
import os
import re
import tempfile

log = logging.getLogger('cManager')
MOD_PATH = list(ROOT_PATH)[0]

class dbase:
    def __init__(self, dbase_file, auto_commit = False):
      self.auto_commit = auto_commit
      self.compiled_ac_search = re.compile('.*(INSERT|UPDATE|DELETE).*', re.IGNORECASE)
    
      try:
        log.debug("Connecting to database")
        self.conn = sqlite3.connect(
            dbase_file,
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        if os.path.isfile("{}/sqlite.sql".format(MOD_PATH)):
            log.debug("Running initialization script")
            with open("{}/sqlite.sql".format(MOD_PATH), 'r') as sql_file:
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
      log.debug("Deleting database object")
      try:
        self.conn.commit()
        self.conn.close()
        return True
      except Exception as e:
        log.error("There was an error closing the database: {}".format(e))
        raise Exception(e)

    
    ## Close database object
    def close(self):
      del self
      return True


    ## Function to query to database
    def query(self, query, query_data = None):
      log.debug("Running query on database: {}".format(query))
      log.debug("Arguments: {}".format(query_data))
      try:
        ret_data = []
        log.debug("Creating cursor")
        c = self.conn.cursor()
        log.debug("Executing query")
        if query_data:
          c.execute(query, query_data)
        else:
          c.execute(query)
          
        if self.auto_commit and self.compiled_ac_search.match(query):
            log.debug("Auto Commit is True, so commiting changes...")
            self.conn.commit()
            
        log.debug("Getting return data")
        for qd in c:
          ret_data.append(qd)

        log.debug("Closing cursor")
        c.close()
        return ret_data
      except Exception as e:
        log.error("There was an error executing the query: {}".format(e))
        raise Exception(e)


    def category_add(self, name, parent = -1):
      log.debug("Adding category: {}".format(name))
      try:
        self.query("INSERT INTO Categories(Parent, Name) VALUES (?, ?)", (parent, name))
        self.conn.commit()
        return True
       
      except Exception as e:
        log.error("There was an error adding the category: {}".format(e))
        return False


    def category_rename(self, name, id):
      log.debug("Renaming category to {}".format(name))
      try:
        self.query("UPDATE Categories SET Name = ? WHERE id = ?", (name, id))
        self.conn.commit()
        return True
       
      except Exception as e:
        log.error("There was an error adding the category: {}".format(e))
        return False


    def component_add(self, name, data, parent):
        log.debug("Adding component: {}".format(name))
        try:
            self.query(
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
            self.conn.commit()
            return True
           
        except Exception as e:
            log.error("There was an error adding the component: {}".format(e))
            return False


    def component_data_parse(self, id, text, component_data = None):
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

      
    def image_add(self, image, size, parent, category):
        try:
            image = globals.imageResize(image, nWidth=size[0], nHeight=size[1])
            
        except IOError:
            wx.LogError("Cannot open file '%s'." % newfile)
            
        try:
            self.query(
                "INSERT INTO Images(Parent, Category, Image) VALUES (?, ?, ?)",
                (
                    parent, 
                    category, 
                    sqlite3.Binary(image.getvalue())
                )
            )
            self.conn.commit()
            return True
           
        except Exception as e:
            log.error("There was an error adding the image: {}".format(e))
            return False


    def image_delete(self, imageID):
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
            return False
            
            
            
    def datasheet_add(self, fName, componentID):
        if os.path.isfile(fName):
            filename, file_extension = os.path.splitext(fName)
            try:
                exists = self.query("SELECT * FROM Datasheets WHERE Component = ?", (componentID,))
                with open(fName, 'rb') as fIn:
                    _blob = fIn.read()
                    if len(exists) == 0:
                        self.query(
                            "INSERT INTO Datasheets VALUES (?, ?, ?);",
                            (
                                componentID,
                                sqlite3.Binary(_blob),
                                file_extension
                            )
                        )
                        
                        return True
                    else:
                        self.query(
                            "UPDATE Datasheets SET File = ?, Extension = ? WHERE Component = ?;",
                            (
                                sqlite3.Binary(_blob),
                                file_extension,
                                componentID
                            )
                        )
                        
                        return True
                    
                
            except Exception as e:
                log.error("There was an error opening the datasheet file: {}".format(e))
                return False

        else:
            log.error("The file {} does not exists".format(pdf))
            return False

            
    def datasheet_delete(self, componentID):
        try:
            self.query(
                "DELETE FROM Datasheets WHERE Component = ?",
                (
                    componentID,
                )
            )
            self.conn.commit()
            return True
           
        except Exception as e:
            log.error("There was an error deleting the datasheet: {}".format(e))
            return False
            
    def datasheet_export(self, componentID):
        exists = self.query("SELECT * FROM Datasheets WHERE Component = ?", (componentID,))
        if len(exists) > 0:
            try:
                tempName = next(tempfile._get_candidate_names())
                tempFolder = tempfile._get_default_tempdir()
                
                # La extensión la sacamos de la BBDD en l función
                tempFilename = os.path.join(
                    tempFolder,
                    tempName +
                    exists[0][2]
                )
                
                with open(tempFilename, 'wb') as fOut:
                    fOut.write(exists[0][1])
                
                return tempFilename
            except Exception as e:
                log.error("There was an error writing datasheet temporary file: {}".format(e))
                return False
        else:
          return False
        
            
    def selection_to_html(self, id, components_db = None, category = False):
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
            component = self.query(
                "SELECT * FROM Components WHERE id = ?",
                (
                    id,
                )
            )
            
            component_query = self.query(
                "SELECT * FROM Components_Data WHERE Component = ?",
                (
                    id,
                )
            )
            
            component_data = {}
            for item in component_query:
                component_data.update({ item[2]: item[3] })
            
            html += "<h1>{}</h1>\n<table>\n".format(self.component_data_parse(id, component[0][2], component_data))
            first = True
            if not components_db.get(component[0][5], False):
                log.warning(
                    "The component type {} was not found for component {}.".format(
                        component[0][5],
                        component[0][2]
                    )
                )
                html += "<tr><td> Tipo de componente no encontrado. <br>Por favor, verifica si se borró el fichero JSON de la carpeta components.</td>"
                
            else:
                for item, data in components_db.get(component[0][5]).get('data', {}).items():
                    name = data.get("text")
                    
                    if first:
                        html += "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">".format(name)
                        first = False
                    else:
                        html += "<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">".format(name)
                        
                    first = True
                    for cont, cont_data in data.get('controls', {}).items():
                        control_name = "{}_{}".format(item, cont)    
                        value = component_data.get(control_name, "")
                        if not cont_data.get('nospace', False) and not first:
                            html += " - "
                            
                        if first:
                            first = False
                        
                        html += "{}".format(
                            value if value != "" else "-",
                        )
                        
                    html += "</td></tr>\n"
                    
            html += "</table>"
            
        html += "</center></body>"
        return html