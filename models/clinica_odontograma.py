from odoo import fields, models

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


class ClinicaOdontograma(models.Model):
    _name = 'clinica.odontograma'
    _description = 'Dental Odontogram'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc'

    paciente_id = fields.Many2one('res.partner', string='Patient', required=True, tracking=True)
    fecha = fields.Date(string='Date', default=fields.Date.today, required=True)
    notas_generales = fields.Text(string='General Notes')
    lineas_ids = fields.One2many('clinica.odontograma.linea', 'odontograma_id', string='Lines')
    state = fields.Selection([
        ('borrador', 'Draft'),
        ('confirmado', 'Confirmed'),
    ], string='Status', default='borrador', tracking=True)

    def action_confirmar(self):
        self.write({'state': 'confirmado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})


class ClinicaOdontogramaLinea(models.Model):
    _name = 'clinica.odontograma.linea'
    _description = 'Odontogram Line'

    odontograma_id = fields.Many2one('clinica.odontograma', string='Odontogram',
                                      required=True, ondelete='cascade')
    numero_pieza = fields.Selection(PIEZAS_FDI, string='Tooth Number', required=True)
    estado = fields.Selection([
        ('sano', 'Healthy'),
        ('caries', 'Cavity'),
        ('fractura', 'Fracture'),
        ('ausente', 'Missing'),
        ('corona', 'Crown'),
        ('implante', 'Implant'),
        ('endodoncia', 'Root Canal'),
        ('extraccion_indicada', 'Extraction Indicated'),
        ('obturacion', 'Filling'),
    ], string='Condition', required=True)
    superficie = fields.Selection([
        ('oclusal', 'Occlusal'),
        ('vestibular', 'Vestibular'),
        ('lingual', 'Lingual'),
        ('mesial', 'Mesial'),
        ('distal', 'Distal'),
        ('cervical', 'Cervical'),
    ], string='Surface')
    notas = fields.Text(string='Notes')
