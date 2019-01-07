# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockAccountInventoryChangeReason(models.Model):
    _inherit = 'stock.inventory.line.reason'

    account_reason_input_id = fields.Many2one('account.account',
                                              string='Account Reason Input')
    account_reason_output_id = fields.Many2one('account.account',
                                               string='Account Reason Output')
