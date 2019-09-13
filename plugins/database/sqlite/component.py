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
    component_q = self.query(
        """SELECT Template FROM Components WHERE ID = ?;""",
        (
            comp_id,
        )
    )
    template_data = self.parent.database_temp.template_get(
        component_q[0][0]
    )

    # Getting raw data
    q = self.query(
        """SELECT [Field_id], [Value] FROM [Components_data] WHERE [Component] = ?;""",
        (
            comp_id,
        )
    )
    for item in q:
        data_raw.update({ item[0]: item[1] })

    # Converting raw data to real values
    for item, data in data_raw.items():
        for field in template_data.get('fields', {}):
            if field['id'] == item:
                if globals.field_kind[field['field_type']] == "ComboBox":
                    fd = self.parent.database_temp.query(
                        """SELECT [Value] FROM [Values] WHERE [ID] = ?;""",
                        (
                            data,
                        )
                    )
                    if len(fd) > 0:
                        data_real.update(
                        { 
                            item: {
                                'key': field['label'],
                                'value': fd[0][0] 
                            }
                        })
                    else:
                        data_real.update(
                        { 
                            item: {
                                'key': field['label'],
                                'value': "<unknown field>" 
                            }
                        })
                else:
                    data_real.update(
                    { 
                        item: {
                            'key': field['label'],
                            'value': data 
                        }
                    })
                continue

    # Getting the name
    name = ""
    first = True
    for item in template_data['fields']:
        if item['field_data'].get('in_name', 'false').lower() == 'true':
            if not item['field_data'].get('join_previous', 'false').lower() == 'true' and not first:
                name += " - "
            elif item['field_data'].get('no_space', 'false').lower() == 'false' and not first:
                name += " "
            if item['field_data'].get('in_name_label', 'false').lower() == 'true':
                if item['field_data'].get('in_name_label_separator', 'true').lower() == 'true':
                    name += "{}:".format(item['label'])
                else:
                    name += "{}".format(item['label'])
                if item['field_data'].get('no_space', 'false').lower() == 'false' and not first:
                    name += " "

            name += data_real[item['id']].get('value', '')
            if first:
                first = False
    # Return the final data
    return {
        "name": name,
        "template_data": template_data,
        "data_raw": data_raw,
        "data_real": data_real
    }


def component_data_html(self, id):
    html = ""
    component_data = self.component_data(id)
    if not component_data:
        self.log.warning(
            "The component type {} was not found for component {}.".format(
                component[0][1],
                component[0][0]
            )
        )
        html += "<tr><td> Tipo de componente no encontrado. <br>Por favor, verifica si se borró la plantilla.</td>/tr>"
    else:
        html += "<h1>{}</h1>\n<table>\n".format(component_data['name'])
        first = True
        first_field = True

        for item in component_data['template_data']['fields']:
            print()
            if first:
                html += "<tr><td class=\"left-first\"><b>{}</b></td><td class=\"right-first\">".format(item['label'])
                first = False
            elif item['field_data']['join_previous'].lower() == 'false':
                html += "</td></tr>\n<tr><td class=\"left\"><b>{}</b></td><td class=\"right\">".format(item['label'])
            else:
                if item['field_data']['no_space'].lower() == 'false' and not first:
                    html += " "
                if item['field_data']['in_name_label'].lower() == 'true':
                    html += "<b>{}:</b> ".format(item['label'])

            value = component_data['data_real'][item['id']]['value']
            html += "{}".format(" - " if value == "" else value)
        html += "</td></tr>\n"

    return self.header + html + self.footer
