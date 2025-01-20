from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Load Database Configuration from .env
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)

class Applicant(db.Model):
    __tablename__ = 'applicants'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    resume = db.Column(db.Text, nullable=False)

# API Endpoints
@app.route('/api/jobs')
def get_jobs():
    jobs = Job.query.all()
    data = [{"id": job.id, "company": job.company, "title": job.title, "description": job.description, "location": job.location, "salary": job.salary} for job in jobs]
    return jsonify(data)

@app.route('/api/jobs/<int:job_id>')
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    data = {"id": job.id, "company": job.company, "title": job.title, "description": job.description, "location": job.location, "salary": job.salary}
    return jsonify(data)

@app.route('/api/job/post', methods=['POST'])
def post_job():
    data = request.json
    job_details = Job(
        company = data['company'],
        title = data['title'],
        description=data['description'],
        location=data['location'],
        salary=data['salary']
    )
    db.session.add(job_details)
    db.session.commit()
    return jsonify({"message": "Job post created successfully!", "job_id": job_details.id, "statusCode": 201})

@app.route('/api/job/apply', methods=['POST'])
def apply_job():
    applicant_data = request.json
    job = Job.query.get(applicant_data.job_id)
    
    if not job:
        return jsonify({"message": "This is not a valid job_id"}, 404)
    
    job_applicantData = Applicant(
        job_id = applicant_data['job_id'],
        fname = applicant_data['fname'],
        lname = applicant_data['lname'],
        email = applicant_data['email'],
        phone = applicant_data['phone'],
        resume = applicant_data['resume']
    )
    
    db.session.add(job_applicantData)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully!", "applicant_id": job_applicantData.id, "statusCode": 201})
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
