# Copyright 019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase


class TestStockAccountChangeQtyReason(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockAccountChangeQtyReason, cls).setUpClass()

        # MODELS
        cls.product_product_model = cls.env['product.product']
        cls.product_category_model = cls.env['product.category']
        cls.wizard_model = cls.env['stock.change.product.qty']
        cls.encoded_reason_id = cls.env['stock.inventory.line.reason']

        # INSTANCES
        cls.category = cls.product_category_model.create({
            'name': 'Physical (test)',
            'property_cost_method': 'standard'})

        company = cls.env.ref('base.main_company')

        # Instance: account type (receivable)
        cls.type_recv = cls.env.ref('account.data_account_type_receivable')

        # Instance: account type (payable)
        cls.type_payable = cls.env.ref('account.data_account_type_payable')

        # account (receivable)
        cls.account_input = cls.env['account.account'].create({
            'name': 'test_account_reason_input',
            'code': '1234',
            'user_type_id': cls.type_recv.id,
            'company_id': company.id,
            'reconcile': True
        })

        # account (payable)
        cls.account_output = cls.env['account.account'].create({
            'name': 'test_account_reason_input',
            'code': '4321',
            'user_type_id': cls.type_payable.id,
            'company_id': company.id,
            'reconcile': True
        })

        cls.reason_id = cls.encoded_reason.create({
            'name': 'Test Reason',
            'description': 'Test Reason Description',
            'account_reason_input_id': cls.account_input.id,
            'account_reason_output_id': cls.account_output.id,
        })

    def _create_product(self, name):
        return self.product_product_model.create({
            'name': name,
            'categ_id': self.category.id,
            'type': 'product',
            'standard_price': 100, })

    def _product_change_qty(self, product, new_qty, reason_id,
                            encoded_reason=None):
        wizard = self.wizard_model.create({'product_id': product.id,
                                           'new_quantity': new_qty,
                                           'reason_id': reason_id,
                                           'encoded_reason':
                                               encoded_reason.id
                                               if encoded_reason else False
                                           })
        wizard.change_product_qty()

    def _create_reason(self, name, description=None):
        return self.encoded_reason.create({
            'name': name,
            'description': description})

    def test_product_change_qty_account_reason(self):
        # create products
        product = self._create_product('product_product')

        # update qty on hand and add reason
        self._product_change_qty(product, 10, self.reason_id.name,
                                 self.reason_id)

        # check stock moves and account moves created
        stock_move = self.env['stock.move'].search([('product_id', '=',
                                                     product.id)])
        account_move = self.env['account.move'].search(
            [('stock_move_id', '=', stock_move.id)])

        # asserts
        account_move_line1 = self.env['account.move.line'].search(
            [('move_id', '=', account_move.id),
             ('account_id', '=', self.account_input.id)])
        account_move_line2 = self.env['account.move.line'].search(
            [('move_id', '=', account_move.id),
             ('account_id', '=', self.account_output.id)])
        self.assertEqual(abs(account_move_line1.balance_cash_basis),
                         abs(account_move_line2.balance_cash_basis))
