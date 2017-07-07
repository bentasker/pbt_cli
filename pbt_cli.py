#!/usr/bin/env python

import urllib2
import json
import re
import time

import sys, readline, os,stat,requests



BASEDIR="https://projects.bentasker.co.uk/jira_projects"
AUTH=False
ADDITIONAL_HEADERS=False

# I use this settings file to gain access to the non-public copy of my projects
if os.path.isfile(os.path.expanduser("~/.pbtcli.settings")):
    print "Loading settings"
    with open(os.path.expanduser("~/.pbtcli.settings"),'r') as f:
        for x in f:
            x = x.rstrip()
            if not x:
                continue
            
            # The lines are keyvalue pairs
            cfgline = x.split("=")
            if cfgline[0] == "BASEDIR":
                BASEDIR=cfgline[1]
                
            if cfgline[0] == "AUTH":
                AUTH='='.join(cfgline[1:])

            if cfgline[0] == "ADD_HEADER":
                if not ADDITIONAL_HEADERS:
                    ADDITIONAL_HEADERS = []
                    
                h = {
                        'name' : cfgline[1],
                        'value' : '='.join(cfgline[2:]),
                    }
                ADDITIONAL_HEADERS.append(h)

PROJURLS={}
ISSUEURLS={}
PROJDATA={}

def getJSON(url):
    #print "Fetching %s" % (url,)
    
    request = urllib2.Request(url)
    
    if AUTH:
        request.add_header("Authorization","Basic %s" % (AUTH,))
    
    if ADDITIONAL_HEADERS:
        for header in ADDITIONAL_HEADERS:
            request.add_header(header['name'],header['value'])
    
    
    response = urllib2.urlopen(request)
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
        

    # Prevent case-sensitivity issues with filters
    if isstype:
        isstype = [e.lower() for e in isstype]

    if issstatus:
        issstatus = [e.lower() for e in issstatus]

        
    for issue in issues:
        
        # Check whether we're filtering by issue type
        if isstype and issue['IssueType'].lower() not in isstype:
            continue
        
        if issstatus and issue['Status'].lower() not in issstatus:
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
        
        if issue['Key'] not in ISSUEURLS:
            ISSUEURLS[issue['Key']] = issue['href']
        
    
    return make_table(Cols,rows)
    


def fetchProject(proj):
    ''' Fetch the JSON for a project, and return it
    '''
    if proj not in PROJURLS:
        url = "%s/browse/%s.json" % (BASEDIR,proj)
    else:
        url = PROJURLS[proj]

    plist = getJSON(url)
    
    
    # Do some cachey-cachey
    if proj not in PROJDATA:
        PROJDATA[proj] = {}
    
    
    # Cache version URLs. We can't trivially calculate these
    if len(plist['versions']) > 0 and "versions" not in PROJDATA[proj]:
        PROJDATA[proj]['versions'] = {}
        for ver in plist['versions']:
            PROJDATA[proj]['versions'][ver['Name']] = ver['href']
    
    # Cache component URLs. We can't trivially calculate those either
    if len(plist['components']) > 0 and "components" not in PROJDATA[proj]:
        PROJDATA[proj]['components'] = {}
        for comp in plist['components']:
            PROJDATA[proj]['components'][comp['Name']] = comp['href']
        
    
    
    
    return plist



def listProject(proj,isstype=False,issstatus=False):
    """ Print details about the specified project
    """

    plist = fetchProject(proj)
    
    print "%s: %s\n\n%s\n\n" % (plist['Key'],plist['Name'],stripTags(plist['Description']))
    
    print buildIssueTable(plist['issues'],isstype,issstatus)



def listProjectComponent(proj,comp,isstype=False,issstatus=False):
    ''' List issues for a specific project component
    
        Args:
        
        proj - the project key (E.g. GPXIN)
        comp - The component name (e.g. Experimental Features)
    
    
    '''
    
    if proj not in PROJDATA or "components" not in PROJDATA[proj] or comp not in PROJDATA[proj]["components"]:
        # We need to fetch the project homepage first so that we can find out the version URL 
        fetchProject(proj)
        
    if comp not in PROJDATA[proj]["components"]:
        print "Invalid Component"
        return
    
    # Otherwise, fetch the page
    plist = getJSON(PROJDATA[proj]["components"][comp])
    
    print "%s: Component %s\n\n%s" % (proj,plist['Name'],plist['Description'])
    print "--------------"
    print "Issues"
    print "--------------"
    print buildIssueTable(plist['issues'],isstype,issstatus)






