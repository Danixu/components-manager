# -*- coding: utf-8 -*-


def field_add(self, template, label, type, order, width=None):
    if not self.templates:
        self.log.warning(
          "This function is not compatible with global" +
          " databases"
        )
        return False

    self.log.debug("Adding field: {}".format(label))
    try:
        field_id = self.query(
            """INSERT INTO [Fields] VALUES (NULL, ?, ?, ?, ?);""",
            (
              template,
              label,
              type,
              order
            )
        )

        self.query(
            """INSERT INTO [Fields_data] VALUES(NULL, ?, ?, ?);""",
            (
              field_id[0],
              "width",
              width
            )
        )
        self.conn.commit()
        return field_id

    except Exception as e:
        self.log.error("There was an error adding the field: {}".format(e))
        self.conn.rollback()
        return False


def field_delete(self, id):
    if not self.templates:
        self.log.warning(
          "This function is not compatible with global" +
          " databases"
        )
        return False

    self.log.debug("Deleting group {}".format(id))
    try:
        self.query(
            """DELETE FROM [Fields] WHERE [ID] = ?""",
            (
                id,
            )
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error deleting the group: {}".format(e))
        self.conn.rollback()
        return False


def field_get_data(self, id):
    try:
        query_f = """SELECT * FROM [Fields] WHERE [ID] = ?;"""
        query_fd = """SELECT * FROM [Fields_data] WHERE [Field] = ?;"""
        field = self.query(query_f, (id,))
        field_data = self.query(query_fd, (id,))

        field_return = {}
        for item in field:
            field_return['ID'] = id
            field_return['label'] = item[2]
            field_return['field_type'] = item[3]
            field_return['order'] = item[4]

        field_return['field_data'] = {}
        for item in field_data:
            field_return['field_data'][item[2]] = item[3]

        return field_return
    except Exception as e:
        self.log.error("There was an error processing field data: {}".format(e))
        return False
