# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class WizardStockRequestOrderKanban(models.TransientModel):
    _name = "wizard.stock.request.kanban"
    _inherit = "wizard.stock.request.kanban.abstract"

    stock_request_id = fields.Many2one(
        'stock.request',
        readonly=True,
    )
    stock_request_ids = fields.Many2many(
        'stock.request',
        readonly=True,
        compute='_compute_stock_request_ids'
    )
    stock_requests = fields.Char()

    @api.multi
    @api.depends('stock_requests')
    def _compute_stock_request_ids(self):
        for rec in self.filtered(lambda r: r.stock_requests):
            stock_request_ids = [
                int(i) for i in self.stock_requests.split(',')]
            rec.stock_request_ids = [(6, 0, stock_request_ids)]

    def barcode_ending(self):
        super().barcode_ending()
        used_kanbans = self.stock_request_ids.mapped('kanban_id')
        stock_requests = self.stock_requests
        if self.kanban_id in used_kanbans:
            self.status_state = 1
            self.status = _('Kanban %s for '
                            'product %s has already been scanned.' % (
                    self.kanban_id.name,
                    self.kanban_id.product_id.display_name
            ))
        else:
            self.stock_request_id = self.env['stock.request'].create(
                self.stock_request_kanban_values()
            )
            if not stock_requests:
                self.stock_requests = self.stock_request_id.id
            else:
                self.stock_requests = ','.join([stock_requests,
                                                str(self.stock_request_id.id)])
            self.status = _('Added kanban %s for product %s' % (
                self.stock_request_id.kanban_id.name,
                self.stock_request_id.product_id.display_name
            ))
            self.status_state = 0
        self.stock_request_ending()
        return True

    def stock_request_ending(self):
        # self.stock_request_id.action_confirm()
        pass


    def stock_request_kanban_values(self):
        return {
            'company_id': self.kanban_id.company_id.id,
            'procurement_group_id':
                self.kanban_id.procurement_group_id.id or False,
            'location_id': self.kanban_id.location_id.id or False,
            'warehouse_id': self.kanban_id.warehouse_id.id or False,
            'product_id': self.kanban_id.product_id.id,
            'product_uom_id': self.kanban_id.product_uom_id.id or False,
            'route_id': self.kanban_id.route_id.id or False,
            'product_uom_qty': self.kanban_id.product_uom_qty,
            'kanban_id': self.kanban_id.id,
        }

    @api.multi
    def action_view_stock_requests(self):
        action = self.env.ref(
            'stock_request.action_stock_request_form').read()[0]
        if len(self.stock_request_ids) > 1:
            action['domain'] = [('id', 'in', self.stock_request_ids.ids)]
        elif self.stock_request_ids:
            action['views'] = [
                (self.env.ref(
                    'stock_request.view_stock_request_form').id, 'form')]
            action['res_id'] = self.stock_request_ids.id
        return action

    @api.multi
    def action_confirm_stock_requests(self):
        self.stock_request_ids.action_confirm()
