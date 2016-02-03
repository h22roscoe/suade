from flask import Flask, Response
from flask_restful import abort, Api, Resource
from dicttoxml import dicttoxml
from pg import DB
import fpdf
import ast

app = Flask(__name__.split('.')[0])
api = Api(app)

db = DB(host='candidate.suade.org', dbname='suade', port=5432,
                user='interview', passwd='LetMeIn')

def getreport(report_id):
    q = db.query("SELECT type FROM reports WHERE id = $1", (report_id))
    q = q.namedresult()
    return ast.literal_eval(q[0].type)

@api.representation('application/pdf') 
def pdf_rep(data, code, headers):
    pdf = fpdf.FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_font('Arial','B',16);
    pdf.set_title("The Report")
    pdf.cell(0, 10, "The Report", align='C', ln=1, border='B')
    pdf.ln(5)
    pdf.cell(0, 10, "Organization: " + data['organization'], align='R', ln=1)
    pdf.cell(0, 10, "Reported: " + data['reported_at'], align='R', ln=1)
    pdf.cell(0, 10, "Created: " + data['created_at'], align='R', ln=1)
    for item in data['inventory']:
        item = item.items()
        pdf.cell(0, 10, item[1][1] + ": " + item[0][1], align='L', ln=1)
    pdf.output("report.pdf")
    f = file("report.pdf", "r")
    resp = Response(f, status=code, headers=headers,
                    mimetype='application/pdf')
    return resp

@api.representation('application/xml')
def xml_rep(data, code, headers):
    resp = Response(dicttoxml(data), status=code,
                    headers=headers, mimetype='application/xml')
    return resp

def abort_if_report_doesnt_exist(report_id):
    numreports = db.query("SELECT count(id) FROM reports").namedresult()
    numreports = numreports[0].count
    if report_id < 1 or report_id > numreports:
       abort(404, message="Report {} doesn't exist".format(report_id))

# Report in XML
# shows a single report item as XML and lets you delete a report
# based on the report_id
@api.resource('/reports/xml/<report_id>')
class ReportXML(Resource):
    def get(self, report_id):
        report_id = int(report_id)
        abort_if_report_doesnt_exist(report_id)
        dic = getreport(report_id)
        return xml_rep(dic, 200, {})

    def delete(self, report_id):
        report_id = int(report_id)
        abort_if_report_doesnt_exist(todo_id)
        db.delete('reports', id=report_id)
        return '', 204

# Report in PDF
# shows a single report item as PDF and lets you delete a report
# based on the report_id
@api.resource('/reports/pdf/<report_id>')
class ReportPDF(Resource):
    def get(self, report_id):
        report_id = int(report_id)
        abort_if_report_doesnt_exist(report_id)
        dic = getreport(report_id)
        return pdf_rep(dic, 200, {}) 

    def delete(self, report_id):
        report_id = int(report_id)
        abort_if_report_doesnt_exist(todo_id)
        db.delete('reports', id=report_id)
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
