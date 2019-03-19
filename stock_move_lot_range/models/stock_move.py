# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    lot_range = fields.Char(
        string='Lot Range',
        compute='_compute_stock_move_lot_range',
        store=True
    )

    @api.depends('move_line_ids')
    def _compute_stock_move_lot_range(self):
        for rec in self:
            if rec.product_id.tracking == 'serial':
                last_serial = 0
                last_included = 0
                try:
                    for line in rec.move_line_ids:
                        serial = line.lot_name or line.lot_id.name
                        if not last_serial:
                            last_serial = rec.lot_range = last_included = \
                                serial
                        elif int(serial) - int(last_serial) == 1:
                            last_serial = serial
                        else:
                            if last_included != last_serial:
                                rec.lot_range += " - %s,\n%s" % (
                                    last_serial, serial)
                                last_included = serial
                            elif last_included != serial:
                                rec.lot_range += ",\n%s" % serial
                                last_included = serial
                            last_serial = serial
                    if last_included != last_serial:
                        rec.lot_range += " - %s" % last_serial
                except ValueError:
                    for line in rec.move_line_ids:
                        serial = line.lot_name or line.lot_id.name
                        rec.lot_range += "%s,\n" % serial
