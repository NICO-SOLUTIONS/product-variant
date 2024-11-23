# Copyright 2015-17 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestSaleOrderLineVariantDescription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.tax_model = cls.env["account.tax"]
        cls.pricelist_model = cls.env["product.pricelist"]
        cls.uom_uom_model = cls.env["uom.uom"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.product_model = cls.env["product.product"]
        cls.so_model = cls.env["sale.order"]
        cls.so_line_model = cls.env["sale.order.line"]
        cls.partner = cls.env.ref("base.res_partner_1")

    def test_product_id_change(self):
        pricelist = self.pricelist_model.search([("name", "=", "Public Pricelist")])
        if not pricelist:
            pricelist = self.pricelist_model.create(
                {"name": "Public Pricelist", "currency_id": self.env.ref("base.USD").id}
            )
        pricelist = pricelist[0]

        uom = self.uom_uom_model.search([("name", "=", "Units")])[0]
        tax_include = self.tax_model.create(
            dict(name="Include tax", amount="0.21", price_include=True)
        )
        product_tmpl = self.product_tmpl_model.create(
            dict(
                name="Product template",
                list_price="121",
                taxes_id=[(6, 0, [tax_include.id])],
            )
        )
        product_tmpl.product_variant_id.update(
            dict(
                variant_description_sale="Product variant description",
            )
        )
        product = product_tmpl.product_variant_id
        fp = self.fiscal_position_model.create(dict(name="fiscal position", sequence=1))
        so = self.so_model.create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "fiscal_position_id": fp.id,
            }
        )
        so_line = self.so_line_model.create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 1.0,
                "product_uom": uom.id,
                "price_unit": 121.0,
                "order_id": so.id,
            }
        )
        so_line._onchange_product_id_warning()
        so_line_name_without_product_name = so_line.name.split("\n", 1)[-1]
        self.assertEqual(
            product.variant_description_sale, so_line_name_without_product_name
        )
