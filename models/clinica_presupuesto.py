from odoo import fields, models


class ClinicaPresupuesto(models.Model):
    _name = 'clinica.presupuesto'
    _description = 'Dental Budget'
    _inherit = ['sale.order']
    _table = 'clinica_presupuesto'

    tipo_presupuesto = fields.Selection([
        ('preventivo', 'Preventive'),
        ('correctivo', 'Corrective'),
        ('estetico', 'Aesthetic'),
        ('ortodontico', 'Orthodontic'),
    ], string='Budget Type')
    notas_clinicas = fields.Text(string='Clinical Notes')

    # Reverse relation for res.partner (paciente)
    paciente_id = fields.Many2one('res.partner', string='Patient',
                                   related='partner_id', store=True, readonly=True)
