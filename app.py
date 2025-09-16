from flask import Flask, render_template,request,url_for,redirect,session,flash,jsonify 
from livereload import Server
from flask_sqlalchemy import SQLAlchemy
from models import db,Client,User,Workout
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime


app = Flask(__name__)
app.secret_key="secretkey"

#database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trainerapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)

with app.app_context():
    db.create_all()

#add to database

@app.route("/add_client", methods=["POST"])
def add_client():
    name=request.form["name"]
    email=request.form["email"]
    birthYear=request.form.get("birthYear")
    weight=request.form.get("weight")
    height=request.form.get("height")
    notes=request.form.get("notes")

    new_client=Client(
        name=name,
        email=email,
        birthYear=birthYear,
        weight=weight,
        height=height,
        notes=notes
    )

    db.session.add(new_client)
    db.session.commit()

    return redirect(url_for("clients"))



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        remember="remember" in request.form

        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            session["user_id"]=user.id
            session["role"]=user.role
            session["username"]=user.username
            session.permanent=remember

            flash("Login successful!","success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password","danger")
            return redirect(url_for("login"))


    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        role=request.form["role"]

        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.","danger")
            return redirect(url_for("register"))
        
        hashed_password=generate_password_hash(password)
        new_user=User(username=username,email=email,password=hashed_password,role=role)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Check your email for confirmation!","success")
        return redirect(url_for("login"))


    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if session["role"]=="trainer":
        return redirect(url_for("trainer_dashboard"))
    elif session["role"]=="client":
        return redirect(url_for("client_dashboard"))
    else:
        return "Unknown role",403
    
@app.route("/edit_workout/<int:workout_id>",methods=["POST"])
def edit_workout(workout_id):
    if "user_id" not in session or session["role"]!="trainer":
        return jsonify({"error": "Only trainers can edit workouts"}), 403
    data=request.get_json()
    workout=Workout.query.get_or_404(workout_id)
    workout.title=data["title"]
    workout.description = data.get("description", "")
    workout.start = datetime.fromisoformat(data["start"])
    workout.end = datetime.fromisoformat(data["end"])
    workout.date = datetime.fromisoformat(data["date"]).date()
    workout.client_id = int(data["client_id"]) if data.get("client_id") else None
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/delete_workout/<int:workout_id>", methods=["POST"])
def delete_workout(workout_id):
    if "user_id" not in session or session["role"] != "trainer":
        return jsonify({"error": "Only trainers can delete workouts"}), 403
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/trainer")
def trainer_dashboard():
    # dummy user for testing
    user = {"username": "Trainer1"}
    return render_template("trainer_dashboard.html", user=user)

@app.route("/client")
def client_dashboard():
    # dummy user for testing
    user = {"username": "Client1"}
    return render_template("client_dashboard.html", user=user)

@app.route("/clients")
def clients():
    all_clients=Client.query.all()  
    if request.args.get("json")=="1":
        return jsonify([{"id":c.id,"name":c.name} for c in all_clients])
    return render_template("clients.html", clients=all_clients)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.","info")
    return redirect(url_for("login"))

@app.route("/create_test_users")
def create_test_users():
    from werkzeug.security import generate_password_hash
    trainer = User(username="Trainer1", email="trainer@example.com", password=generate_password_hash("trainer123"), role="trainer")
    client = User(username="Client1", email="client@example.com", password=generate_password_hash("client123"), role="client")
    db.session.add(trainer)
    db.session.add(client)
    db.session.commit()
    return "Test users created!"

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/get_workouts")
def get_workouts():
    workouts=Workout.query.all()
    events=[
        {
            "id":w.id,
            "title":w.title,
            "start":w.start.isoformat(),
            "end":w.end.isoformat(),
            "description":w.description,
            "client_id":w.client_id
        }
        for w in workouts
    ]
    return jsonify(events)

@app.route("/add_workout",methods=["POST"])
def add_workout():
    if "user_id" not in session or session["role"]!="trainer":
        return jsonify({"error":"Only trainers can add workouts"}), 403

    data=request.get_json()
    new_workout=Workout(
        title=data["title"],
        description=data.get("description", ""),
        start=datetime.fromisoformat(data["start"]),
        end=datetime.fromisoformat(data["end"]),
        date=datetime.fromisoformat(data["date"]).date(),
        trainer_id=session["user_id"],
        client_id=int(data["client_id"]) if data.get("client_id") else None
    )

    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"status":"success","id":new_workout.id})


if __name__ == "__main__":
    server=Server(app.wsgi_app)
    server.serve(debug=True)
    #app.run(debug=True)
