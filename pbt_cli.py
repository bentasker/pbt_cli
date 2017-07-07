#!/usr/bin/env python

import urllib2
import json
import re
import time



BASEDIR="https://projects.bentasker.co.uk/jira_projects"


PROJURLS={}


def getJSON(url):
    print "Fetching %s" % (url,)
    response = urllib2.urlopen(url)
    jsonstr = response.read()
    #print jsonstr
    return json.loads(jsonstr)


# See https://snippets.bentasker.co.uk/page-1705192300-Make-ASCII-Table-Python.html
def make_table(columns, data):
    """Create an ASCII table and return it as a string.

    Pass a list of strings to use as columns in the table and a list of
    dicts. The strings in 'columns' will be used as the keys to the dicts in
    'data.'

    """
    # Calculate how wide each cell needs to be
    cell_widths = {}
    for c in columns:
        lens = []
        values = [lens.append(len(str(d.get(c, "")))) for d in data]
        lens.append(len(c))
        lens.sort()
        cell_widths[c] = max(lens)

    # Used for formatting rows of data
    row_template = "|" + " {} |" * len(columns)

    # CONSTRUCT THE TABLE

    # The top row with the column titles
    justified_column_heads = [c.ljust(cell_widths[c]) for c in columns]
    header = row_template.format(*justified_column_heads)
    # The second row contains separators
    sep = "|" + "-" * (len(header) - 2) + "|"
    end = "-" * len(header)
    # Rows of data
    rows = []

    for d in data:
        fields = [str(d.get(c, "")).ljust(cell_widths[c]) for c in columns]
        row = row_template.format(*fields)
        rows.append(row)
    rows.append(end)
    return "\n".join([header, sep] + rows)



def listprojects():
    """ List the projects available
    """
    
    plist = getJSON("%s/manifest.json" % (BASEDIR,))
    
    print """Projects:
            
            """
    
    
    if "items" not in plist:
        print "No projects returned"
        return False
    
    Cols=['Key','Name']
    rows=[]
    for project in plist["items"]:
        entry = {
            'Key' : project['Key'],
            'Name' : project['Name'],
            'Description' : project['Description']
            }
        rows.append(entry)
        if project['Key'] not in PROJURLS:
            PROJURLS[project['Key']] = project['href']
    
    print make_table(Cols,rows)
    


def stripTags(str):
    ''' Strip out HTML tags and return just the plain text
    '''
    return re.sub('<[^<]+?>', '', str)


def buildIssueTable(issues,isstype=False,issstatus=False):
    ''' Print a table of issues
    
        Args:
        
            isstype - False to disable filter. Otherwise list containing issuetypes to display
            issstatus - False to disable filter. Otherwise list containing issuetypes to display
    
    
    '''
    Cols = ['Key','Type','Priority','Summary','Status','Resolution','Created','Assigned To']
    rows = []
    
    if isstype or issstatus:
        print "Filtering by Issue type = %s and Status = %s\n\n" % (isstype,issstatus)
        
        
    for issue in issues:
        
        # Check whether we're filtering by issue type
        if isstype and issue['IssueType'] not in isstype:
            continue
        
        if issstatus and issue['Status'] not in issstatus:
            continue
        
        entry = {
            'Key' : issue['Key'],
            'Type' : issue['IssueType'],
            'Priority' : issue['Priority'],
            'Summary' : issue['Name'],
            'Status' : issue['Status'],
            'Resolution' : issue['Resolution'],
            'Created' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(issue['Created'])),
            'Assigned To' : issue['assigneee']
        }
        rows.append(entry)
    
    return make_table(Cols,rows)
    



def listProject(proj,isstype=False,issstatus=False):
    """ Print details about the specified project
    """

    if proj not in PROJURLS:
        url = "%s/browse/%s.json" % (BASEDIR,proj)
    else:
        url = PROJURLS[proj]

    plist = getJSON(url)

    print "%s: %s\n\n%s\n\n" % (plist['Key'],plist['Name'],stripTags(plist['Description']))
    
    print buildIssueTable(plist['issues'],isstype,issstatus)





#listprojects()
listProject('BTFW',isstype=['Task'],issstatus=['Open'])