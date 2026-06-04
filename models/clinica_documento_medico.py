from odoo import api, fields, models, _


class ClinicaDocumentoMedico(models.Model):
    _name = 'clinica.documento.medico'
    _description = 'Medical Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc'

    paciente_id = fields.Many2one('res.partner', string='Patient', required=True, tracking=True)
    nombre = fields.Char(string='Document Name', required=True)
    tipo_documento = fields.Selection([
        ('radiografia_periapical', 'Periapical X-Ray'),
        ('radiografia_panoramica', 'Panoramic X-Ray'),
        ('radiografia_bitewing', 'Bitewing X-Ray'),
        ('radiografia_cefalometrica', 'Cephalometric X-Ray'),
        ('fotografia_intraoral', 'Intraoral Photo'),
        ('fotografia_extraoral', 'Extraoral Photo'),
        ('consentimiento_informado', 'Informed Consent'),
        ('receta', 'Prescription'),
        ('laboratorio', 'Lab Results'),
        ('otro', 'Other'),
    ], string='Document Type', required=True, tracking=True)
    fecha = fields.Date(string='Date', default=fields.Date.today, required=True)
    subido_por = fields.Many2one('res.users', string='Uploaded By',
                                  default=lambda self: self.env.user,
                                  readonly=True)
    dentista_id = fields.Many2one('res.users', string='Directed To (Dentist)', tracking=True)
    cita_id = fields.Many2one('clinica.cita', string='Related Appointment')
    tratamiento_id = fields.Many2one('clinica.tratamiento', string='Related Treatment')
    descripcion = fields.Text(string='Description')
    adjunto_ids = fields.Many2many('ir.attachment', 'documento_medico_attachment_rel',
                                    'documento_id', 'attachment_id',
                                    string='Attachments')
    imagen_principal = fields.Binary(string='Main Image', attachment=True)
    imagen_filename = fields.Char(string='Image Filename')
    state = fields.Selection([
        ('pendiente_revision', 'Pending Review'),
        ('revisado', 'Reviewed'),
        ('archivado', 'Archived'),
    ], string='Status', default='pendiente_revision', tracking=True)
    es_confidencial = fields.Boolean(string='Confidential', default=False)
    notas_dentista = fields.Text(string='Dentist Notes')

    def action_marcar_revisado(self):
        for rec in self:
            rec.state = 'revisado'
            if rec.subido_por and rec.subido_por.partner_id:
                rec.message_post(
                    body=_('Document <b>%s</b> has been reviewed by %s.')
                         % (rec.nombre, self.env.user.name),
                    subtype_xmlid='mail.mt_note',
                    partner_ids=[rec.subido_por.partner_id.id],
                )

    def action_archivar(self):
        self.write({'state': 'archivado'})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.dentista_id and rec.dentista_id.partner_id:
                tipo_label = dict(rec._fields['tipo_documento'].selection).get(
                    rec.tipo_documento, rec.tipo_documento
                )
                rec.message_post(
                    body=_('You have a new <b>%s</b> from patient <b>%s</b> pending review.')
                         % (tipo_label, rec.paciente_id.name),
                    subtype_xmlid='mail.mt_note',
                    partner_ids=[rec.dentista_id.partner_id.id],
                )
        return records
