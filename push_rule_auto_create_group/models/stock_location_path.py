# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PushedFlow(models.Model):
    _inherit = "stock.location.path"

    auto_create_group = fields.Boolean(string='Auto-create Procurement Group')

    def _apply(self, move):
        res = super(PushedFlow, self)._apply(move)
        backorder_list = self.env.context.get('backorder_list', [])
        new_date = (datetime.strptime(move.date_expected,
                                      DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta.relativedelta(
            days=self.delay)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if self.auto == 'transparent':
            move.write({
                'date': new_date,
                'date_expected': new_date,
                'location_dest_id': self.location_dest_id.id})
            # avoid looping if a push rule is not well configured; otherwise call again push_apply to see if a next step is defined
            if self.location_dest_id != move.location_dest_id:
                # TDE FIXME: should probably be done in the move model IMO
                move._push_apply()
        else:
            new_move_vals = self.with_context(
                backorder_list)._prepare_move_copy_values(move, new_date)
            new_move = move.copy(new_move_vals)
            move.write({'move_dest_ids': [(4, new_move.id)]})
            new_move._action_confirm()
        return res

    def _prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super(
            PushedFlow, self)._prepare_move_copy_values(
            move_to_copy, new_date)
        if self.auto_create_group and not move_to_copy.picking_id.pushed_group_id and move_to_copy.purchase_line_id.order_id.group_picking_count:
            group_data = self._prepare_auto_procurement_group_data()
            group = self.env['procurement.group'].create(group_data)
            new_move_vals['group_id'] = group.id
            move_to_copy.picking_id.pushed_group_id = group.id
        elif move_to_copy.picking_id.pushed_group_id:
            new_move_vals['group_id'] = move_to_copy.picking_id.pushed_group_id.id
        return new_move_vals

    @api.model
    def _prepare_auto_procurement_group_data(self):
        name = self.env['ir.sequence'].next_by_code(
            'procurement.group') or False
        if not name:
            raise UserError(_('No sequence defined for procurement group'))
        return {
            'name': name
        }
