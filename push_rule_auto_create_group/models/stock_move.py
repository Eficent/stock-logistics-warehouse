from odoo import models

class StockMove(models.Model):
    _inherit = "stock.move"

    def _push_apply(self):
        res = super(StockMove, self)._push_apply()
        backorder_list = self.env.context.get('backorder_list', [])
        Push = self.env['stock.location.path']
        for move in self:
            # if the move is already chained, there is no need to check push rules
            if move.move_dest_ids:
                continue
            # if the move is a returned move, we don't want to check push rules, as returning a returned move is the only decent way
            # to receive goods without triggering the push rules again (which would duplicate chained operations)
            domain = [('location_from_id', '=', move.location_dest_id.id)]
            # priority goes to the route defined on the product and product category
            routes = move.product_id.route_ids | move.product_id.categ_id.total_route_ids
            rules = Push.search(domain + [('route_id', 'in', routes.ids)],
                                order='route_sequence, sequence', limit=1)
            if rules and (
                not move.origin_returned_move_id or move.origin_returned_move_id.location_dest_id.id != rules.location_dest_id.id):
                rules.with_context(backorder_list)._apply(move)
        return res
