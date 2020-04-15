# 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Account Manual Adjustment",
    "summary": "Shows in the product inventory stock value and the accounting "
               "value and allows to reconcile them",
    "version": "11.0.1.0.0",
    "author": "ForgeFlow S.L., "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_account", "stock_inventory_revaluation",
                "account_move_line_stock_info"],
    "data": [
        "data/stock_valuation_account_manual_adjustment_data.xml",
        "security/stock_valuation_account_manual_adjustment_security.xml",
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/stock_picking_view.xml",
        "views/account_move_line_view.xml",
        "views/stock_valuation_account_manual_adjustment_view.xml",
        "wizards/mass_create_view.xml",
        "wizards/stock_valuation_account_mass_adust_picking.xml"
    ],
    'pre_init_hook': 'pre_init_hook',
    "license": "AGPL-3",
    'installable': True,
}
