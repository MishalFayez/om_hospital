from odoo import api, fields, models
import base64
import io


class PatientAppointmentXlsx(models.AbstractModel):
    _name = 'report.om_hospital.report_patient_appointment_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, patients):
        print('mmmmmmmmmmmmmmmm', data, patients)
        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow'})
        sheet = workbook.add_worksheet('Appointments')
        row = 3
        col = 3
        sheet.write(row, col, 'Reference', bold)
        sheet.write(row, col + 1, 'Patient Name', bold)

        for appointment in data['appointments']:
            row += 1
            sheet.write(row, col, appointment['name'])
            sheet.write(row, col + 1, appointment['patient_id'][1])
