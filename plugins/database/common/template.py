# -*- coding: utf-8 -*-


def template_add(self, name, parent=-1):
    if not self.templates:
        self.log.warning(
            "This function is not compatible with global" +
            " databases"
        )
        return False

    self.log.debug("Adding template: {}".format(name))
    try:
        template_id = self._insert(
            "Templates",
            items=[
                "Category",
                "Name"
            ],
            values=[
                parent,
                name
            ]
        )
        self.conn.commit()
        return template_id

    except Exception as e:
        self.log.error("There was an error adding the template: {}".format(e))
        self.conn.rollback()
        return False


def template_del(self, id):
    if not self.templates:
        self.log.warning(
            "This function is not compatible with global" +
            " databases"
        )
        return False

    self.log.debug("Deleting template {}".format(id))
    try:
        self._delete(
            "Templates",
            where=[
                {'key': 'ID', 'value': id}
            ]
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error deleting the template: {}".format(e))
        self.conn.rollback()
        return False


def template_get(self, id):
    if not self.templates:
        self.log.warning(
            "This function only is compatible with templates" +
            " databases"
        )
        return False

    tmp_sql_data = self._select(
        "Templates",
        ["Name"],
        where=[
            {'key': 'ID', 'value': id}
        ]
    )
    if len(tmp_sql_data) == 0:
        self.log.info("Template has no data: {}".format(id))
        return False

    template_data = {
        "Name": tmp_sql_data[0][0]
    }

    fields = self._select(
        "Fields",
        ["*"],
        where=[
            {'key': 'Template', 'value': id}
        ],
        order=[
            {'key': 'Order'}
        ]
    )
    template_data['fields'] = []
    for field in fields:
        field_data = {}
        fdata = self._select(
            "Fields_data",
            ["Key", "Value"],
            where=[
                {'key': 'Field', 'value': field[0]}
            ]
        )
        for fd in fdata:
            field_data[fd[0]] = fd[1]

        template_data['fields'].append({
            "id": field[0],
            "label": field[2],
            "field_type": field[3],
            "order": field[4],
            "field_data": field_data
        })
    return template_data


def template_ren(self, name, id):
    if not self.templates:
        self.log.warning(
            "This function is not compatible with global" +
            " databases"
        )
        return False

    self.log.debug("Renaming template to {}".format(name))
    try:
        self._update(
            "Templates",
            [
                {'key': 'Name', 'value': name}
            ],
            [
                {'key': 'ID', 'value': id}
            ]
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error adding the template: {}".format(e))
        self.conn.rollback()
        return False
