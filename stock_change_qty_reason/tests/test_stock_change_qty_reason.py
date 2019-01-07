# pylint: disable=import-error,protected-access,too-few-public-methods
# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockQuantityChangeReason(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockQuantityChangeReason, cls).setUpClass()

        # MODELS
        cls.product_product_model = cls.env['product.product']
        cls.product_category_model = cls.env['product.category']
        cls.wizard_model = cls.env['stock.change.product.qty']
        cls.encoded_reason_id = cls.env['stock.inventory.line.reason']

        # INSTANCES
        cls.category = cls.product_category_model.create({
            'name': 'Physical (test)'})

    def _create_product(self, name):
        return self.product_product_model.create({
            'name': name,
            'categ_id': self.category.id,
            'type': 'product'})

    def _product_change_qty(self, product, new_qty, reason_id,
                            encoded_reason_id=None):
        wizard = self.wizard_model.create({
            'product_id': product.id,
            'new_quantity': new_qty,
            'reason_id': reason_id,
            'encoded_reason':
                encoded_reason_id.id if encoded_reason_id else False
        })
        wizard.change_product_qty()

    def _create_reason(self, name, description=None):
        return self.encoded_reason_id.create({
            'name': name,
            'description': description})

    def test_product_change_qty(self):
        """ Check product quantity update move reason is well set
        """

        # create products
        product2 = self._create_product('product_product_2')
        product3 = self._create_product('product_product_3')
        product4 = self._create_product('product_product_4')
        product5 = self._create_product('product_product_5')
        product6 = self._create_product('product_product_6')

        # update qty on hand and add reason
        self._product_change_qty(product2, 10, 'product_2_reason')
        self._product_change_qty(product3, 0, 'product_3_reason')
        self._product_change_qty(product4, 0, 'product_4_reason')
        self._product_change_qty(product5, 10, 'product_5_reason')
        self._product_change_qty(product6, 0, 'product_6_reason')

        # check stock moves created
        move2 = self.env['stock.move'].search([('product_id', '=',
                                                product2.id)])
        move3 = self.env['stock.move'].search([('product_id', '=',
                                                product3.id)])
        move4 = self.env['stock.move'].search([('product_id', '=',
                                                product4.id)])
        move5 = self.env['stock.move'].search([('product_id', '=',
                                                product5.id)])
        move6 = self.env['stock.move'].search([('product_id', '=',
                                                product6.id)])

        self.assertEqual(move2.origin, 'product_2_reason')
        self.assertFalse(move3)
        self.assertFalse(move4)
        self.assertEqual(move5.origin, 'product_5_reason')
        self.assertFalse(move6)

    def test_product_change_qty_with_tabuled_reason(self):
        """ Check product quantity update move reason is well set
        """
        # create reason
        reason = self._create_reason('Test', 'Description Test')
        # create products
        product2 = self._create_product('product_product_2')
        product3 = self._create_product('product_product_3')

        # update qty on hand and add reason
        self._product_change_qty(product2, 10, reason.name, reason)
        self._product_change_qty(product3, 0, reason.name, reason)

        # check stock moves created
        move2 = self.env['stock.move'].search([('product_id', '=',
                                                product2.id)])
        move3 = self.env['stock.move'].search([('product_id', '=',
                                                product3.id)])
        # asserts
        self.assertEqual(move2.origin, reason.name)
        self.assertFalse(move3)

    def test_onchange_encoded_reason(self):
        reason = self._create_reason('Test', 'Description Test')
        wiz = self.env['stock.change.product.qty'].new(
            {'encoded_reason': reason.id})
        wiz.onchange_encoded_reason()
        self.assertEqual(wiz.reason, wiz.encoded_reason_id.name)
