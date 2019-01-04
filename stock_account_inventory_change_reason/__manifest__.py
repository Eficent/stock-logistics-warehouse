# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': "Stock Account Inventory Change Reason",
    'summary': """
        Stock Account Inventory Change Reason """,
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Warehouse Management',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'stock_account',
        'stock_change_qty_reason'
    ],
    'data': [
        'views/stock_change_product_reason_view.xml',
        'views/stock_move_view.xml',
    ],
    'installable': True,
}
