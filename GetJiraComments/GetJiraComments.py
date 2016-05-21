# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
import re
import time
import random
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from jira import JIRA
from slackclient import SlackClient

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
issues = jira.search_issues('assignee = sergey.zhurbenko AND updated >= startOfDay(-1d) ORDER BY updated ASC')
#print issues
# Get an issue.
for issueid in issues:
    issue = jira.issue(issueid.id)
    print issue.key                            # 'JRA'
    print issue.fields.issuetype.name          # 'New Feature'
    print issue.fields.reporter.displayName    # 'Mike Cannon-Brookes [Atlassian]'
    #all_comments=issue.fields.comment.comments

    # Find all comments made by solomoto on this issue.
    solo_comments = [comment for comment in issue.fields.comment.comments
                if re.search(r'sergey.zhurbenko@solomoto.com$', comment.author.emailAddress)]

    worklogs = jira.worklogs(issue.key)

    for comment in solo_comments:
        commenttext = jira.comment(issueid.id, comment)
        print commenttext.body
        pass

    for worklog in worklogs:
        text = jira.worklog(issueid.id, worklog)
        rawtext = text.comment
        print rawtext
        pass
    pass
#comment = jira.comment('SOLO-764', '16535')
#print comment.body
# Add a comment to the issue.
#jira.add_comment(issue, 'Comment text')