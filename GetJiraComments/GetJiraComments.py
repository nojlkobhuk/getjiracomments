# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
import re
import time
import random
import unicodedata
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from jira import JIRA
from slackclient import SlackClient

def jiraReport(USER):
    # By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK
    # (see https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details).
    # Override this with the options parameter.
    jira_options = {
        'server': 'https://solomoto.atlassian.net'}
    jira = JIRA(options=jira_options, basic_auth=('sergey.zhurbenko', 'Asdqzec2012!?'))

    # Get all projects viewable by anonymous users.
    projects = jira.projects()

    # Sort available project keys, then return the second, third, and fourth keys.
    keys = sorted([project.key for project in projects])[2:5]
    search = 'assignee = %s AND updated >= startOfDay(-1d) ORDER BY updated ASC' % USER
    issues = jira.search_issues(search)
    #print issues
    # Get an issue.
    comtext2 = ""
    for issueid in issues:
        issue = jira.issue(issueid.id)
        print issue.key                            # 'JRA'
        print issue.fields.summary                 # 'JRA'
        print issue.fields.issuetype.name          # 'New Feature'
        print issue.fields.reporter.displayName    # 'Mike Cannon-Brookes [Atlassian]'
        #all_comments=issue.fields.comment.comments

        # Find all comments made by solomoto on this issue.
        solo_comments = [comment for comment in issue.fields.comment.comments
                    if re.search(USER, comment.author.emailAddress)]

        worklogs = jira.worklogs(issue.key)
        comtext = "My comments:"
        for comment in solo_comments:
            commenttext = jira.comment(issueid.id, comment)
            #comtext = unicodedata.normalize('NFKD', commenttext.body).encode('ascii','ignore')
            comtext = "\r\n".join(["%s","%s"]) % (comtext,commenttext.body)            
            #alltext=+comtext
            pass
        worktext = "My worklog:"
        for worklog in worklogs:
            worklogtext = jira.worklog(issueid.id, worklog)
            #print worklogtext.comment
            worktext = "\r\n".join(["%s","%s"]) % (worktext,worklogtext.comment)
            #alltext=+rawtext
            pass
        comtext2 = "\r\n".join(["%s","%s %s","[%s]","%s","%s","\r\n"]) % (comtext2,issue.key,issue.fields.summary,issue.fields.issuetype.name,comtext,worktext)
        pass
        
    return comtext2

def sendMail(FROM,TO,SUBJECT,TEXT,SERVER):
    import smtplib
    # Send the mail
    msg = "\r\n".join([
      "From: %s",
      "To: %s",
      "Subject: %s",
      "",
      "%s"
      ]) % (FROM, TO, SUBJECT, TEXT)

    server = smtplib.SMTP(SERVER)
    server.ehlo()
    server.starttls()
    server.login('sergey.zhurbenko@solomoto.com', 'Asdqzec2012!?')
    server.sendmail(FROM, TO, msg)
    server.quit()

report = jiraReport('sergey.zhurbenko')
sendMail ('sergey.zhurbenko@solomoto.com','sergey.zhurbenko@solomoto.com','Daily Report',report,'smtp.gmail.com:587')

token = "xoxb-44694863140-7J4o134qrs8C9DQpRDq7q8Zx"      # found at https://api.slack.com/web#authentication
client = SlackClient(token)
print client.api_call("api.test")
#print sc.api_call("channels.info", channel="#datadog")
print client.api_call(
    "chat.postMessage", channel="#dailyreports", text="I am here!",
    username='dailyreporter', icon_emoji=':hankey:'
)
if client.rtm_connect():
    while True:
        last_read = client.rtm_read()
        if last_read:
            try:
                parsed = last_read[0]['text']
                #reply to channel message was found in.
                message_channel = last_read[0]['channel']
                userid = last_read[0]['user']                
                if parsed and 'food' in parsed:
                    userinfo = client.api_call('users.info', user=userid)
                    email = userinfo['user']['profile']['email']
                    choice = random.choice(['hamburger', 'pizza'])
                    client.rtm_send_message(message_channel,'%s sent to %s.' % (choice,email))
            except:
                pass
        time.sleep(1)