# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockInventoryLineReason(models.Model):

    _name = 'stock.inventory.line.reason'

    name = fields.Char('Reason Name', unique=True)
    description = fields.Char('Reason Description')
