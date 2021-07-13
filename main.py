from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import request
import json
from datetime import datetime
from flask import session
import math

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class Contacts(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    postby = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=False)


@app.route("/")
@app.route("/home")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('home.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/quarantine")
def quarantine():
    return render_template('quarantine.html',title='Quarantine Rules')


@app.route("/child")
def childcare():
    return render_template('child.html',title='ChildrenCare')


@app.route("/health")
def healthwealth():
    return render_template('health.html',title='Health & Wealth tips')

@app.route("/outbreak")
def outbreak():
    return render_template('outbreak.html',title='Covid-19 Status')


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if "user" in session and session['user']==params['admin_user']:
        posts = Posts.query.all()
        return render_template("dashboard.html", params=params, posts=posts)

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if username==params['admin_user'] and userpass==params['admin_password']:
            # set the session variable
            session['user']=username
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)

    return render_template("login.html", params=params)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')



@app.route("/post/<string:post_slug>/", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_number = phone, message = message,email = email )
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html')




@app.route("/edit/<string:srno>" , methods=['GET', 'POST'])
def edit(srno):
    if "user" in session and session['user']==params['admin_user']:
        if request.method == "POST":
            slug = request.form.get('slug')
            title = request.form.get('title')
            postby = request.form.get('postby')
            content = request.form.get('content')
            date = datetime.now()
        
            if srno=='0':
                post = Posts(slug=slug, title=title, content=content,postby=postby, date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(srno=srno).first()
                post.title = title
                post.slug = slug
                post.content = content
                post.postby = postby
                post.date = date
                db.session.commit()
                return redirect('/edit/'+srno)
             
    post = Posts.query.filter_by(srno=srno).first()   
    return render_template('edit.html', params=params, srno=srno, post=post)

@app.route("/delete/<string:srno>" , methods=['GET', 'POST'])
def delete(srno):
    if "user" in session and session['user']==params['admin_user']:
        post = Posts.query.filter_by(srno=srno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")

    


app.run(debug=True)