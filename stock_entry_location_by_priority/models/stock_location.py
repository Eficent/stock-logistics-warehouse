# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    entry_priority = fields.Integer(
        string="Entry Priority", default=10,
    )
    apply_entry_priority = fields.Boolean(
        string="Apply Entry Priority Policy"
    )
    max_quantity = fields.Float(
        string="Maximum Location Capacity",
        default=0.0,
        help="This is the maximum location capacity, setting the value to 0.0 "
             "means infinite capacity"
    )
