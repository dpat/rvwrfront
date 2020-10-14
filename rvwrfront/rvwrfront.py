from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
import requests, json, flask, sys, os
from dateutil.parser import parse

app = Flask(__name__, static_folder='/var/www/rvwrfront/rvwrfront/rvwrfront/static', static_url_path='/var/www/rvwrfront/rvwrfront/rvwrfront/static')
app.secret_key = 'testing this out'

def return_app():
    return app

def api_request(payload):

    baseurl = str(app.config.get('baseurl'))
    url = (baseurl + '/api')
    headers = {'content-type': 'application/json', 'token':app.config.get('token')}
    payload = payload
    response = requests.post(url, data=payload, headers=headers)
    return json.loads(response.text)


def add_review(product,score,review):
    return api_request(('review {1} {2} {3}'.format(product,score,review)))

def get_blog(id):
    return api_request(('blog -get=' + str(id)))


def get_personal(id):
    return api_request(('personal -get=' + str(id)))


def get_random(id):
    return api_request(('random -get=' + str(id)))


def get_reviews():
    return api_request('reviews -get=all')


@app.route('/sms', methods=['POST'])
def sms_handler():

    baseurl = str(app.config.get('baseurl'))
    url = (baseurl + '/sms')
    response = requests.post(url, request)

    resp = MessagingResponse()
    num = str(request.form['From'])
    resp.message(response)
    return str(resp)


@app.route('/login', methods=['post', 'get'])
def login():

    if request.method == 'POST':

        password = str(request.form.get('password'))

        if password == str(app.config.get('password')):
            session['owner'] = 'valid'
            return redirect(url_for('home'))
        else:
            return render_template('login.html', failed=True)
    else:
        return render_template('login.html')


@app.route('/logout', methods=['get'])
def logout():
    if 'owner' in session:
        session.pop('owner', None)

    return redirect(url_for('home'))


@app.route('/', methods=['get'])
def home():
    if request.method == 'POST':

        product = str(request.form.get('product'))
        score = str(request.form.get('score'))
        review = str(request.form.get('review'))

        add_review(product,score,review)
        return redirect(url_for('reviews'))


    else:
        reviews = get_reviews('all')
        return render_template('reviews.html', reviews=reviews)

@app.route('/blog', methods=['get'])
def blog():

    blog = get_blog('all')
    for item in blog:
        item['date'] = parse(item['date']).strftime('%B %d, %Y')
    return render_template('blog.html', blog=blog)

@app.route('/blog/category/<category>', methods=['get'])
def blog_category(category):

    blog = get_blog('all')
    for item in blog:
        item['date'] = parse(item['date']).strftime('%B %d, %Y')
    return render_template('blog.html', blog=blog, category=category)

@app.route('/blog/<id>', methods=['get'])
def blog_id(id):

    blog = [get_blog(id)]
    for item in blog:
        item['date'] = parse(item['date']).strftime('%B %d, %Y')
    return render_template('blog.html', blog=blog, id=id)

@app.route('/personal', methods=['get'])
def personal():

    if 'owner' not in session:
        return redirect(url_for('login'))

    personal = get_personal('all')

    return render_template('personal.html', personal=personal)

@app.route('/personal/category/<category>', methods=['get'])
def personal_category(category):

    if 'owner' not in session:
        return redirect(url_for('login'))

    personal = get_personal('all')

    return render_template('personal.html', personal=personal, category=category)


@app.route('/signup/<id>', methods=['post', 'get'])
def signup_id(id):
    if request.method == 'POST':

        number = str(request.form.get('phoneNumber'))
        add_number(number,id,'false')
        #if number is valid:
        if True:
            return redirect(url_for('home'))
        else:
            return render_template('login.html', failed=True)
    else:
        return render_template('signup.html', id=id)

@app.route('/personal/<id>', methods=['get'])
def personal_id(id):

    if 'owner' not in session:
        return redirect(url_for('login'))

    personal = [get_personal(id)]

    return render_template('personal.html', personal=personal, id=id)

@app.route('/random', methods=['get'])
def random():

    if 'owner' not in session:
        return redirect(url_for('login'))

    random = get_random('all')

    return render_template('random.html', random=random)

@app.route('/random/category/<category>', methods=['get'])
def random_category(category):

    if 'owner' not in session:
        return redirect(url_for('login'))

    random = get_random('all')

    return render_template('random.html', random=random, category=category)

@app.route('/random/<id>', methods=['get'])
def random_id(id):

    if 'owner' not in session:
        return redirect(url_for('login'))

    random = [get_random(id)]

    return render_template('random.html', random=random, id=id)

@app.route('/reviews', methods=['get'])
def reviews():

    if 'owner' not in session:
        return redirect(url_for('login'))

    reviews = get_reviews()

    return render_template('reviews.html', reviews=reviews)

@app.route('/about', methods=['get'])
def about():

    return render_template('about.html')

@app.route('/contact', methods=['get'])
def contact():

    return render_template('contact.html', phone=app.config.get('num'),
                           linkedin=app.config.get('linkedin'),
                           git=app.config.get('git'),
                           email=app.config.get('email'))

if __name__=='__main__':
    app.config['baseurl'] = ''
    app.config['token'] = ''
    app.config['password'] = ''
    app.config['linkedin'] = '?'
    app.config['git'] = '?'
    app.config['email'] = '?'
    app.config['phone'] = '?'
    app.run()
