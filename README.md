# PBTCLI


## About

A python based commandline utility to fetch the json representations from JIRA projects at [https://projects.bentasker.co.uk](https://projects.bentasker.co.uk) and display them as plain text.

Basically a tool for my own convenienve, allows me to grab data from projects/issues without leaving the comfort of my terminal. The JSON representations are generated by [JILS](https://github.com/bentasker/Jira-Issue-Listing) as of [JILS-43](https://projects.bentasker.co.uk/jira_projects/browse/JILS-43.html)

It's currently *very* rough and ready. Essentially, it's a proof of concept for a wider project that will implement similar capabilities in a single script encompassing most (if not all) of my web estate, so that I can grap snippets from [snippets.bentasker.co.uk](https://snippets.bentasker.co.uk) as well as check issues at [projects.bentasker.co.uk](https://projects.bentasker.co.uk). The realisation of that browserless dream is a little way off though.


### Caching

By default, pages are cached for a short time (at time of writing, 15 minutes) to avoid repeated requests to the server if a resource is continually being reviewed (or in the case of project pages, potentially re-used).

The CLI will allow you to interact with the cache to a small extent, and the cache is maintained between sessions by writing to an on-disk cache file. During execution the cache runs entirely in memory.

There's also an offline mode, which is initially toggled based upon a test request to the configured server. If the script believes that we're offline, then items in cache will not be invalidated, and attempts will not be made to fetch content from the server where an item isn't in cache. Offline mode can be manually turned on/off via the CLI (see below). It's a simplistic implementation but means I can review things without having connectivity.




### Features

* Caching to reduce number of upstream connections
* Pipe support
* CLI maintains history
* Offline reading mode



## Usage

Commands can be parsed in one of three ways

* Piped (e.g. `echo projects | ./pbt_cli.py`)
* Interactivey (`./pbt_cli.py`)
* As arguments (`./pbt_cli.py projects`)

Where something intended as single argument contains a space, it should be quoted:

    ./pbt_cli.py projectcomp GPXIN 'Experimental Features'


### Navigation

The upstream JSON files define whether there's a 'next' or 'previous' issue, where those are available, you can switch to them by using the following keystrokes

    n - move to the issue defined next
    b - move to the issue defined previous
    [p|back] - move to the previous issue you viewed
    

### General

    [Issue Key] - Display the named issue
    projects - List all projects


### Project views

    project [projkey] - List all issues for the specified project
    project [projkey] isopen - List only Open issues for the project
    project [projkey] type [types] - List only issues of type (multiple types can be space seperated)
    project [projkey] status [statuses] - List only issues with status matching list (multiple types can be space seperated without quotes)
    project [projkey] title [searchstring] - List only issues where title contains specified phrase
    project [projkey] listcomps - List components for the project
    project [projkey] listvers - List version names for the project
    

### Project Versions

    projectver [projkey] [ver] - List all issues for the specified project version
    projectver [projkey] [ver] isopen - List only Open issues for the project version
    projectver [projkey] [ver] type [types] - List only issues of type (multiple types can be space seperated)
    projectver [projkey] [ver] status [statuses] - List only issues with status matching list (multiple types can be space seperated without quotes).
    projectver [projkey] [ver] knownissues - List only known issues affecting specified version
    projectver [projkey] [ver] implements - List only issues implemented (or fixed) in the specified version
    projectver [projkey] [ver] title [searchstring] - List only issues where title contains specified phrase
    projectver [projkey] listvers - List version names for the project
    

### Project Components

    projectcomp [projkey] [comp name] - List all issues for the specified project component
    projectcomp [projkey] [comp name] isopen - List only Open issues for the project component
    projectcomp [projkey] [comp name] type [types] - List only issues of type (multiple types can be space seperated)
    projectcomp [projkey] [comp name] status [statuses] - List only issues with status matching list (multiple types can be space seperated without quotes).
    projectcomp [projkey] [comp name] title [searchstring] - List only issues where title contains specified phrase
    projectcomp [projkey] listcomps - List components for the project    
    

### Issue View

    issue [Issue Key] - Display the named issue
    [Issue Key] - Shortcut to the above


### Cache Interaction

    cache dump - Dumps out keys, values and expiry times from the cache (generates a *lot* of output)
    cache fetch [issuekey|url] - Fetch the specified Issue/URL and write into cache
    cache flush - Flush all values out of the cache (will also update the ondisk cache)
    cache get [key] - Fetch the value of a specific item from the cache
    cache invalidate [key] - Invalidate a specific item from the cache
    cache print - Print keys and expiry times (but not values) from the cache

### Offline Reading Mode

    set Offline - Tell the cache we're offline
    set Online - Tell the cache we're online



## TODO

* Add ability to cache an entire project via the cache subcommands
* Add ability to cache entire archive
* Add ability to search (or a close approximation of)
* Include keywords in output
* Trigger pager for particularly long output

    
    
## Copyright


PBTCli is Copyright (C) 2017 B Tasker. All Rights Reserved.
Released under the GNU GPL V2 License, see LICENSE.
