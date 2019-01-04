# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    qty_reason_encoded = fields.Boolean(
        string="Encoded Change Qty Reason",
        related="company_id.qty_reason_encoded",
        required=True,
        )


class ResCompany(models.Model):
    _inherit = 'res.company'

    qty_reason_encoded = fields.Boolean(string="Encoded Change Qty Reason")
