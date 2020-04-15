# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
import re
import time
import random
import unicodedata
import datetime
import time
import textwrap
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from jira import JIRA
from slackclient import SlackClient

def jiraReport(USER,report_date):
    # By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK
    # (see https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details).
    # Override this with the options parameter.
    jira_options = {
        'server': 'https://solomoto.atlassian.net'}
    jira = JIRA(options=jira_options, basic_auth=('sergey.zhurbenko', 'zxzxzx'))

    # Get all projects viewable by anonymous users.
    projects = jira.projects()

    # Sort available project keys, then return the second, third, and fourth keys.
    #keys = sorted([project.key for project in projects])[2:5]
    if report_date == 'today':
        now = datetime.datetime.now() - datetime.timedelta(hours=12)
        nextday = datetime.datetime.now() + datetime.timedelta(hours=12)
        search = 'worklogAuthor = %s AND worklogDate = "%s/%s/%s" ORDER BY updated ASC' % (USER,now.year,now.month,now.day)
    else:
        now = datetime.datetime.strptime(report_date,"%d.%m.%Y")
        nextday = datetime.datetime(now.year,now.month,now.day + 1)
        search = 'worklogAuthor = %s AND worklogDate = "%s/%s/%s" ORDER BY updated ASC' % (USER,now.year,now.month,now.day)
    issues = jira.search_issues(search)
    #print issues
    # Get an issue.
    result = ""
    for issueid in issues:
        issue = jira.issue(issueid.id)
        print issue.key                            # 'JRA'
        print issue.fields.summary                 # 'My very serious task'
        print issue.fields.issuetype.name          # 'New Feature'
        print issue.fields.reporter.displayName    # 'Mike Cannon-Brookes [Atlassian]'
        #all_comments=issue.fields.comment.comments

        # Find all comments made by solomoto on this issue.
        solo_comments = [comment for comment in issue.fields.comment.comments
                    if re.search(USER, comment.author.name)]

        worklogs = jira.worklogs(issue.key)
        comtext = ""
        for comment in solo_comments:
            if comment.author.name == USER:
                commenttime = time.strptime(comment.created[:19], "%Y-%m-%dT%H:%M:%S")
                commenttime = datetime.datetime(commenttime[0], commenttime[1], commenttime[2], commenttime[3], commenttime[4])
                if commenttime >= now and commenttime < nextday:
                    comtext = "\r\n".join(["%s","\tcomments: \r\n\t%s"]) % (comtext,comment.body)            
            pass
        worktext = ""
        for worklog in worklogs:
            if worklog.author.name == USER:
                worklogtime = time.strptime(worklog.created[:19], "%Y-%m-%dT%H:%M:%S")
                worklogtime = datetime.datetime(worklogtime[0], worklogtime[1], worklogtime[2], worklogtime[3], worklogtime[4])
                if worklogtime >= now and worklogtime < nextday:
                    worktext = "\r\n".join(["%s","\tworklog: %s\r\n\t%s"]) % (worktext,worklog.timeSpent,worklog.comment)
            pass
        if worktext > "" or comtext > "":
            result = "\r\n".join(["%s","[%s] %s %s:","\t%s","\t%s","\r\n"]) % (result,issue.fields.issuetype.name,issue.key,issue.fields.summary,worktext,comtext)
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
    server.login('admin@solomoto.com', 'zxxxzxzx')
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
                if parsed and ('report' in parsed or parsed == 'dr' or parsed == 'dr to all'):
                    userinfo = client.api_call('users.info', user=userid)
                    email = userinfo['user']['profile']['email']
                    fullname = userinfo['user']['real_name']
                    choice = random.choice(['Your epic report', 'Hernya', 'Magic', 'Black mamba', 'Great report', 'Productivity'])
                    verbs = random.choice(['sent', 'happened', 'realized', ':hankey:'])
                    username = email[:-13]                  
                    if 'today' in parsed or parsed == 'dr' or parsed == 'dr to all':
                        report = jiraReport(username,'today')
                        now = datetime.datetime.now()
                        subject = '%s daily report for %s.%s.%s' % (fullname,now.day,now.month,now.year)
                    else:
                        match = re.search(r'(\d+.\d+.\d+)',parsed)
                        date = match.group(1).encode('ascii')  
                        report = jiraReport(username,date)
                        subject = '%s daily report for %s' % (fullname,date)
                    if 'message' in parsed:
                        report = report + "\r\nAdditional message:\r\n\t" + parsed[parsed.find("message")+8:]
                    if 'to all' in parsed:
                        email = 'ru_dev_team@solomoto.com'
                    sendMail ('admin@solomoto.com',email,subject,'Activities:\r\n' + report,'smtp.gmail.com:587')
                    client.rtm_send_message(message_channel,'%s %s to %s.' % (choice,verbs,email))
            except:
                pass
        time.sleep(1)
