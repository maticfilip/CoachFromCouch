from flask import Flask, render_template,request,url_for,redirect,session,flash
from livereload import Server
from flask_sqlalchemy import SQLAlchemy
from models import db,Client,User
from werkzeug.security import check_password_hash,generate_password_hash


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
            #store session
            session["user_id"]=user.id
            session["role"]=user.role
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

if __name__ == "__main__":
    server=Server(app.wsgi_app)
    server.serve(debug=True)
    #app.run(debug=True)
