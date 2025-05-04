from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Load Excel files
student_file = "C:/Users/priya/OneDrive/Documents/Nss ppt/Documents/data base of B.Tech CSE  HPTU for Photocop.xlsx"
subject_file = "Student who have appeared.xlsx"

# Read data
df_students = pd.read_excel(student_file, dtype={"University Roll no": str})
df_subjects = pd.read_excel(subject_file, dtype={"University Roll no": str})

# Memory-based status storage
status_data = {}  # {"roll_no": {"form_submitted": True/False, "payment_done": True/False}}

@app.route('/')
def home():
    return render_template("index.HTML")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", 'download.jpg')

@app.route('/get_student/<roll_no>', methods=['GET'])
def get_student(roll_no):
    try:
        student = df_students[df_students['University Roll no'] == roll_no]
        if not student.empty:
            student_data = {
                "applicant_name": student.iloc[0].get("Student Name", ""),
                "father_name": student.iloc[0].get("Father's Name", ""),
                "course": student.iloc[0].get("Course", ""),
                "branch": student.iloc[0].get("Branch", ""),
                "exam_month": str(student.iloc[0].get("Exam Month", "")),
                "contact": student.iloc[0].get("Contact", ""),
                "address": student.iloc[0].get("Address", ""),
                "college": student.iloc[0].get("College", ""),
                "exam_center": student.iloc[0].get("Exam Center", "")
            }
            return jsonify(student_data)
        else:
            return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_subjects', methods=['POST'])
def get_subjects():
    data = request.get_json()
    roll_number = data.get("roll_no")

    if not roll_number:
        return jsonify({"subjects": []})

    student_data = df_subjects[df_subjects["University Roll no"] == roll_number]

    if student_data.empty:
        return jsonify({"subjects": []})

    subjects = student_data[["Subject Code", "Subject"]].to_dict(orient="records")
    return jsonify({"subjects": subjects})

@app.route('/submit_form', methods=['POST'])
def submit_form():
    data = request.get_json()
    roll_no = data.get("roll_no")
    if roll_no:
        status_data.setdefault(roll_no, {})
        status_data[roll_no]['form_submitted'] = True
        status_data[roll_no]['payment_done'] = status_data[roll_no].get('payment_done', False)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/pay_now', methods=['POST'])
def pay_now():
    data = request.get_json()
    roll_no = data.get("roll_no")
    if roll_no:
        status_data.setdefault(roll_no, {})
        status_data[roll_no]['payment_done'] = True
        status_data[roll_no]['form_submitted'] = status_data[roll_no].get('form_submitted', False)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/status/<roll_no>', methods=['GET'])
def check_status(roll_no):
    status = status_data.get(roll_no)
    if status:
        return jsonify({
            "form_submitted": status.get('form_submitted', False),
            "payment_done": status.get('payment_done', False)
        })
    else:
        return jsonify({"error": "No form submitted yet for this roll number."}), 404

if __name__ == '__main__':
    app.run(debug=True)
