# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""stock_change_product_qty"""


from odoo import models, fields, api


class StockChangeProductQty(models.TransientModel):
    """Class to inherit model stock.change.product.qty"""
    _inherit = 'stock.change.product.qty'

    reason_id = fields.Char('Reason',
                         help='Type in a reason for the '
                         'product quantity change')
    encoded_reason_id = fields.Many2one('stock.inventory.line.reason',
                                        required=False)

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env['res.company']._company_default_get()
    )

    qty_reason_encoded = fields.Boolean(
        related="company_id.qty_reason_encoded")

    def _action_start_line(self):
        res = super(StockChangeProductQty)._action_start_line()
        if self.company_id.qty_reason_encoded and self.encoded_reason:
            ext_res = {
                'encoded_reason_id': self.encoded_reason_id,
                'reason_id': self.encoded_reason_id.name,
            }
            res = {**res, **ext_res}
        elif self.reason:
            ext_res = {'reason_id': self.reason_id, }
            res = {**res, **ext_res}
        return res

    @api.onchange('encoded_reason_id')
    def onchange_encoded_reason(self):
        if self.encoded_reason_id:
            self.reason_id = self.encoded_reason_id.name
