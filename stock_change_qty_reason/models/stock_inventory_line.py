# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockInventoryLine(models.Model):
    """Class to inherit model stock.inventory.line"""
    _inherit = "stock.inventory.line"

    reason = fields.Char('Reason',
                         help='Type in a reason for the '
                              'product quantity change')
    encoded_reason_id = fields.Many2one('stock.change.product.reason',
                                        required=False)

    @api.onchange('encoded_reason_id')
    def onchange_encoded_reason(self):
        if self.encoded_reason_id:
            self.reason = self.encoded_reason_id.name
