from odoo import http
from odoo.http import request


class StockRequestKanbanController(http.Controller):
    @http.route("/stock_request_kanban/kanban_code_reader", auth="user", type="json")
    def kanban_code_reader(self):
        """ Returns the `banner` for the start scanning kanban cards. """

        company = request.env.company

        return {
            "html": request.env.ref(
                "stock_request_kanban.stock_request_kanban_panel"
            ).render({"company": company})
        }
