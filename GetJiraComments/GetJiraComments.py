# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
import re
import time
import random
import unicodedata
from datetime import datetime
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
    result = ""
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
        comtext = "comments:"
        for comment in solo_comments:
            commenttext = jira.comment(issueid.id, comment)
            #comtext = unicodedata.normalize('NFKD', commenttext.body).encode('ascii','ignore')
            comtext = "\r\n".join(["%s","\t%s"]) % (comtext,commenttext.body)            
            pass
        worktext = ""
        for worklog in worklogs:
            worklogtext = jira.worklog(issueid.id, worklog)
            #print worklogtext.comment
            worktext = "\r\n".join(["%s","\tworklog: %s\r\n\t%s"]) % (worktext,worklogtext.timeSpent,worklogtext.comment)
            pass
        result = "\r\n".join(["%s","[%s] %s %s:","\t%s","\t%s","\r\n"]) % (result,issue.fields.issuetype.name,issue.key,issue.fields.summary,comtext,worktext)
        pass
        
    return result

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

token = "xoxb-44694863140-kyMCRyVHrlqOdbQguUgDxawc"      # found at https://api.slack.com/web#authentication
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
                    fullname = userinfo['user']['real_name']
                    choice = random.choice(['Your epic report', 'Hernya', 'Magic', 'Black mamba', 'Great report', 'Productivity'])
                    verbs = random.choice(['sent', 'happened', 'realized', ':hankey:'])
                    username = email[:-13]                    
                    report = jiraReport(username)
                    now = datetime.now()
                    subject = '%s daily report for %s.%s.%s' % (fullname,now.day,now.month,now.year)
                    sendMail ('sergey.zhurbenko@solomoto.com',email,subject,'Activities:\r\n' + report,'smtp.gmail.com:587')
                    client.rtm_send_message(message_channel,'%s %s to %s.' % (choice,verbs,email))
            except:
                pass
        time.sleep(1)