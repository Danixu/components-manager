# -*- coding: utf-8 -*-

from . import __path__ as ROOT_PATH
import logging
import sqlite3
import globals

log = logging.getLogger('cManager')
MOD_PATH = list(ROOT_PATH)[0]

class dbase:
    def __init__(self, dbase_file):
      try:
        log.debug("Connecting to database")
        self.conn = sqlite3.connect(
            dbase_file,
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        log.debug("Running initialization script")
        with open("{}/sqlite.sql".format(MOD_PATH), 'r') as sql_file:
          cursor = self.conn.cursor()
          cursor.executescript(sql_file.read())
          cursor.close()
          self.conn.commit()

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
        log.debug("Getting return data")
        for qd in c:
          ret_data.append(qd)

        log.debug("Closing cursor")
        c.close()
        return ret_data
      except Exception as e:
        log.error("There was an error executing the query: {}".format(e))
        raise Exception(e)
        
    def add_category(self, name, parent = -1):
      log.debug("Adding category: {}".format(name))
      try:
        self.query("INSERT INTO Category(Parent, Name) VALUES (?, ?)", (parent, name))
        self.conn.commit()
        return True
       
      except Exception as e:
        log.error("There was an error adding the category: {}".format(e))
        return False
        
    def rename_category(self, name, id):
      log.debug("Renaming category to {}".format(name))
      try:
        self.query("UPDATE Category SET Name = ? WHERE id = ?", (name, id))
        self.conn.commit()
        return True
       
      except Exception as e:
        log.error("There was an error adding the category: {}".format(e))
        return False
        
    def add_component(self, name, data, parent):
        log.debug("Adding component: {}".format(name))
        try:
            self.query(
                "INSERT INTO Components(Category, Name, Template) VALUES (?, ?, ?)",
                (parent, name, data.get("template", None))
            )
            self.conn.commit()
            return True
           
        except Exception as e:
            log.error("There was an error adding the component: {}".format(e))
            return False
      
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
            
            
    def selection_to_html(self, id, components_db, category = False):
        html = """
        <head>
          <style>
            body {background-color: powderblue;}
            table { border-spacing: 5px; }
            td.left-first
            {
              border-top: 2px dotted black;
              border-bottom: 2px dotted black;
            }
            td.right-first
            {
              border-top: 2px dotted black;
              border-bottom: 2px dotted black;
            }
            td.left
            {
              border-bottom: 2px dotted black;
            }
            td.right
            {
              border-bottom: 2px dotted black;
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
        
        html += "<h1>{}</h1>\n<table>\n".format(component[0][2])
        first = True
        for item, data in components_db[component[0][3]].get('data', {}).items():
            name = data.get("text")
            value = component_data.get(item, "")
            if first:
                html += "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">{}</td></tr>\n".format(name, value if value != "" else "Sin información")
                first = False
            else:
                html += "<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">{}</td></tr>\n".format(name, value if value != "" else "Sin información")
        
        html += "</center></table></body>"        
        print(html)
        return html