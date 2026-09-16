# Structured Views

Structured views are implementation-oriented XRAY documents for ServiceNow record types.

They capture what a record exposes in the classic server-rendered HTML, how that data should be represented, and which parts are stable fields versus dynamic or related data. They are discovery documents, not promises that every ServiceNow instance exposes the same fields.

Each view should stay generic: no tenant names, internal domains, real record numbers, sys_ids, people, customers, sites, or authentication artifacts.

## Views

- [Requested Item (`sc_req_item` / RITM)](ritm.md)
- [Work Order (`wm_order` / WO)](wo.md)
- [Request (`sc_request` / REQ)](req.md)
- [Work Order Task (`wm_task` / WOT)](wot.md)
