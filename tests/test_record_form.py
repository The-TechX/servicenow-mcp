import unittest
from servicenow_mcp.models.record import RequestDTO, RequestedItemDTO, WorkOrderDTO, WorkOrderTaskDTO
from servicenow_mcp.parsers.record_form import parse_record_form


def form(table, fields):
    body = []
    for field, html in fields.items():
        body.append(html.replace("{table}", table).replace("{field}", field))
    return "<html><body>" + "".join(body) + "</body></html>"


class RecordFormTests(unittest.TestCase):
    def test_wot_uses_display_parent_and_state(self):
        html = form("wm_task", {
            "number": '<input name="{table}.number" value="WOT0000001">',
            "parent": '<input name="{table}.parent" value="internal"><input name="sys_display.{table}.parent" value="WO0000001">',
            "state": '<select id="sys_readonly.{table}.state"><option value="3" selected>Closed Complete</option></select><input name="{table}.state" value="3">',
        })
        x = parse_record_form(html, "wm_task", "a" * 32, "WOT0000001")
        self.assertIsInstance(x, WorkOrderTaskDTO)
        self.assertEqual(x.parent, "WO0000001")
        self.assertEqual(x.state, "Closed Complete")

    def test_wo_is_typed_and_keeps_custom_fields(self):
        html = form("wm_order", {
            "number": '<input name="{table}.number" value="WO0000001">',
            "company": '<input name="{table}.company" value="internal"><input name="sys_display.{table}.company" value="Example Customer">',
            "custom": '<label for="{table}.u_example">Example field</label><input id="{table}.u_example" name="{table}.u_example" value="example">',
        })
        x = parse_record_form(html, "wm_order", "b" * 32, "WO0000001")
        self.assertIsInstance(x, WorkOrderDTO)
        self.assertEqual(x.customer, "Example Customer")
        self.assertEqual(x.custom_fields[0].name, "u_example")

    def test_ritm_extracts_catalog_variables(self):
        html = form("sc_req_item", {
            "number": '<input name="{table}.number" value="RITM0000001">',
            "request": '<input name="{table}.request" value="internal"><input name="sys_display.{table}.request" value="REQ0000001">',
            "variable": '<label for="ni.VE0001">Environment</label><select id="ni.VE0001" name="ni.VE0001"><option value="prod" selected>Production</option></select>',
        })
        x = parse_record_form(html, "sc_req_item", "c" * 32, "RITM0000001")
        self.assertIsInstance(x, RequestedItemDTO)
        self.assertEqual(x.request, "REQ0000001")
        self.assertEqual(x.variables[0].display_value, "Production")

    def test_req_is_typed(self):
        html = form("sc_request", {
            "number": '<input name="{table}.number" value="REQ0000001">',
            "requested_for": '<input name="{table}.requested_for" value="internal"><input name="sys_display.{table}.requested_for" value="Example User">',
        })
        x = parse_record_form(html, "sc_request", "d" * 32, "REQ0000001")
        self.assertIsInstance(x, RequestDTO)
        self.assertEqual(x.requested_for, "Example User")


if __name__ == "__main__":
    unittest.main()
