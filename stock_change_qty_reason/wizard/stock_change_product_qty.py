# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""stock_change_product_qty"""


from odoo import models, fields, api


class StockChangeProductQty(models.TransientModel):
    """Class to inherit model stock.change.product.qty"""
    _inherit = 'stock.change.product.qty'

    reason = fields.Char('Reason',
                         help='Type in a reason for the '
                         'product quantity change')
    encoded_reason = fields.Many2one('stock.change.product.reason',
                                       required=False)

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env['res.company']._company_default_get()
    )

    qty_reason_encoded = fields.Boolean(
        related="company_id.qty_reason_encoded")

    @api.multi
    def change_product_qty(self):
        """Function to super change_product_qty"""
        if self.company_id.qty_reason_encoded and self.encoded_reason:
            this = self.with_context(
                change_quantity_reason=self.reason,
                change_reason_id=self.encoded_reason.id)
        elif self.reason:
            this = self.with_context(change_quantity_reason=self.reason)
        else:
            this = self
        return super(StockChangeProductQty, this).change_product_qty()


    @api.onchange('encoded_reason')
    def onchange_encoded_reason(self):
        if self.encoded_reason:
            self.reason = self.encoded_reason.name
