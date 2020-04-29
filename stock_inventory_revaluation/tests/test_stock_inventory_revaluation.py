# Copyright 2020 Matt Taylor
# Copyright 2016-17 ForgeFlow  S.L.
#   (https://forgeflow.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import exceptions
from datetime import datetime
from datetime import date, timedelta


class TestStockInventoryRevaluation(TransactionCase):
    """Test that the Inventory is Revaluated when the
    inventory price for any product is changed."""

    def setUp(self):
        super(TestStockInventoryRevaluation, self).setUp()
        # Get required Model
        self.product_model = self.env['product.product']
        self.template_model = self.env['product.template']
        self.product_ctg_model = self.env['product.category']
        self.reval_model = self.env['stock.inventory.revaluation']
        self.account_model = self.env['account.account']
        self.journal_model = self.env['account.journal']
        self.stock_move_model = self.env['stock.move']
        self.get_move_model = self.\
            env['stock.inventory.revaluation.get.moves']
        self.mass_post_model = self.\
            env['stock.inventory.revaluation.mass.post']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.stock_location_model = self.env['stock.location']
        self.res_users_model = self.env['res.users']

        # Get required Model data
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.company = self.env.ref('base.main_company')

        # groups
        self.group_inventory_valuation = self.env.ref(
            'stock.group_stock_manager')
        self.group_stock_user = self.env.ref(
            'stock.group_stock_user')

        location = self.stock_location_model.search([('name', '=', 'WH')])
        self.location = self.stock_location_model.search([('location_id', '=',
                                                           location.id)])

        self.scrap_location = self.stock_location_model.search(
            [('scrap_location', '=', True)], limit=1)

        # Account types
        expense_type = self.env.ref('account.data_account_type_expenses')
        equity_type = self.env.ref('account.data_account_type_equity')
        asset_type = self.env.ref('account.data_account_type_fixed_assets')\

        # Create account for Goods Received Not Invoiced
        name = 'Goods Received Not Invoiced'
        code = 'grni'
        acc_type = equity_type
        self.account_grni = self._create_account(acc_type, name, code,
                                                 self.company)
        # Create account for Cost of Goods Sold
        name = 'Cost of Goods Sold'
        code = 'cogs'
        acc_type = expense_type
        self.account_cogs = self._create_account(acc_type, name, code,
                                                 self.company)

        # get accounting journal
        self.journal = self.journal_model.create({
            'code': 'test',
            'name': 'test',
            'type': 'general'
        })
        # Create account for Inventory
        name = 'Inventory'
        code = 'inventory'
        acc_type = asset_type
        self.account_inventory = self._create_account(acc_type, name, code,
                                                      self.company)

        # Create account for Inventory Revaluation
        name = 'Inventory Revaluation'
        code = 'revaluation'
        acc_type = expense_type
        self.account_revaluation = self._create_account(acc_type, name, code,
                                                        self.company)

        # Create product category
        self.product_ctg = self._create_product_category()

        # Create users
        self.user1 = self._create_user('user_1',
                                       [self.group_stock_user,
                                        self.group_inventory_valuation],
                                       self.company)

        # Create a Product with fifo cost
        standard_price = 10.0
        list_price = 20.0
        self.product_fifo_1 = self._create_product(
            'fifo',
            standard_price,
            False,
            list_price)
        self.product_fifo_2 = self._create_product(
            'fifo',
            standard_price,
            self.product_fifo_1.product_tmpl_id,
            list_price)

        # Add default quantity
        quantity = 10.00
        self._update_product_qty(self.product_fifo_1, self.location, quantity)
        self._update_product_qty(self.product_fifo_2, self.location, quantity)

        # Create a Product with average cost
        standard_price = 10.0
        list_price = 20.0
        self.product_average_1 = self._create_product(
            'average',
            standard_price,
            False,
            list_price)
        self.product_average_2 = self._create_product(
            'average',
            standard_price,
            self.product_average_1.product_tmpl_id,
            list_price)

        # Add default quantity
        quantity = 10.00
        self._update_product_qty(self.product_average_1, self.location,
                                 quantity)
        self._update_product_qty(self.product_average_2, self.location,
                                 quantity)

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.res_users_model.with_context(
                {'no_reset_password': True}).create(
                {'name': 'Test User',
                 'login': login,
                 'password': 'demo',
                 'email': 'test@yourcompany.com',
                 'company_id': company.id,
                 'company_ids': [(4, company.id)],
                 'groups_id': [(6, 0, group_ids)]
                 })
        return user

    def _create_account(self, acc_type, name, code, company):
        """Create an account."""
        account = self.account_model.create({
            'name': name,
            'code': code,
            'user_type_id': acc_type.id,
            'company_id': company.id,
        })
        return account

    def _create_product_category(self):
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_inventory.id,
            'property_inventory_revaluation_increase_account_categ':
                self.account_revaluation.id,
            'property_inventory_revaluation_decrease_account_categ':
                self.account_revaluation.id,
            'property_valuation': 'real_time',
            'property_stock_journal': self.journal.id,
        })
        return product_ctg

    def _create_product(self, cost_method, standard_price, template,
                        list_price):
        """Create a Product variant."""
        if not template:
            template = self.template_model.create({
                'name': 'test_product',
                'categ_id': self.product_ctg.id,
                'type': 'product',
                'standard_price': standard_price,
                'valuation': 'real_time',
                'cost_method': cost_method,
                'property_stock_account_input': self.account_grni.id,
                'property_stock_account_output': self.account_cogs.id,
            })
            return template.product_variant_ids[0]
        product = self.product_model.create(
            {'product_tmpl_id': template.id,
             'standard_price': standard_price,
             'list_price': list_price,
             })
        return product

    def _create_inventory_revaluation(self, revaluation_type,
                                      product, post_date=None):
        """Create a Inventory Revaluation by applying
         increase and decrease account to it."""
        self.increase_account_id = product.categ_id and \
            product.categ_id.\
            property_inventory_revaluation_increase_account_categ
        self.decrease_account_id = product.categ_id and \
            product.categ_id.\
            property_inventory_revaluation_decrease_account_categ

        reval = self.reval_model.sudo(self.user1).create({
            'name': 'test_inventory_revaluation',
            'revaluation_type': revaluation_type,
            'product_id': product.id,
            'increase_account_id': self.increase_account_id.id,
            'decrease_account_id': self.decrease_account_id.id,
            'post_date': post_date or False,
            'remarks': "Test revaluation",
        })
        return reval

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.stock_change_model.create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def _get_move(self, date_from, revaluation):
        """Get Moves for Inventory Revaluation between the date supplied."""
        line_context = {
            'active_id': revaluation.id,
            'active_ids': revaluation.ids,
            'active_model': 'stock.inventory.revaluation',
        }
        get_moves = self.get_move_model.with_context(line_context).create({
            'date_from': date_from,
            'date_to': datetime.today(),
        })
        get_moves.with_context(line_context).process()
        for reval_move in revaluation.reval_move_ids:
            reval_move.new_value = 8.0 * reval_move.qty

    def _mass_post(self, revaluations):
        """Post revaluations."""
        context = {
            'active_id': revaluations[0],
            'active_ids': [rev.id for rev in revaluations],
            'active_model': 'stock.inventory.revaluation',
        }
        mass_post_wiz = self.mass_post_model.sudo(self.user1).with_context(
            context).create({})
        mass_post_wiz.process()
        return True

    def test_defaults(self):
        """Test default methods"""
        # we no longer set a default journal
        # self.assertNotEqual(self.reval_model._default_journal(), False)
        pass

    def test_inventory_revaluation_price_change_fifo(self):
        """Test that the inventory is revaluated when the
        inventory price for a product managed under fifo costing method is
        changed."""

        # Create an Inventory Revaluation for fifo cost product
        revaluation_type = 'inventory_value'
        post_date = date.today() - timedelta(days=4)
        invent_price_change_fifo = \
            self._create_inventory_revaluation(
                revaluation_type,
                self.product_fifo_1,
                post_date)

        # Create an Inventory Revaluation Line Move
        date_from = date.today() - timedelta(1)
        self._get_move(date_from, invent_price_change_fifo)

        invent_price_change_fifo.sudo(self.user1).button_post()

        expected_result = (10.00 - 8.00) * 10.00
        self.assertEqual(len(
            invent_price_change_fifo.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        for move_line in invent_price_change_fifo.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, expected_result,
                                 'Incorrect inventory revaluation for '
                                 'type Total Value Change.')

        for acc_move in invent_price_change_fifo.account_move_ids:
            self.assertEqual(acc_move.date, post_date,
                             "Journal entry dates don't match Post Date.")

    def create_inventory_revaluation_price_change_average(self):
        revaluation_type = 'price_change'
        # Create an Inventory Revaluation for average cost product
        invent_price_change_average = self._create_inventory_revaluation(
            revaluation_type,
            self.product_average_1)
        invent_price_change_average.new_cost = 8.00
        return invent_price_change_average

    def test_inventory_revaluation_price_change_average(self):
        """Test that the inventory is revaluated when the
        inventory price for a product managed under average costing method is
        changed."""
        # product_average_1   | qty | cost |  value
        # --------------------+-----+------+--------
        # previous            |  10 |   10 |    100
        # change              |  10 |    8 |     80

        invent_price_change_average = \
            self.create_inventory_revaluation_price_change_average()
        # Post the inventory revaluation
        test_context = {
            'active_id': invent_price_change_average.id,
            'active_ids': invent_price_change_average.ids,
            'active_model': 'stock.inventory.revaluation',
        }
        invent_price_change_average.with_context(test_context).button_post()
        expected_result = (10.00 - 8.00) * 10.00

        # Verify journal entries were created
        self.assertEqual(
            len(invent_price_change_average.account_move_ids), 1,
            'Accounting entries were not generated for revaluation')

        self.assertEqual(len(
            invent_price_change_average.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        for move_line in \
                invent_price_change_average.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, expected_result,
                                 'Incorrect inventory revaluation for '
                                 'Standard Product .')

    def test_inventory_revaluation_do_change_standard_price(self):
        """Test that the inventory is revaluated when using the
        do_change_standard_price() method for a product with average
        costing."""
        # product_average_1   | qty | cost |  value
        # --------------------+-----+------+--------
        # previous            |  10 |   10 |    100
        # change              |  10 |    5 |     50

        context = {'active_model': u'product.product',
                   'active_ids': self.product_average_1.ids,
                   'active_id': self.product_average_1.id}
        self.product_average_1.with_context(context).\
            do_change_standard_price(5.00, self.account_revaluation.id)

        if self.product_average_1:
            self.assertEqual(self.product_average_1.standard_price, 5.0,
                             'Incorrect Product Price.')

        reval = self.reval_model.search(
            [('product_id', '=', self.product_average_1.id)],
            order='document_date desc', limit=1)

        for move_line in reval.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, 50.0,
                                 'Incorrect inventory revaluation using '
                                 'Update Cost wizard.')

    def create_inventory_revaluation_value_change(self):
        # Create an Inventory Revaluation for value change for average
        # cost product
        revaluation_type = 'inventory_value'
        invent_value_change = self._create_inventory_revaluation(
            revaluation_type,
            self.product_average_1)
        invent_value_change.new_value = 90.00
        return invent_value_change

    def test_inventory_revaluation_value_change(self):
        """Test that the inventory is revaluated when the
        inventory price for any product is changed."""
        # product_average_1   | qty | cost |  value
        # --------------------+-----+------+--------
        # previous            |  10 |   10 |    100
        # change              |  10 |    9 |     90

        invent_value_change = self.create_inventory_revaluation_value_change()

        # Post the inventory revaluation
        test_context = {
            'active_id': invent_value_change.id,
            'active_ids': invent_value_change.ids,
            'active_model': 'stock.inventory.revaluation',
        }
        invent_value_change.with_context(test_context).button_post()

        self.assertEqual(len(
            invent_value_change.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        with self.assertRaises(exceptions.Warning):
            invent_value_change.account_move_ids.unlink()

        with self.assertRaises(exceptions.Warning):
            invent_value_change.account_move_ids[0].line_ids.unlink()

        for move_line in invent_value_change.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(move_line.credit, 10.0,
                                 'Incorrect inventory revaluation for '
                                 'type Total Inventory Change.')

    def test_mass_post(self):
        """Test mass post"""

        revaluations = self.env['stock.inventory.revaluation']

        # Create an Inventory Revaluation for average cost product
        invent_price_change_average = \
            self.create_inventory_revaluation_price_change_average()
        revaluations += invent_price_change_average

        # Create an Inventory Revaluation for fifo cost product
        invent_value_change = self.create_inventory_revaluation_value_change()
        revaluations += invent_value_change

        # Post the inventory revaluation using wizard
        self._mass_post(revaluations)

        # Check that both inventory valuations are now posted
        self.assertEqual(invent_price_change_average.state, 'posted')
        self.assertEqual(invent_value_change.state, 'posted')

    def test_cancel(self):
        """Test cancel"""

        # Create an Inventory Revaluation for fifo cost product
        revaluation_type = 'inventory_value'
        invent_price_change_fifo = \
            self._create_inventory_revaluation(
                revaluation_type,
                self.product_fifo_1)

        # Create an Inventory Revaluation Line Move
        date_from = date.today() - timedelta(1)
        self._get_move(date_from, invent_price_change_fifo)

        invent_price_change_fifo.sudo(self.user1).button_post()

        # Allow cancelling journal entries
        invent_price_change_fifo.journal_id.sudo().update_posted = True

        # Cancel the inventory revaluation
        invent_price_change_fifo.sudo(self.user1).button_cancel()

        for reval_move in invent_price_change_fifo.reval_move_ids:
            expected_result = 10.00 * 10.00
            self.assertEqual(reval_move.move_id.remaining_value,
                             expected_result,
                             'Cancelling the revaluation did not restore the '
                             'original move value.')

        self.assertEqual(len(
            invent_price_change_fifo.account_move_ids), 0,
            'Accounting entries have not been removed after cancel')

    def test_inventory_revaluation_price_change_fifo_multi_quant(self):
        """Test that the inventory is revaluated when the
        inventory value for a product managed under fifo costing method is
        changed even if there are multple moves to revaluate"""

        location = self.env.ref('stock.stock_location_components')
        self._update_product_qty(self.product_fifo_1, location, 1)

        revaluation_type = 'inventory_value'
        invent_price_change_fifo = \
            self._create_inventory_revaluation(
                revaluation_type,
                self.product_fifo_1)

        # Create an Inventory Revaluation Line Move
        date_from = date.today() - timedelta(1)
        self._get_move(date_from, invent_price_change_fifo)

        invent_price_change_fifo.sudo(self.user1).button_post()

        self.assertEqual(len(
            invent_price_change_fifo.account_move_ids[0].line_ids), 2,
            'Incorrect accounting entry generated')

        for move_line in invent_price_change_fifo.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                expected_result = (10.00 - 8.00) * move_line.quantity
                self.assertEqual(move_line.credit, expected_result,
                                 'Incorrect inventory revaluation for '
                                 'type Total Value Change.')

    def test_cancel_after_qty_change(self):
        """Test cancel after stock move remaining quantity has changed"""

        revaluation_type = 'inventory_value'
        invent_price_change_fifo = self._create_inventory_revaluation(
            revaluation_type,
            self.product_fifo_1)

        # Create an Inventory Revaluation Line Move
        date_from = date.today() - timedelta(1)
        self._get_move(date_from, invent_price_change_fifo)

        invent_price_change_fifo.sudo(self.user1).button_post()

        # Decrease the remaining quantity of the stock move
        self._update_product_qty(self.product_fifo_1, self.location, 9)

        # Trying to cancel the inventory revaluation should raise an error
        with self.assertRaises(exceptions.UserError):
            invent_price_change_fifo.sudo(self.user1).button_cancel()

    def test_inventory_revaluation_fifo_consumed_value(self):
        """Test that subsequent stock moves us the new value for a product
        managed under fifo costing method."""

        # Create an Inventory Revaluation for fifo cost product
        revaluation_type = 'inventory_value'
        post_date = date.today() - timedelta(days=4)
        invent_price_change_fifo = \
            self._create_inventory_revaluation(
                revaluation_type,
                self.product_fifo_1,
                post_date)
        date_from = date.today() - timedelta(1)
        self._get_move(date_from, invent_price_change_fifo)
        invent_price_change_fifo.sudo(self.user1).button_post()

        # Consume one of the revalued units
        self._update_product_qty(self.product_fifo_1, self.location, 9)

        # Get outbound stock move
        stock_move = self.stock_move_model.search([
            ('product_id', '=', self.product_fifo_1.id),
            ('location_id', '=', self.location.id),
        ])

        # Verify journal entries were created
        self.assertEqual(
            len(stock_move.account_move_ids), 1,
            'Accounting entries have not been generated for stock move')

        # Check journal entry for correct value
        expected_result = 8.00 * 1.00
        for move_line in stock_move.account_move_ids[0].line_ids:
            if move_line.account_id == self.account_inventory:
                self.assertEqual(
                    move_line.credit, expected_result,
                    'Incorrect account move amount for consumption of '
                    'revalued product.')
