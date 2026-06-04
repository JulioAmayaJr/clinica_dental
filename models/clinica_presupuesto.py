from odoo import fields, models


class SaleOrderClinicaDental(models.Model):
    _inherit = 'sale.order'

    es_presupuesto_dental = fields.Boolean(string='Is Dental Budget', default=False)
    tipo_presupuesto = fields.Selection([
        ('preventivo', 'Preventive'),
        ('correctivo', 'Corrective'),
        ('estetico', 'Aesthetic'),
        ('ortodontico', 'Orthodontic'),
    ], string='Budget Type')
    notas_clinicas = fields.Text(string='Clinical Notes')
