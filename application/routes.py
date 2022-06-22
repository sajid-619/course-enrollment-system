
from application import app, db, api
from flask import Response, jsonify, redirect, render_template, request, json, jsonify, flash, redirect, url_for, session
from application.course_list import course_list
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm
from flask_restx import Resource, Api
from application.course_list import course_list

#################################################

@api.route('/api','/api/')
class GetAndPost(Resource):
  #GET all users
  def get(self):
    return jsonify(User.objects.all())

  #POST 
  def post(self):
    data = request.get_json()
    user = User(user_id = data['user_id'],
                first_name = data['first_name'],
                last_name = data['last_name'],
                email = data['email']
                )
    user.set_password(data['password'])
    user.save()
    return jsonify(User.objects(user_id=data['user_id']))


@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
  #GET a user
  def get(self,idx):
    return jsonify(User.objects(user_id=idx))

  #PUT
  def put(self, idx):
    data = request.get_json()
    User.objects(user_id=idx).update(**data)
    return jsonify(User.objects(user_id=idx))

  #Delete
  def delete(self, idx):
    User.objects(user_id=idx).delete()
    return jsonify("User is deleted!")

#################################################

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
  return render_template("index.html", index=True)

@app.route("/login", methods=["GET", "POST"])
def login():
  if session.get('username'):
    return redirect(url_for('index'))

  form = LoginForm()
  if form.validate_on_submit():
    email = form.email.data
    password = form.password.data
    user = User.objects(email=email).first()
    if user and user.get_password(password):
      flash("You are successfully logged in!", "success")
      session['user_id'] = user.user_id
      session['username'] = user.first_name
      return redirect("/index")
    else:
      flash("Something might went wrong, please try again!", "danger")
  return render_template("login.html", title= 'Login', form=form, login=True)

@app.route("/logout")
def logout():
  session['user_id'] = False
  session.pop('username', None)
  return redirect(url_for('index'))

@app.route("/courses")
@app.route("/courses/<term>") 
def courses(term=None):
  if term is None:
    term = "Spring 2019"

  classes = Course.objects.order_by('courseID')
  return render_template("courses.html", courseData=classes, courses=True, term=term)

@app.route("/register", methods=["GET", "POST"])
def register():
  if session.get('username'):
    return redirect(url_for('index'))
  form = RegisterForm()
  if form.validate_on_submit():
    user_id = User.objects.count()
    user_id += 1

    email = form.email.data
    password = form.password.data
    first_name = form.first_name.data
    last_name = form.last_name.data

    user = User(user_id = user_id,
                first_name = first_name,
                last_name = last_name,
                email = email
                )
    user.set_password(password)
    user.save()
    flash("You're successfully registered!", "success")
    return redirect(url_for('index'))
    
  return render_template("register.html", title='Register', form=form, register=True)

@app.route("/enrollment", methods=["GET", "POST"])
def enrollment():  
  if not session.get('username'):
    return redirect(url_for('index'))

  courseID = request.form.get('courseID')
  courseTitle = request.form.get('title')
  user_id = session.get('user_id')
  if courseID:
    if Enrollment.objects(user_id=user_id, courseID=courseID):
      flash(f"Opps! You are already registered in this course {courseTitle}!","danger" )
      return redirect(url_for('courses'))
    else:
      Enrollment(user_id=user_id,courseID=courseID).save()
      flash(f"You registered to {courseTitle} successfully!", "success")
  classes = course_list()
  term = request.form.get('term')
  return render_template("enrollment.html", enrollment=True, title = "Enrollment", classes=classes)

@app.route("/api/") 
@app.route("/api/<idx>")
def api(idx=None):
  if(idx==None):
    jsonData = courseData
  else:
    jsonData = courseData[int(idx)]
  return Response(json.dumps(jsonData), mimetype="application/json")



  
@app.route("/user")
def user():
  # User(user_id = '1', first_name = 'Min', last_name = 'Lin', email = 'min-lin@hotmail.com', password = 'test123').save()
  # User(user_id = '2', first_name = 'Tom', last_name = 'Hank', email = 'th@hotmail.com', password = 'thtest123').save()
  users = User.objects.all()
  return render_template("user.html", users = users)

