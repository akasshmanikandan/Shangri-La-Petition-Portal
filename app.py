from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
import bcrypt,os
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)
app.secret_key = "c4642f8b4389df20897173d1d48ac997"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["slpp"]

# Directory for storing uploaded QR codes
UPLOAD_FOLDER = "C:/Users/Akassh Manikandan/slpp/uploads" #change it to the path in your computer
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#list of valid bioIDs
VALID_BIOIDS = [
    "K1YL8VA2HG", "7DMPYAZAP2", "D05HPPQNJ4", "2WYIM3QCK9", "DHKFIYHMAZ",
    "LZK7P0X0LQ", "H5C98XCENC", "6X6I6TSUFG", "QTLCWUS8NB", "Y4FC3F9ZGS",
    "V30EPKZQI2", "O3WJFGR5WE", "SEIQTS1H16", "X16V7LFHR2", "TLFDFY7RDG",
    "PGPVG5RF42", "FPALKDEL5T", "2BIB99Z54V", "ABQYUQCQS2", "9JSXWO4LGH",
    "QJXQOUPTH9", "GOYWJVDA8A", "6EBQ28A62V", "30MY51J1CJ", "FH6260T08H",
    "JHDCXB62SA", "O0V55ENOT0", "F3ATSRR5DQ", "1K3JTWHA05", "FINNMWJY0G",
    "CET8NUAE09", "VQKBGSE3EA", "E7D6YUPQ6J", "BPX8O0YB5L", "AT66BX2FXM",
    "1PUQV970LA", "CCU1D7QXDT", "TTK74SYYAN", "4HTOAI9YKO", "PD6XPNB80J",
    "BZW5WWDMUY", "340B1EOCMG", "CG1I9SABLL", "49YFTUA96K", "V2JX0IC633",
    "C7IFP4VWIL", "RYU8VSS4N5", "S22A588D75", "88V3GKIVSF", "8OLYIE2FRC"
]

