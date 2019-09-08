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
    self.query("UPDATE Categories SET Name = ? WHERE id = ?", (name, id))
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