# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    encoded_reason_id = fields.Many2one('stock.change.product.reason')

    @api.multi
    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        journal_id, acc_src, acc_dest, acc_valuation = \
            super(StockMove, self)._get_accounting_data_for_valuation()
        if self.encoded_reason_id:
            if self.encoded_reason_id.account_reason_input_id:
                acc_src = self.encoded_reason_id.account_reason_input_id.id
            if self.encoded_reason_id.account_reason_output_id:
                acc_dest = self.encoded_reason_id.account_reason_output_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
