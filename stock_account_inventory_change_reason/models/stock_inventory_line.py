# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockInventoryLine(models.Model):
    """Class to inherit model stock.inventory.line"""
    _inherit = "stock.inventory.line"

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        """Function to super _get_move_value"""
        res = super(StockInventoryLine, self)._get_move_values(
            qty, location_id, location_dest_id, out)
        if not res.get('encoded_reason_id'):
            res['encoded_reason_id'] = self.env.context.get('encoded_reason_id',
                                                           False)
        return res
