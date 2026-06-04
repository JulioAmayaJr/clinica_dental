from odoo import api, fields, models

PIEZAS_FDI = [
    ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'),
    ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'),
    ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'),
    ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'),
    ('31', '31'), ('32', '32'), ('33', '33'), ('34', '34'),
    ('35', '35'), ('36', '36'), ('37', '37'), ('38', '38'),
    ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'),
    ('45', '45'), ('46', '46'), ('47', '47'), ('48', '48'),
]


class ClinicaTratamiento(models.Model):
    _name = 'clinica.tratamiento'
    _description = 'Dental Treatment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc'

    paciente_id = fields.Many2one('res.partner', string='Patient', required=True, tracking=True)
    cita_id = fields.Many2one('clinica.cita', string='Appointment')
    dentista_id = fields.Many2one('res.users', string='Dentist', required=True, tracking=True)
    fecha = fields.Date(string='Date', default=fields.Date.today, required=True)
    pieza_dental = fields.Selection(PIEZAS_FDI, string='Tooth')
    tipo_tratamiento = fields.Selection([
        ('limpieza', 'Cleaning'),
        ('extraccion', 'Extraction'),
        ('obturacion', 'Filling'),
        ('endodoncia', 'Root Canal'),
        ('corona', 'Crown'),
        ('implante', 'Implant'),
        ('ortodoncia', 'Orthodontics'),
        ('blanqueamiento', 'Whitening'),
        ('protesis', 'Prosthetics'),
        ('radiografia', 'X-Ray'),
        ('otro', 'Other'),
    ], string='Treatment Type', required=True)
    descripcion = fields.Text(string='Description')
    producto_id = fields.Many2one('product.product', string='Product/Service')
    cantidad = fields.Float(string='Quantity', default=1.0)
    precio_unitario = fields.Float(string='Unit Price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    state = fields.Selection([
        ('planificado', 'Planned'),
        ('en_proceso', 'In Progress'),
        ('completado', 'Completed'),
        ('cancelado', 'Cancelled'),
    ], string='Status', default='planificado', tracking=True)
    notas_clinicas = fields.Text(string='Clinical Notes')

    @api.depends('cantidad', 'precio_unitario')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.cantidad * rec.precio_unitario

    @api.onchange('producto_id')
    def _onchange_producto_id(self):
        if self.producto_id:
            self.precio_unitario = self.producto_id.lst_price

    def action_iniciar(self):
        self.write({'state': 'en_proceso'})

    def action_completar(self):
        self.write({'state': 'completado'})

    def action_cancelar(self):
        self.write({'state': 'cancelado'})