def listProjectVersion(proj,ver,isstype=False,issstatus=False,showKnown=True,showFixes=True):
    ''' List issues for a specific project version
    
        Args:
        
        proj - the project key (E.g. GPXIN)
        ver - The version name (e.g. 1.02)
    
    
    '''
    
    if proj not in PROJDATA or "versions" not in PROJDATA[proj] or ver not in PROJDATA[proj]["versions"]:
        # We need to fetch the project homepage first so that we can find out the version URL 
        fetchProject(proj)
        
    if ver not in PROJDATA[proj]["versions"]:
        print "Invalid version"
        return
    
    # Otherwise, fetch the version page
    plist = getJSON(PROJDATA[proj]["versions"][ver])
    
    print "%s: Version %s\n\nState: %s" % (proj,plist['Name'],plist['State'])
    print "Time Est:     %s          Time Logged: %s\n"    % (plist['TimeEstimate'], plist['TimeLogged'])
    print "Release Date: %s\n" % (time.strftime('%Y-%m-%d', time.localtime(plist['ReleaseDate'])),)
    
    if showFixes:
        print "--------------"
        print "Fixed Issues"
        print "--------------"
        print buildIssueTable(plist['issues'],isstype,issstatus)
    

    if showKnown:
        print "\n--------------"
        print "Known Issues"
        print "--------------"
        print buildIssueTable(plist['Knownissues'],isstype,issstatus)    
    



def secondsToTime(s):
    ''' Convert a count in seconds to hours and minutes
    '''
    
    if not s:
        return "0h 0m"
    
    mins, secs = divmod(int(s),60)
    hours, mins = divmod(mins,60)
    
    return "%dh %02dm" % (hours,mins)


def printIssue(isskey):
    ''' Print out details about an issue
    '''
    if isskey not in ISSUEURLS:
        url = "%s/browse/%s.json" % (BASEDIR,isskey)
    else:
        url = ISSUEURLS[isskey]

    issue = getJSON(url)

    print "%s: %s\n\n" % (issue['Key'],issue['Name'])
    print "------------------"
    print "Issue Details"
    print "------------------"
    print "Issue Type:  %s" % (issue['IssueType'])
    print "Priority:    %s          Status: %s\n\n" % (issue['Priority'], issue['Status'])
    print "Reporter:    %s          Assignee: %s" % (issue['Reporter'], issue['assigneee'])
    print "Resolution:  %s\n" % (issue['Resolution'],)
    print "Time Est:    %s          Time Logged: %s\n"    % (secondsToTime(issue['TimeEstimate']), secondsToTime(issue['TimeLogged']))
    print "Last Change: %s\n\n" % (issue['LastModified'],)
    print "------------------"
    print "Issue Description"
    print "------------------\n"
    print "%s\n\n" % (issue['Description'],)
    
    # Print subtasks if there are any
    if len(issue['Relations']['SubTasks']) > 0:
            print "------------------"
            print "Subtasks"
            print "------------------\n"
            Cols = ['Key','Summary']
            rows = []
            for subtask in issue['Relations']['SubTasks']:
                entry = {
                        'Key' : subtask['Key'],
                        'Summary' : subtask['Name']
                    }
                rows.append(entry)
                if subtask['Key'] not in ISSUEURLS:
                    ISSUEURLS[subtask['Key']] = issue['href']
            
            print make_table(Cols,rows)
    
    # Print internal relations (if any)
    Cols = ['Relation Type','Key','Summary','URL']
    relrows = []
    if len(issue['Relations']['LinkedIssues']) > 0:
            for relissue in issue['Relations']['LinkedIssues']:
                entry = {
                        'Relation Type' : relissue['RelType'],
                        'Key' : relissue['Key'],
                        'Summary' : relissue['Name'],
                        'URL' : '' # Will be used later
                    }
                relrows.append(entry)
                if relissue['Key'] not in ISSUEURLS:
                    ISSUEURLS[relissue['Key']] = relissue['href']

            # We don't print yet, as we want to merge in any external links


    if "RelatedLinks" in issue['Relations']:
            for link in issue['Relations']['RelatedLinks']:
                entry = {
                        'Relation Type' : '',
                        'Key' : '',
                        'Summary' : link['title'],
                        'URL' : link['href']
                    }
                relrows.append(entry)
    
    # Similarly, add any attachments if present
    if len(issue['attachments']) > 0:
            for attachment in issue['attachments']:
                entry = {
                        'Relation Type' : 'Attachment',
                        'Key' : '',
                        'Summary' : attachment['Name'],
                        'URL' : attachment['href']
                    }
                relrows.append(entry)
    
    
    if len(relrows) > 0:
            print "\n------------------"
            print "Relations"
            print "------------------\n"        
            print make_table(Cols,relrows)            
    
    # Finally, the big one, issue comments
    if issue['Comments']['count'] > 0:
        print "\n------------------"
        print "Comments"
        print "------------------\n"
        for comment in issue['Comments']['items']:
                print "----------------------------------------------------------------"
                print "%s\n%s" % (comment['Author'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment['Created'])))
                print "----------------------------------------------------------------"
                print "%s\n\n" % (comment['body'],)


