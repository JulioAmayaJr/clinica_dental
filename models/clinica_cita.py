from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClinicaCita(models.Model):
    _name = 'clinica.cita'
    _description = 'Dental Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    paciente_id = fields.Many2one('res.partner', string='Patient', required=True, tracking=True)
    dentista_id = fields.Many2one('res.users', string='Dentist', required=True, tracking=True)
    fecha_inicio = fields.Datetime(string='Start Date', required=True, tracking=True)
    fecha_fin = fields.Datetime(string='End Date', required=True)
    duracion = fields.Float(string='Duration (hours)', compute='_compute_duracion', store=True)
    motivo = fields.Char(string='Reason')
    tipo_cita = fields.Selection([
        ('consulta', 'Consultation'),
        ('limpieza', 'Cleaning'),
        ('extraccion', 'Extraction'),
        ('ortodoncia', 'Orthodontics'),
        ('endodoncia', 'Root Canal'),
        ('protesis', 'Prosthetics'),
        ('estetica', 'Aesthetics'),
        ('urgencia', 'Emergency'),
        ('control', 'Follow-up'),
        ('otro', 'Other'),
    ], string='Appointment Type', default='consulta')
    state = fields.Selection([
        ('agendada', 'Scheduled'),
        ('confirmada', 'Confirmed'),
        ('en_proceso', 'In Progress'),
        ('completada', 'Completed'),
        ('cancelada', 'Cancelled'),
        ('no_asistio', 'No Show'),
    ], string='Status', default='agendada', tracking=True)
    notas = fields.Text(string='Notes')
    tratamiento_ids = fields.One2many('clinica.tratamiento', 'cita_id', string='Treatments')
    calendar_event_id = fields.Many2one('calendar.event', string='Calendar Event',
                                         readonly=True, copy=False)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order',
                                     readonly=True, copy=False)
    color = fields.Integer(string='Color')
    alergias_paciente = fields.Text(related='paciente_id.alergias', string='Patient Allergies',
                                     readonly=True)

    @api.depends('fecha_inicio', 'fecha_fin')
    def _compute_duracion(self):
        for rec in self:
            if rec.fecha_inicio and rec.fecha_fin:
                delta = rec.fecha_fin - rec.fecha_inicio
                rec.duracion = delta.total_seconds() / 3600.0
            else:
                rec.duracion = 0.0

    @api.constrains('fecha_inicio', 'fecha_fin', 'dentista_id')
    def _check_solapamiento(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('dentista_id', '=', rec.dentista_id.id),
                ('state', 'not in', ['cancelada', 'no_asistio']),
                ('fecha_inicio', '<', rec.fecha_fin),
                ('fecha_fin', '>', rec.fecha_inicio),
            ]
            if self.search(domain, limit=1):
                raise ValidationError(
                    _('The dentist %s already has an appointment in this time slot.')
                    % rec.dentista_id.name
                )

    def action_confirmar(self):
        for rec in self:
            rec.state = 'confirmada'
            rec._crear_calendar_event()

    def action_en_proceso(self):
        self.write({'state': 'en_proceso'})

    def action_completar(self):
        for rec in self:
            rec.state = 'completada'
            rec.tratamiento_ids.filtered(
                lambda t: t.state == 'en_proceso'
            ).write({'state': 'completado'})

    def action_cancelar(self):
        for rec in self:
            rec.state = 'cancelada'
            if rec.calendar_event_id:
                rec.calendar_event_id.unlink()

    def action_no_asistio(self):
        self.write({'state': 'no_asistio'})

    def action_generar_venta(self):
        self.ensure_one()
        tratamientos = self.tratamiento_ids.filtered(
            lambda t: t.state == 'completado' and t.producto_id
        )
        if not tratamientos:
            return
        order_lines = [(0, 0, {
            'product_id': t.producto_id.id,
            'product_uom_qty': t.cantidad,
            'price_unit': t.precio_unitario,
        }) for t in tratamientos]
        order = self.env['sale.order'].create({
            'partner_id': self.paciente_id.id,
            'order_line': order_lines,
        })
        self.sale_order_id = order.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
        }

    def _crear_calendar_event(self):
        self.ensure_one()
        if self.calendar_event_id:
            return
        event = self.env['calendar.event'].create({
            'name': _('Appointment: %s - %s') % (self.paciente_id.name, self.tipo_cita),
            'start': self.fecha_inicio,
            'stop': self.fecha_fin,
            'partner_ids': [(4, self.dentista_id.partner_id.id),
                            (4, self.paciente_id.id)],
            'description': self.notas or '',
        })
        self.calendar_event_id = event.id

    @api.onchange('paciente_id')
    def _onchange_paciente_id(self):
        if self.paciente_id and self.paciente_id.alergias:
            return {
                'warning': {
                    'title': _('Patient Allergies'),
                    'message': _('Warning: This patient has registered allergies:\n%s')
                               % self.paciente_id.alergias,
                }
            }
