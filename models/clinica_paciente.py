from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class ClinicaPaciente(models.Model):
    _inherit = 'res.partner'

    es_paciente = fields.Boolean(string='Is Patient', default=False)
    historia_clinica = fields.Text(string='Clinical History')
    fecha_nacimiento = fields.Date(string='Date of Birth')
    edad = fields.Integer(string='Age', compute='_compute_edad', store=False)
    genero = fields.Selection([
        ('masculino', 'Male'),
        ('femenino', 'Female'),
        ('otro', 'Other'),
    ], string='Gender')
    grupo_sanguineo = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ], string='Blood Type')
    alergias = fields.Text(string='Allergies')
    enfermedades_sistemicas = fields.Text(string='Systemic Diseases')
    medicamentos_actuales = fields.Text(string='Current Medications')
    fumador = fields.Boolean(string='Smoker', default=False)
    contacto_emergencia = fields.Char(string='Emergency Contact')
    telefono_emergencia = fields.Char(string='Emergency Phone')

    cita_ids = fields.One2many('clinica.cita', 'paciente_id', string='Appointments')
    tratamiento_ids = fields.One2many('clinica.tratamiento', 'paciente_id', string='Treatments')
    odontograma_ids = fields.One2many('clinica.odontograma', 'paciente_id', string='Odontograms')
    documento_medico_ids = fields.One2many('clinica.documento.medico', 'paciente_id', string='Medical Documents')
    presupuesto_ids = fields.One2many('sale.order', 'partner_id', string='Budgets',
                                       domain=[('es_presupuesto_dental', '=', True)])

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        today = fields.Date.today()
        for rec in self:
            if rec.fecha_nacimiento:
                rec.edad = relativedelta(today, rec.fecha_nacimiento).years
            else:
                rec.edad = 0

    def action_open_nueva_cita(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'clinica.cita',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_paciente_id': self.id},
        }
