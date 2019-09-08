# -*- coding: utf-8 -*-


def datasheet_clear(self, componentID):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    try:
        self.log.debug("Running clear datasheet query")
        self.query("UPDATE Files SET Datasheet = 0 WHERE Component = ? AND Datasheet = 1", (componentID,))
        self.log.debug("Dataset query executed correctly")
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error clearing the component datasheet: {}".format(e))
        self.conn.rollback()
        return False


def datasheet_set(self, componentID, fileID):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    try:
        self.log.debug("Clearing datasheet info")
        self.datasheet_clear(componentID)
        self.log.debug("Setting the new datasheet File")
        self.query("UPDATE Files SET Datasheet = 1 where ID = ?", (fileID,))
        self.log.debug("Datasheet setted correctly")
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error clearing the component datasheet: {}".format(e))
        self.conn.rollback()
        return False
        

def datasheet_view(self, componentID, fName = None):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    exists = self.query("SELECT ID FROM Files WHERE Component = ? AND Datasheet = 1", (componentID,))
    if len(exists) > 0:
        try:
            return self.file_export(exists[0][0])
        except Exception as e:
            self.log.error("There was an error writing datasheet temporary file: {}".format(e))
            return False
    else:
      return False