# Middleware to check if user is logged in
def login_required(func):
    def wrapper(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login_page", error="Please log in first!"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("is_admin", False):  # Ensure 'is_admin' is set to True for admin
            return redirect(url_for("login_page", error="Access denied. Admins only!"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# Admin login credentials
ADMIN_EMAIL = "admin@petition.parliament.sr"
ADMIN_PASSWORD_HASH = bcrypt.hashpw("2025%shangrila".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

#  the home page
@app.route("/")
def index():
    return render_template("index.html")

# show the login page
@app.route("/login.html")
def login_page():
    error = request.args.get("error", "")
    return render_template("login.html", error=error)

# show the registration page
@app.route("/register.html")
def register_page():
    return render_template("register.html")

# show the petitioner dashboard
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    try:
        petitions_collection = db["petitions"]

        # get petitions created by the user
        user_petitions = list(petitions_collection.find({"user_id": session["user_id"]}))

        # get all petitions
        all_petitions = list(petitions_collection.find({}))

        for petition in all_petitions:
            petition["_id"] = str(petition["_id"])  # Convert ObjectId to string
            petition["petition_title"] = petition.pop("title", "")
            petition["petition_text"] = petition.pop("description", "")

        return render_template(
            "petitioner dashboard.html",
            user_petitions=user_petitions,
            all_petitions=all_petitions,
        )
    except Exception as e:
        return render_template(
            "petitioner dashboard.html",
            error=f"Failed to load dashboard: {str(e)}",
            user_petitions=[],
            all_petitions=[],
        )


# Sign the Petition
@app.route("/sign-petition/<petition_id>", methods=["POST"])
@login_required
def sign_petition(petition_id):
    try:
        db["petitions"].update_one(
            {"_id": ObjectId(petition_id)},
            {"$addToSet": {"signatures": session["user_id"]}}  # Avoid duplicates
        )
        return redirect(url_for("dashboard"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    #create petition
@app.route("/create-petition", methods=["GET", "POST"])
def create_petition():
    if request.method == "POST":
      
        title = request.form.get("title")
        description = request.form.get("description")
        user_id = session.get("user_id")  # Assuming user_id is stored in the session

      
        if not title or not description:
            return "Title and Description are required.", 400

        # Insert petition into the database
        db.petitions.insert_one({
            "title": title,
            "description": description,
            "user_id": user_id,
            "status": "open",
            "signatures": []
        })
        return redirect("/dashboard")  # Redirect to the dashboard after submission

    return render_template("create_petition.html")



# Serve the admin dashboard
@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    try:
        petitions_collection = db["petitions"]

        # get all petitions
        petitions = list(petitions_collection.find({}))

        # Add signature count 
        for petition in petitions:
            petition["_id"] = str(petition["_id"]) 
            petition["signature_count"] = len(petition.get("signatures", []))  

        return render_template("admin dashboard.html", petitions=petitions)
    except Exception as e:
        return render_template("admin dashboard.html", error=f"Error loading data: {str(e)}", petitions=[])


    
#for setting the signature threshold
@app.route("/set-signature-threshold", methods=["POST"])
@admin_required
def set_signature_threshold():
    try:
        # Retrieve the threshold value from the form
        threshold = request.form.get("threshold")
        print("Received threshold:", threshold)

        if not threshold or not threshold.isdigit():
            print("Invalid threshold value.")
            return redirect(url_for("admin_dashboard", error="Invalid threshold value!"))
        
        threshold = int(threshold)
        if threshold <= 0:
            print("Threshold must be greater than zero.")
            return redirect(url_for("admin_dashboard", error="Threshold must be greater than zero."))

        # Save the threshold to the database
        db["settings"].update_one(
            {"name": "signature_threshold"},
            {"$set": {"value": threshold}},
            upsert=True
        )
        print("Threshold updated successfully:", threshold)
        return redirect(url_for("admin_dashboard"))
    except Exception as e:
        print("Error setting threshold:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/get-threshold", methods=["GET"])
@admin_required
def get_threshold():
    try:
        setting = db["settings"].find_one({"name": "signature_threshold"})
        if not setting:
            print("No threshold setting found in the database.")
            return jsonify({"threshold": "Not set"})

        print("Threshold setting found:", setting)
        return jsonify({"threshold": setting.get("value", "Not set")})
    except Exception as e:
        print("Error fetching threshold:", str(e))
        return jsonify({"error": str(e)})




#to close the petition
@app.route("/admin/close-petition/<petition_id>", methods=["POST"])
@admin_required
def close_petition(petition_id):
    try:
        db["petitions"].update_one(
            {"_id": ObjectId(petition_id)}, {"$set": {"status": "closed"}}
        )
        return jsonify({"message": "Petition closed successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})


#giving a responce to the petition
@app.route("/admin/respond-petition/<petition_id>", methods=["POST"])
@admin_required
def respond_petition(petition_id):
    try:
        data = request.get_json()
        response_text = data["response"]
        db["petitions"].update_one(
            {"_id": ObjectId(petition_id)}, {"$set": {"response": response_text}}
        )
        return jsonify({"message": "Response added successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})

# Registration (Petitioner)
@app.route("/register", methods=["POST"])
def register():
    data = request.form
    file = request.files.get("qr_code")
    if not all(key in data for key in ("email", "name", "dob", "password")):
        return render_template("register.html", error="Missing required fields")
    
    email = data["email"]
    name = data["name"]
    dob = data["dob"]
    password = data["password"]
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    bioid = data.get("bioid", None)

    # for scanning qr code and automatically fill the bioID field
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            qr_data = decode(Image.open(file_path))
            if qr_data:
                bioid_from_qr = qr_data[0].data.decode('utf-8')
                if bioid_from_qr not in VALID_BIOIDS:
                    return render_template("register.html", error="Invalid BioID in QR code")
                bioid = bioid_from_qr
            else:
                return render_template("register.html", error="QR code could not be read")
        except Exception as e:
            return render_template("register.html", error=f"Error reading QR code: {e}")

    if not bioid or bioid not in VALID_BIOIDS:
        return render_template("register.html", error="Invalid BioID")

    try:
        db["users"].insert_one({
            "email": email,
            "name": name,
            "bioid": bioid,
            "dob": dob,
            "password_hash": password_hash.decode("utf-8")
        })
        return redirect(url_for("login_page"))
    except Exception as e:
        return render_template("register.html", error=f"Error: {str(e)}")
    

@app.route("/scan-qr-code", methods=["POST"])
def scan_qr_code():
    try:
        file = request.files.get("qr_code")
        if not file:
            return jsonify({"error": "No file uploaded."}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        qr_data = decode(Image.open(file_path))
        if qr_data:
            bioid_from_qr = qr_data[0].data.decode("utf-8")
            if bioid_from_qr not in VALID_BIOIDS:
                return jsonify({"error": "Invalid BioID in QR code."}), 400

            return jsonify({"bioid": bioid_from_qr}), 200
        else:
            return jsonify({"error": "QR code could not be read."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# Route to get data for visualizations
@app.route('/admin-dashboard/chart-data', methods=['GET'])
@admin_required
def get_chart_data():
    try:
        petitions_data = list(db["petitions"].find({}, {"status": 1, "category": 1, "signatures": 1}))
        for petition in petitions_data:
            petition["_id"] = str(petition["_id"])  # Convert ObjectId to string for JSON compatibility
        return jsonify(petitions_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/admin/petition-stats', methods=['GET'])
def petition_stats():
    try:
        petitions_collection = db["petitions"]

        # Group petitions by status and count them
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        stats = list(petitions_collection.aggregate(pipeline))

        labels = [item["_id"] for item in stats]
        values = [item["count"] for item in stats]

        return jsonify({"labels": labels, "values": values})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# REST API TASK 2

@app.route("/slpp/petitions", methods=["GET"])
def get_petitions():
    status = request.args.get("status")
    query = {"status": status} if status else {}
    petitions = list(db["petitions"].find(query))
    formatted_petitions = [
        {
            "petition_id": str(p["_id"]),
            "status": p.get("status", ""),
            "petition_title": p.get("title", ""),
            "petition_text": p.get("description", ""),
            "petitioner": p.get("petitioner", ""),
            "signatures": len(p.get("signatures", [])) if isinstance(p.get("signatures", []), list) else p.get("signatures", 0),
            "response": p.get("response", "No response yet"),
        }
        for p in petitions
    ]
    return jsonify({"petitions": formatted_petitions})



# Login route (Petitioner/Admin)
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return render_template("login.html", error="Email and Password are required.")

        if email == ADMIN_EMAIL:  # Admin login
            if bcrypt.checkpw(password.encode("utf-8"), ADMIN_PASSWORD_HASH.encode("utf-8")):
                session["email"] = ADMIN_EMAIL
                return redirect(url_for("admin_dashboard"))
            else:
                return render_template("login.html", error="Invalid admin credentials.")
        else:  # Petitioner login
            user = db["users"].find_one({"email": email})
            if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                session["user_id"] = str(user["_id"])
                session["email"] = email
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")


# Logout route
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
