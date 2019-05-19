import jira, base64, bs4
from confluence.client import Confluence as cnfl


# protocol and baseurl
proto = 'https://'
baseurl = 'isostech.com'

# get credentials from files
with open('/Users/sky/Dev/rest_blog/resource1', mode='br') as file_object:
    password = base64.b64decode(file_object.read()).decode()

with open('/Users/sky/Dev/rest_blog/resource2', mode='r') as file_object:
    username = file_object.read()

# create jira object and authenticate to server
jira_auth = jira.JIRA(f'{proto}issues.{baseurl}', auth=(username, password))

# create confluence object and authenticate to server
cnfl_auth = cnfl(f'{proto}wiki.{baseurl}', (username, password))

# download the page with our blog teams table on it
blog_teams = cnfl_auth.get_content(space_key='BS', title='2019 Spring Blog Draft')
for page in blog_teams:
    page_content = cnfl_auth.get_content_by_id(page.id, expand=['body.view'])

# parse the content of the page
parsed_page = bs4.BeautifulSoup(page_content.body.view,'html.parser')
teamsHeader = parsed_page.find_all('h1')[1]
teamsTable = teamsHeader.next_sibling.contents[0].contents[1].contents

# build the team lists
teams = {0: [], 1: [], 2: []}

for row in teamsTable:
    for i, td in enumerate(row.contents):
        try:
            teams[i].append(td.contents[0].attrs['data-username'])
        except KeyError:
            try:
                teams[i].append(td.contents[0].contents[0].contents[0].attrs['data-username'])
            except IndexError:
                break

# name the teams
namedTeams = {'Mary': teams[0],
              'Amanda': teams[1],
              'Bob': teams[2]}

# get the issues in BLOG project by team
for team in namedTeams:
    # search for issues in jira using jql
    teamIssues = jira_auth.search_issues(jql_str=f'project = BLOG AND resolution = Unresolved AND \
                                        assignee in ({",".join(namedTeams[team])})',json_result=True)
    # generate output
    print('\n\nTeam',team,'has',len(teamIssues['issues']),'open blog issues:\n')
    for issue in teamIssues['issues']:
        print(issue['key'], ':\t', issue['fields']['assignee']['displayName'],'\n\t',issue['fields']['summary'])