# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Stock Change Quantity Reason",
    'summary': """
        Stock Quantity Change Reason """,
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Warehouse Management',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/base_config_view.xml',
        'views/stock_change_product_reason_view.xml',
        'views/stock_inventory_line_view.xml',
        'wizard/stock_product_change_qty.xml'
    ],
    'installable': True,
}
