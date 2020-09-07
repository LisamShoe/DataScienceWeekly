from flask import Flask, request, url_for
#from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import mysql.connector
import smtplib
import json
import os.path

app = Flask(__name__)

with open(os.path.dirname(__file__) + '/../secretkey.json') as f:
    secretkey = json.load(f)
s = URLSafeTimedSerializer(secretkey['key'])

#with open(os.path.dirname(__file__) + '/../sqlcreds.json') as f:
#    sqlcreds = json.load(f)

#mydb = mysql.connector.connect(
#host=sqlcreds['host'],
#user=sqlcreds['user'],
#password=sqlcreds['password'],
#database=sqlcreds['database']
#)

#mycursor = mydb.cursor()


@app.route('/', methods=['GET', 'POST'])
def index():
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    with open(os.path.dirname(__file__) + '/../googlecredentials.json') as f:
        google = json.load(f)


    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(google['username'], google['password'])

    if request.method == 'GET':
        return'<form action="/" method="POST"><input name="email"><input type="submit"></form>'
    email = request.form['email']
    token = s.dumps(email, salt=secretkey['email-confirm'])

    link = url_for('confirm_email', token=token, _external=True)

    me = google['username']
    you = email
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Confirm Your Subscription to DataScienceWeekly'
    msg['From'] = me
    msg['To'] = you
    # Create the body of the message (a plain-text and an HTML version).
    text = "Thank you for subscribing to DataScienceWeekly. Please click this link to confirm: \n{}".format(link)
    html = "Thank you for subscribing to DataScienceWeekly. Please click this link to confirm: \n{}".format(link)
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    smtpObj.sendmail(me, you, msg.as_string())
    smtpObj.quit()

    return '<h1>The email you entered is {}. Please check your email for a confirmation. The token is {}. Link is {}</h1>'.format(email,token,link)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    with open(os.path.dirname(__file__) + '/../sqlcreds.json') as f:
        sqlcreds = json.load(f)

    mydb = mysql.connector.connect(
    host=sqlcreds['host'],
    user=sqlcreds['user'],
    password=sqlcreds['password'],
    database=sqlcreds['database']
    )

    mycursor = mydb.cursor()

    email = ''
    myresult = ''
    try:
        email = s.loads(token, salt=secretkey['email-confirm'], max_age=3600)
        mycursor.execute("SELECT COUNT(*) FROM subscriberList WHERE email = '{}'".format(email))
        myresult = mycursor.fetchall()[0][0]
    except:
        mydb.close()
        return 'Oh no! This link didn\'t work, please return to the home page to try again'
    if myresult > 0:
        mydb.close()
        return 'It looks like you were already signed up to receive our emails. If you are having trouble, check your spam folder or your email rules.'
    else:
        try:
            mycursor.execute("INSERT INTO subscriberList (email) VALUES ('{}');".format(email))
            mydb.commit()
            mydb.close()
            return 'Thanks for subscribing! You have been subscribed as {}'.format(email)
        except:
            mydb.close()
            return 'We experienced an error'

@app.route('/unsubscribe/<token>')
def unsubscribe(token):
    with open(os.path.dirname(__file__) + '/../sqlcreds.json') as f:
        sqlcreds = json.load(f)

    mydb = mysql.connector.connect(
    host=sqlcreds['host'],
    user=sqlcreds['user'],
    password=sqlcreds['password'],
    database=sqlcreds['database']
    )

    myresult = ''
    mycursor = mydb.cursor()
    try:
        email = s.loads(token, salt=secretkey['email-unsubscribe'])
        mycursor.execute("SELECT COUNT(*) FROM subscriberList WHERE email = '{}'".format(email))
        myresult = mycursor.fetchall()[0][0]
        #return myresult
    except:
        mydb.close()
        return 'There seems to be something wrong.'
    if myresult > 0:
        try:
            mycursor.execute("DELETE FROM subscriberList WHERE email = '{}' ;".format(email))
            mydb.commit()
            mydb.close()
            return 'We are sorry to see you go! {} has been unsubscribed'.format(email)
        except:
            mydb.close()
            return 'We experienced an error'
    else:
        mydb.close()
        return "You are no longer on our list"


if __name__ == '__main__':
    app.run(debug=True)