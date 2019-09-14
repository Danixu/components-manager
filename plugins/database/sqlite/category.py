# -*- coding: utf-8 -*-

def category_add(self, name, parent = -1):
  self.log.debug("Adding category: {}".format(name))
  try:
    category_id = self.query("INSERT INTO Categories(Parent, Name) VALUES (?, ?)", (parent, name))
    self.conn.commit()
    return category_id

  except Exception as e:
    self.log.error("There was an error adding the category: {}".format(e))
    self.conn.rollback()
    return False


def category_rename(self, name, id):
  self.log.debug("Renaming category to {}".format(name))
  try:
    self.query(
        """UPDATE [Categories] SET [Name] = ? WHERE [ID] = ?;""", 
        (
            name, 
            id
        )
    )
    self.conn.commit()
    return True

  except Exception as e:
    self.log.error("There was an error adding the category: {}".format(e))
    self.conn.rollback()
    return False

def category_delete(self, id):
  self.log.debug("Deleting category {}".format(id))
  try:
    self.query("DELETE FROM Categories WHERE id = ?", (id,))
    self.conn.commit()
    return True

  except Exception as e:
    self.log.error("There was an error deleting the category: {}".format(e))
    self.conn.rollback()
    return False


def category_data_html(self, id):
    html = ""
    category = self.query(
        """SELECT [Name] FROM [Categories] WHERE [ID] = ?;""",
        (
            id,
        )
    )

    parentOfCats = self.query(
        """SELECT COUNT([ID]) FROM [Categories] WHERE [Parent] = ?""",
        (
            id,
        )
    )
    parentOfComp = self.query(
        """SELECT COUNT([ID]) FROM [Components] WHERE [Category] = ?""",
        (
            id,
        )
    )

    html += "<h1>{}</h1>\n<table>\n".format(category[0][0])

    html += "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">{}</td></tr>\n".format("Subcategorías", parentOfCats[0][0])
    html += "<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">{}</td></tr>\n".format("Componentes", parentOfComp[0][0])

    return self.header + html + self.footer