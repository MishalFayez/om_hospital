from odoo import api, fields, models, _


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _description = "Hospital Doctor"
    _rec_name = "doctor_name"

    doctor_name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age', tracking=True, copy=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    note = fields.Text(string='Description')
    image=fields.Binary(string='Patient Image')
    appointment_count = fields.Integer(String='Appointment Count', compute='_compute_appointment_count')
    active = fields.Boolean(string="Active", default=True)


    def _compute_appointment_count(self):
        for rec in self:
            appointment_count = self.env['hospital.appointment'].search_count([('doctor_id', '=', rec.id)])
            rec.appointment_count = appointment_count

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('doctor_name'):
            default['doctor_name'] = _('%s (copy)', self.doctor_name)
        default['note'] = "Copy Record"
        return super(HospitalDoctor, self).copy(default=default)