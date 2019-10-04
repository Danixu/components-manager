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
        field_id = self._insert(
            "Fields",
            values=[
                None,
                template,
                label,
                type,
                order
            ]
        )
        self._insert(
            "Fields_data",
            values=[
                None,
                field_id[0],
                "width",
                width
            ]
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
        self._delete(
            "Fields",
            where=[
                {'key': 'ID', 'value': id}
            ]
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error deleting the group: {}".format(e))
        self.conn.rollback()
        return False


def field_get_data(self, id):
    try:
        field = self._select(
            "Fields",
            ["*"],
            where=[
                {
                    'key': 'ID',
                    'value': id
                },
            ]
        )
        field_data = self._select(
            "Fields_data",
            ["*"],
            where=[
                {
                    'key': 'Field',
                    'value': id
                },
            ]
        )

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
