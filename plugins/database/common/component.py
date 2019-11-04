# -*- coding: utf-8 -*-
import globals
from wx import App

# Load global data
app = App()
globals.init()


def component_data(self, comp_id):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    data_raw = {}
    data_real = {}

    # Getting template info
    component_q = self._select(
        "Components",
        ["Template", "Stock"],
        where=[
            {
                'key': 'ID',
                'value': comp_id
            },
        ]
    )
    template_data = self.parent.database_temp.template_get(
        component_q[0][0]
    )

    # Getting raw data
    q = self._select(
        "Components_data",
        ["Field_id", "Value"],
        where=[
            {
                'key': 'Component',
                'value': comp_id
            },
        ]
    )
    for item in q:
        data_raw.update({item[0]: item[1]})

    # Converting raw data to real values
    for item, data in data_raw.items():
        for field in template_data.get('fields', {}):
            if field['id'] == item:
                if globals.field_kind[field['field_type']] == "ComboBox":
                    fd = self.parent.database_temp._select(
                        "Values",
                        ["Value"],
                        where=[
                            {
                                'key': 'ID',
                                'value': data
                            },
                        ]
                    )
                    if len(fd) > 0:
                        data_real.update(
                            {
                                item: {
                                    'key': field['label'],
                                    'value': fd[0][0]
                                }
                            }
                        )
                    else:
                        data_real.update(
                            {
                                item: {
                                    'key': field['label'],
                                    'value': "<unknown field>"
                                }
                            }
                        )
                else:
                    data_real.update(
                        {
                            item: {
                                'key': field['label'],
                                'value': data
                            }
                        }
                    )
                continue

    # Getting the name
    name = ""
    first = True
    for item in template_data['fields']:
        if item['field_data'].get(
            'in_name',
            'false'
        ).lower() == 'true':
            if not item['field_data'].get(
                'join_previous',
                'false'
            ).lower() == 'true' and not first:
                name += " - "
            elif item['field_data'].get(
                'no_space',
                'false'
            ).lower() == 'false' and not first:
                name += " "
            if item['field_data'].get(
                'in_name_label',
                'false'
            ).lower() == 'true':
                if item['field_data'].get(
                    'in_name_label_separator',
                    'true'
                ).lower() == 'true':
                    name += "{}:".format(item['label'])
                else:
                    name += "{}".format(item['label'])
                if item['field_data'].get(
                    'no_space',
                    'false'
                ).lower() == 'false' and not first:
                    name += " "

            name += data_real.get(item['id'], {}).get('value', '<PlaceHolder>')
            if first:
                first = False
    # Return the final data
    return {
        "name": name,
        "template_data": template_data,
        "stock": component_q[0][1],
        "data_raw": data_raw,
        "data_real": data_real
    }
