from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

# Map appointment type category/name keywords to clinica.cita tipo_cita values
_APPOINTMENT_TYPE_MAP = {
    'limpieza': 'limpieza', 'cleaning': 'limpieza',
    'extraccion': 'extraccion', 'extracción': 'extraccion', 'extraction': 'extraccion',
    'ortodoncia': 'ortodoncia', 'orthodontic': 'ortodoncia',
    'endodoncia': 'endodoncia', 'root canal': 'endodoncia',
    'protesis': 'protesis', 'prótesis': 'protesis', 'prosthetic': 'protesis',
    'estetica': 'estetica', 'estética': 'estetica', 'aesthetic': 'estetica',
    'urgencia': 'urgencia', 'emergency': 'urgencia',
    'control': 'control', 'follow': 'control',
    'consulta': 'consulta', 'consultation': 'consulta',
}


def _map_tipo_cita(name):
    if not name:
        return 'consulta'
    lower = name.lower()
    for keyword, tipo in _APPOINTMENT_TYPE_MAP.items():
        if keyword in lower:
            return tipo
    return 'consulta'


class CalendarEventClinicaIntegration(models.Model):
    _inherit = 'calendar.event'

    clinica_cita_id = fields.Many2one(
        'clinica.cita', string='Cita Clínica',
        readonly=True, copy=False, ondelete='set null',
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._sync_clinica_cita()
        return records

    def write(self, vals):
        res = super().write(vals)
        # Re-sync when appointment_type_id is set or attendees/times change
        trigger_fields = {'appointment_type_id', 'partner_ids', 'start', 'stop'}
        if trigger_fields & set(vals):
            for rec in self:
                rec._sync_clinica_cita()
        return res

    def _sync_clinica_cita(self):
        """Create or update a clinica.cita linked to this calendar.event.

        Triggers when the event comes from the appointment module
        (appointment_type_id is set) or when the context flag
        'create_clinica_cita' is True.
        """
        self.ensure_one()

        # Only proceed if appointment_type_id field exists (appointment module)
        # OR if the context explicitly requests cita creation
        has_appt_type = hasattr(self, 'appointment_type_id') and self.appointment_type_id
        force_create = self.env.context.get('create_clinica_cita')

        if not has_appt_type and not force_create:
            return

        # Skip if already linked
        if self.clinica_cita_id:
            return

        # Find the patient partner (first non-internal attendee)
        paciente = self._get_patient_partner()
        if not paciente:
            return

        # Ensure the partner is marked as patient
        if not paciente.es_paciente:
            paciente.sudo().write({'es_paciente': True})

        # Determine tipo_cita from appointment type name
        tipo_nombre = ''
        if has_appt_type:
            tipo_nombre = self.appointment_type_id.name or ''
        tipo_cita = _map_tipo_cita(tipo_nombre)

        # Find the responsible dentist: organizer or first internal user
        dentista = self._get_dentist_user()

        if not dentista:
            _logger.warning('clinica_dental: no dentist found for calendar.event %d', self.id)
            return

        cita_vals = {
            'paciente_id': paciente.id,
            'dentista_id': dentista.id,
            'fecha_inicio': self.start,
            'fecha_fin': self.stop,
            'tipo_cita': tipo_cita,
            'motivo': tipo_nombre or self.name or '',
            'state': 'confirmada',
            'calendar_event_id': self.id,
        }
        cita = self.env['clinica.cita'].sudo().create(cita_vals)
        self.sudo().write({'clinica_cita_id': cita.id})
        _logger.info(
            'clinica_dental: auto-created clinica.cita %d for calendar.event %d (patient: %s)',
            cita.id, self.id, paciente.name,
        )

    def _get_patient_partner(self):
        """Return the patient res.partner from the event's attendees."""
        internal_partner_ids = self.env['res.users'].search([]).mapped('partner_id.id')
        for partner in self.partner_ids:
            if partner.id not in internal_partner_ids:
                return partner
        # Fallback: return any attendee that is already a patient
        for partner in self.partner_ids:
            if partner.es_paciente:
                return partner
        return None

    def _get_dentist_user(self):
        """Return the res.users dentist for the event."""
        # Try the event organizer first
        if self.user_id:
            return self.user_id
        # Then any attendee that is an internal user
        internal_users = self.env['res.users'].search([('share', '=', False)])
        partner_to_user = {u.partner_id.id: u for u in internal_users}
        for partner in self.partner_ids:
            if partner.id in partner_to_user:
                return partner_to_user[partner.id]
        return None
