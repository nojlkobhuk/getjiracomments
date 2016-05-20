# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
import re
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from jira import JIRA


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

# Get an issue.
issue = jira.issue('SOLO-764')
print issue.fields.project.key             # 'JRA'
print issue.fields.issuetype.name          # 'New Feature'
print issue.fields.reporter.displayName    # 'Mike Cannon-Brookes [Atlassian]'
all_comments=issue.fields.comment.comments

# Find all comments made by solomoto on this issue.
solo_comments = [comment for comment in issue.fields.comment.comments
                if re.search(r'@solomoto.com$', comment.author.emailAddress)]

worklogs = jira.worklogs(issue.key)

for comment in solo_comments:
    commenttext = jira.comment('SOLO-764', comment)
    print commenttext.body
    pass

for worklog in worklogs:
    text = jira.worklog('SOLO-764', worklog)
    rawtext = text.comment
    print rawtext
    pass
#comment = jira.comment('SOLO-764', '16535')
#print comment.body
# Add a comment to the issue.
#jira.add_comment(issue, 'Comment text')