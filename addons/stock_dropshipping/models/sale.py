# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        if 'product_uom_qty' in vals and vals.get('order_id'):
            order = self.env['sale.order'].browse(vals.get('order_id'))
            existing_line = order.order_line.filtered(
                lambda line: line.product_id.id == vals.get('product_id')
            )
            if existing_line:
                po_line = self.env['purchase.order.line'].search([
                    ('sale_line_id', 'in', existing_line.ids),
                    ('order_id.state', '!=', 'cancel')
                ])
                if po_line:
                    raise UserError(
                        _('Please reuse the order line with the same product for drop shipping instead of creating a new line which can not be linked!')
                    )
        res = super(SaleOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'product_uom_qty' in vals:
            for line in self:
                po_line = self.env['purchase.order.line'].search([
                    ('sale_line_id', '=', line.id),
                    ('order_id.state', '!=', 'cancel')
                ])
                if po_line:
                    line.move_ids = po_line.move_ids

        res = super(SaleOrderLine, self).write(vals)
        return res
