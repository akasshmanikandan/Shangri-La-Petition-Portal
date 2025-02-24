Shangri-La Petition Platform (SLPP)

Description of the Project
The Shangri-La Petition Platform (SLPP) is a web-based application developed to enable users to create and manage petitions effectively. The administrators have extra features to monitor and manage petitions and system configurations, petitioners may create, view, and sign petitions on the platform.

This project integrates database administration, front-end and back-end programming, and user interaction to show how web technologies may be used practically.

Important Features
Petitioners (Users): 
Safe login process and user registration.
Give your petitions a title and a description.
Examine each petition and, if you'd like, sign it.

The Petitions Committee:
access to the petition management admin panel.
Check out petition statistics (open vs. closed).
Revise petition signing requirements.
As needed, reply to or close petitions.

General: 
Interactive and responsive user interface for administrators and petitioners alike.
For authentication, use secure session management.
Real-time data persistence through database integration.

Technologies Used
Backend: Python with Flask Framework.
Frontend: HTML5, CSS3, Bootstrap.
Database: MongoDB.
Tools: MongoDB Compass, Python 3.11+, VS Code.

Setup and Installation
Prerequisites
Python 3.11 or later.
MongoDB installed and running locally or on a cloud service.

Steps to Run the Application
Navigate to the Project Directory: Extract the ZIP file and navigate to the project folder:

cd SLPP

Install Python Dependencies: Install the required Python packages:

pip install flask pymongo dnspython bcrypt flask-wtf

Restore the Database from the Provided Dump:

Ensure MongoDB is running.
Place the provided dump folder in your desired directory (e.g., /dump).
Use the following command to restore the database:

mongorestore --db slpp <path_to_dump_folder>

Replace <path_to_dump_folder> with the path to the provided dump folder.

Run the Application: Start the Flask development server:

python app.py
Open a browser and navigate to http://127.0.0.1:5000 to access the application.

SLPP/
├── static/                # CSS, JavaScript, Images
├── templates/             # HTML Templates
│   ├── index.html         # Homepage
│   ├── login.html         # Login Page
│   ├── register.html      # Registration Page
│   ├── petitioner_dashboard.html  # User Dashboard
│   ├── admin_dashboard.html       # Admin Dashboard
├── app.py                 # Main Flask Application
└── README.md              # Project Documentation

Instructions for Use
Petitioners:
Create a new account by registering.
Log in by going to the dashboard.
Make Petition: Send in petitions with pertinent headings and summaries.
Sign petitions: See the available petitions and sign them.

Supervisors:
Go to the admin dashboard to log in.
View, close, or reply to petitions to manage them.
Data: See the statistics of petitions.
Update Thresholds: Adjust the thresholds for signatures.

Use the BioID_QR_Codes to upload and register as a user.

database files are available in database folder.


Project Highlights
Real-time Functionality: MongoDB provides real-time reflection of user activities.
Secure Authentication: Session-based authentication is used, and passwords are hashed for protection.


