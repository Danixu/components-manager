# -*- coding: utf-8 -*-


def category_add(self, name, parent=-1):
    self.log.debug("Adding category: {}".format(name))
    try:
        category_id = self._insert(
            "Categories",
            ["Parent", "Name"],
            [parent, name]
        )
        self.conn.commit()
        return category_id

    except Exception as e:
        self.log.error("There was an error adding the category: {}".format(e))
        self.conn.rollback()
        return False


def category_rename(self, name, id):
    self.log.debug("Renaming category to {}".format(name))
    try:
        self._update(
            "Categories",
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
        self.log.error("There was an error adding the category: {}".format(e))
        self.conn.rollback()
        return False


def category_delete(self, id):
    self.log.debug("Deleting category {}".format(id))
    try:
        self._delete(
            "Categories",
            where=[{'key': 'ID', 'value': id}]
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error deleting the category: {}".format(e))
        self.conn.rollback()
        return False


def category_data_html(self, id):
    html = ""
    category = self._select(
        "Categories",
        ["Name"],
        where=[
            {
                'key': 'ID',
                'value': id
            },
        ]
    )

    parentOfCats = self._select(
        "Categories",
        ["COUNT(*)"],
        where=[
            {
                'key': 'Parent',
                'value': id
            },
        ]
    )

    parentOfComp = self._select(
        "Components",
        ["COUNT(*)"],
        where=[
            {
                'key': 'Category',
                'value': id
            },
        ]
    )

    html += "<h1>{}</h1>\n<table>\n".format(category[0][0])

    html += (
        "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">"
        "{}</td></tr>\n".format("Subcategorías", parentOfCats[0][0])
    )
    html += (
        "<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">"
        "{}</td></tr>\n".format("Componentes", parentOfComp[0][0])
    )

    return self.header + html + self.footer