# These were used for testing when building the methods above
#listprojects()
#listProject('BTFW',isstype=['Task'],issstatus=['Open'])
#listProject('BUGGER')
#printIssue('BUGGER-4')
#printIssue('DNSCHAT-2')
#printIssue('BUGGER-1')
#printIssue('MAILARCHIV-10')
#listProjectVersion('GPXIN','1.02')
#listProjectVersion('GPXIN','1.02',showFixes=False)
#listProjectVersion('GPXIN','1.02',showKnown=False)
#listProjectComponent('GPXIN','Experimental Features')



# CLI related functions begin


def runInteractive(display_prompt,echo_cmd=False):
	try:
	    readline.read_history_file(os.path.expanduser("~/.pbtcli.history"))
	except: 
	    pass # Ignore FileNotFoundError, history file doesn't exist

	while True:
	    try:
		command = raw_input(display_prompt)

	    except EOFError:
		print("")
		break

	    if command == "q":
		break

	    elif command.startswith("#") or command == "" or command == " ":
		continue

	    if echo_cmd:
		print "> " + command

	    readline.write_history_file(os.path.expanduser("~/.pbtcli.history"))
	    processCommand(command)


def processCommand(cmd):
    ''' Process the command syntax to work out which functions need to be called
    '''
    
    # First, check whether we've just been given an issue key 
    if re.match('[A-Z]+-[0-9]+',cmd):
        return printIssue(cmd)


    # Split the command out to a list
    cmdlist = cmd.split(' ')

    if cmdlist[0] == "projects":
        return listprojects()

    if cmdlist[0] == "project":
        return parseProjectDisplay(cmdlist)


    if cmdlist[0] == "projectver":
        return parseProjectVerDisplay(cmdlist)
    

    if cmdlist[0] == "projectcomp":
        return parseProjectCompDisplay(cmdlist)



    if cmdlist[0] == "issue":
        return printIssue(cmdlist[1])
    


def parseProjectCompDisplay(cmdlist):
    ''' Handle the command line syntax for anything beginning with the word projectver
    '''
    
    # Most simple case, simply list the project
    if len(cmdlist) == 3:
        return listProjectComponent(cmdlist[1],cmdlist[2])

    if cmdlist[3] == "isopen":
        return listProjectComponent(cmdlist[1], cmdlist[2], issstatus=["Open","In Progress"])
    
    if cmdlist[3] == "type":
        return listProjectComponent(cmdlist[1], cmdlist[2], isstype=cmdlist[4:])
    
    if cmdlist[3] == "status":
        return listProjectComponent(cmdlist[1], cmdlist[2], issstatus=cmdlist[4:])    
        




def parseProjectVerDisplay(cmdlist):
    ''' Handle the command line syntax for anything beginning with the word projectver
    '''
    
    # Most simple case, simply list the project
    if len(cmdlist) == 3:
        return listProjectVersion(cmdlist[1],cmdlist[2])

    if cmdlist[3] == "knownissues":
        return listProjectVersion(cmdlist[1], cmdlist[2], showFixes=False)        

    if cmdlist[3] == "implements":
        return listProjectVersion(cmdlist[1], cmdlist[2], showKnown=False)


    if cmdlist[3] == "isopen":
        return listProjectVersion(cmdlist[1], cmdlist[2], issstatus=["Open","In Progress"])
    
    if cmdlist[3] == "type":
        return listProjectVersion(cmdlist[1], cmdlist[2], isstype=cmdlist[4:])
    
    if cmdlist[3] == "status":
        return listProjectVersion(cmdlist[1], cmdlist[2], issstatus=cmdlist[4:])    
        



def parseProjectDisplay(cmdlist):
    ''' Handle the command line syntax for anything beginning with the word project
    '''
    
    # Most simple case, simply list the project
    if len(cmdlist) == 2:
        return listProject(cmdlist[1])
        

    if cmdlist[2] == "isopen":
        return listProject(cmdlist[1], issstatus=["Open","In Progress"])
    
    if cmdlist[2] == "type":
        return listProject(cmdlist[1], isstype=cmdlist[3:])
    
    if cmdlist[2] == "status":
        return listProject(cmdlist[1], issstatus=cmdlist[3:])    
        


if len(sys.argv) < 2:
        # Launch interactive mode
        
        # If commands are being redirected/piped, we don't want to display the prompt after each
        mode = os.fstat(sys.stdin.fileno()).st_mode
        if stat.S_ISFIFO(mode) or stat.S_ISREG(mode):
                display_prompt = ""
                echo_cmd = True
        else:
                display_prompt = "pbtcli> "
                echo_cmd = False

        runInteractive(display_prompt,echo_cmd)
        sys.exit()


# Otherwise, pull the command from the commandline arguments
command=" ".join(sys.argv[1:])
processCommand(command)




