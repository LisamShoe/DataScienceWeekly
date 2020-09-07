This is a weekly newsletter bot that takes the Weekly Entering & Transitioning thread from https://www.reddit.com/r/datascience/ and emails it to a list of subscribers on Saturday.

This reddit bot runs on Python Anywhere using a mySQL database to handle the subscriber list, a flask site to handle the subscribe and unsubscribe functions, and json files to hold the login credentials needed.
The emails are gnerated through Google, which has a limited number of emails per day (500). If the list is too large, another email provider will need to be used.

The json files are not included in this git repository, but are located in the main directory and named:
googlecredentials.json
redditcredentials.json
secretkey.json
sqlcreds.json# DataScienceWeekly
