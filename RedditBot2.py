    #!/usr/bin/env python3
    # coding: utf-8

import mysql.connector
import datetime
today = datetime.date.today()
weekday = today.weekday()

if (weekday == 5 ):
    from itsdangerous import URLSafeTimedSerializer
    #from flask import url_for
    import smtplib
    import json
    import praw


    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText


    with open('googlecredentials.json') as f:
        google = json.load(f)


    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(google['username'], google['password'])


    url = 'https://www.reddit.com/'
    with open('redditcredentials.json') as f:
        params = json.load(f)

    reddit = praw.Reddit(client_id=params['client_id'],
                         client_secret=params['api_key'],
                         password=params['password'],
                         user_agent='DataScienceWeelyUA accessAPI:v0.0.1 (by /u/DataScienceWeekly)',
                         username=params['username'])
    subreddit = reddit.subreddit('datascience')

    for submission in subreddit.hot(limit=10):
        if 'Weekly' in submission.title and submission.stickied == True:
            subject = submission.title
            submissionurl = submission.url
            weekly = reddit.submission(id=submission.id)



    text = subject + '\n' + submissionurl + '\n \n'
    body = '<a href="' + submissionurl + '" style="text-decoration: none; color: #0079d3; font-size: 16px; font-weight: bold;">' + subject + '</a>'
    for top_level_comment in weekly.comments:
        text = text + 'Posted by ' + str(top_level_comment.author) + '\n' + 'https://www.reddit.com' + str(top_level_comment.permalink) + '\n' + str(top_level_comment.body) + '\n'
        text = text + str(top_level_comment.replies.__len__()) + ' replies \n\n '

        body = body + '<a href="https://www.reddit.com' + str(top_level_comment.permalink)+ '" style="text-decoration: none; color: #999999;"> <p style="font-size: 13px;">Posted by u/' + str(top_level_comment.author) + '</p><p style="font-size:14px; color: #999999;">' + str(top_level_comment.body)[0:250] + '... <span style="color:#0079da;">Read more</span></p>'
        body = body + '<img src="https://ci6.googleusercontent.com/proxy/_Iz274dqmoYeJb2xWRUltaqdfdSRzqcabI-0ISnqiRQK_t_WpQhZHSoL0xslGSj4AD0ZQXfhpKE_lKfZ73F22q4Z8Y_zCU84OzsR-1IA=s0-d-e1-ft#https://www.redditstatic.com/emaildigest/reddit_comment.png" width="13" alt="" style="display:inline;border:0;padding-right:4px;">' + str(top_level_comment.replies.__len__()) + ' replies</a> <br><br><hr width="50%" style="border-top: 1px solid #e4e4e4;"> '

    with open('secretkey.json') as f:
        secretkey = json.load(f)
    s = URLSafeTimedSerializer(secretkey['key'])

    with open('sqlcreds.json') as f:
        sqlcreds = json.load(f)

    mydb = mysql.connector.connect(
    host=sqlcreds['host'],
    user=sqlcreds['user'],
    password=sqlcreds['password'],
    database=sqlcreds['database']
    )
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM subscriberList")

    myresult = mycursor.fetchall()

    for x in myresult:
      # me == my email address
      # you == recipient's email address
      me = google['username']
      you = x[0]
      token = s.dumps(you, salt=secretkey['email-unsubscribe'])
      #link = url_for('unsubscribe', token=token, _external=True)
      unsubscribeLink = ''
      unsubscribeLink = '<a href="http://datascienceweekly.pythonanywhere.com/unsubscribe/{}">Unsubscribe</a>'.format(token)

      # Create message container - the correct MIME type is multipart/alternative.
      msg = MIMEMultipart('alternative')
      msg['Subject'] = subject
      msg['From'] = me
      msg['To'] = you


      # Create the body of the message (a plain-text and an HTML version).
      #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"
      html = """<html>
        <head></head>
        <body style="color: #888888;">
          {}
          {}
        </body>
      </html>
      """.format(body, unsubscribeLink)


      # Record the MIME types of both parts - text/plain and text/html.
      part1 = MIMEText(text, 'plain')
      part2 = MIMEText(html, 'html')

      # Attach parts into message container.
      # According to RFC 2046, the last part of a multipart message, in this case
      # the HTML message, is best and preferred.
      msg.attach(part1)
      msg.attach(part2)


      # sendmail function takes 3 arguments: sender's address, recipient's address
      # and message to send - here it is sent as one string.
      smtpObj.sendmail(me, you, msg.as_string())
    smtpObj.quit()
    mycursor.close()
    mydb.close()