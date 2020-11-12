from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    push_group_id = fields.Many2one('procurement.group')

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self.with_context(manual_push=True):
            for move in picking.move_lines:
                if move.backorder_id:
                    move.first_backorder_move = True
                    break
            picking.move_lines._push_apply()
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    first_backorder_move = fields.Boolean(default=False)
