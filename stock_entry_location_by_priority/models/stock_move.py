# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

<<<<<<< HEAD
from odoo import models, api
=======
from odoo import models
>>>>>>> 40752bd652af051134a8db4bc0a3ec3fbcbedacb


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        if vals.get('location_dest_id'):
            location_dest_id = self.env['stock.location'].browse(
                vals.get('location_dest_id'))
            if location_dest_id.apply_entry_priority:
                child_location_ids = location_dest_id.child_ids.sorted(
                    key="entry_priority", reverse=False)
                if child_location_ids:
                    for child_location in child_location_ids:
                        on_hand_qty = child_location.quant_ids.filtered(
                            lambda x: x.product_id == self.product_id
                        ).quantity
                        if child_location.max_quantity == 0.0 or \
                                (child_location.max_quantity - on_hand_qty >=
                                 vals['product_uom_qty']):
                            vals['location_dest_id'] = child_location.id
                            break
                        elif child_location.max_quantity - on_hand_qty > 0.0:
                            vals['product_uom_qty'] = \
                                child_location.max_quantity - on_hand_qty
                            vals['location_dest_id'] = child_location.id
                            break

        return vals
