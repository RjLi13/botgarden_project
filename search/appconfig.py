# set global variables

from os import path, popen
from common import cspace # we use the config file reading function
from cspace_django_site import settings
import csv


def getParms(parmFile, SUGGESTIONS):
    try:
        f = open(parmFile, 'rb')
        csvfile = csv.reader(f, delimiter="\t")
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % parmFile
        return message, -1
    except:
        raise

    try:
        rows = []
        for row, values in enumerate(csvfile):
            rows.append(values)

        return parseRows(rows, SUGGESTIONS)

    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % parmFile
        return message, -1
    except:
        raise


def parseRows(rows, SUGGESTIONS):
    PARMS = {}
    HEADER = {}
    labels = {}
    FIELDS = {}

    SEARCHCOLUMNS = 0
    SEARCHROWS = 0

    functions = 'Search,Facet,bMapper,listDisplay,fullDisplay,gridDisplay,inCSV'.split(',')
    for function in functions:
        FIELDS[function] = []

    fieldkeys = 'label fieldtype suggestions solrfield name X order'.split(' ')

    for rowid, row in enumerate(rows):
        rowtype = row[0]

        if rowtype == 'header':
            for i, r in enumerate(row):
                HEADER[i] = r
                labels[r] = i

        elif rowtype == 'field':
            needed = [row[labels[i]] for i in 'Label Role Suggestions SolrField Name Search'.split(' ')]
            if row[labels['Suggestions']] != '':
                #suggestname = '%s.%s' % (row[labels['Suggestions']], row[labels['Name']])
                suggestname = row[labels['Name']]
            else:
                suggestname = row[labels['Name']]
            needed[4] = suggestname
            PARMS[suggestname] = needed
            needed.append(rowid)

            for function in functions:
                if len(row) > labels[function] and row[labels[function]] != '':
                    fieldhash = {}
                    for n, v in enumerate(needed):
                        if n == 5 and function == 'Search': # 5th item in needed is search field x,y coord for layout
                            if v == '':
                                continue
                            searchlayout = (v+',1').split(',')
                            fieldhash['column'] = int('0'+searchlayout[1])
                            fieldhash['row'] = int('0'+searchlayout[0])
                            SEARCHCOLUMNS = max(SEARCHCOLUMNS, int('0'+searchlayout[1]))
                            SEARCHROWS = max(SEARCHROWS, int('0'+searchlayout[0]))
                        else:
                            fieldhash[fieldkeys[n]] = v
                    fieldhash['style'] = 'width:200px' # temporary hack!
                    fieldhash['type'] = 'text' # temporary hack!
                    FIELDS[function].append(fieldhash)

    if SEARCHROWS == 0 : SEARCHROWS = 1
    if SEARCHCOLUMNS == 0 : SEARCHCOLUMNS = 1

    return FIELDS, PARMS, SEARCHCOLUMNS, SEARCHROWS


def loadConfiguration(configFileName):
    config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), configFileName)

    global MAXMARKERS
    global MAXRESULTS
    global MAXLONGRESULTS
    global MAXFACETS
    global EMAILABLEURL
    global IMAGESERVER
    global CSPACESERVER
    global INSTITUTION
    global BMAPPERSERVER
    global BMAPPERDIR
    global BMAPPERCONFIGFILE
    global SOLRSERVER
    global SOLRCORE
    global LOCALDIR
    global SEARCH_QUALIFIERS
    global FIELDDEFINITIONS
    global CSVPREFIX
    global CSVEXTENSION
    global TITLE
    global SUGGESTIONS
    global LAYOUT
    global LOCATION
    global DROPDOWNS
    global FIELDS
    global PARMS
    global SEARCHROWS
    global SEARCHCOLUMNS
    global VERSION

    try:
        MAXMARKERS = int(config.get('search', 'MAXMARKERS'))
        MAXRESULTS = int(config.get('search', 'MAXRESULTS'))
        MAXLONGRESULTS = int(config.get('search', 'MAXLONGRESULTS'))
        MAXFACETS = int(config.get('search', 'MAXFACETS'))
        EMAILABLEURL = config.get('search', 'EMAILABLEURL')
        IMAGESERVER = config.get('search', 'IMAGESERVER')
        CSPACESERVER = config.get('search', 'CSPACESERVER')
        INSTITUTION = config.get('search', 'INSTITUTION')
        BMAPPERSERVER = config.get('search', 'BMAPPERSERVER')
        BMAPPERDIR = config.get('search', 'BMAPPERDIR')
        BMAPPERCONFIGFILE = config.get('search', 'BMAPPERCONFIGFILE')
        SOLRSERVER = config.get('search', 'SOLRSERVER')
        SOLRCORE = config.get('search', 'SOLRCORE')
        LOCALDIR = config.get('search', 'LOCALDIR')
        SEARCH_QUALIFIERS = config.get('search', 'SEARCH_QUALIFIERS').split(',')
        FIELDDEFINITIONS = config.get('search', 'FIELDDEFINITIONS')
        CSVPREFIX = config.get('search', 'CSVPREFIX')
        CSVEXTENSION = config.get('search', 'CSVEXTENSION')
        TITLE = config.get('search', 'TITLE')
        SUGGESTIONS = config.get('search', 'SUGGESTIONS')
        LAYOUT = config.get('search', 'LAYOUT')

        try:
            VERSION = popen("cd " + settings.BASE_PARENT_DIR + " ; /usr/bin/git describe --always").read().strip()
            if VERSION == '': # try alternate location for git (this is the usual Mac location)
                VERSION = popen("/usr/local/bin/git describe --always").read().strip()
        except:
            VERSION = 'Unknown'

    except:
        print 'error in configuration file %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + configFileName)
        print 'this webapp will probably not work.'

    # get "frontend" configuration from the ... frontend configuaration file FIELDDEFINITIONS

    print 'Reading field definitions from %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + FIELDDEFINITIONS)

    FIELDS, PARMS, SEARCHCOLUMNS, SEARCHROWS = getParms(path.join(settings.BASE_PARENT_DIR, 'config/' + FIELDDEFINITIONS), SUGGESTIONS)

    LOCATION = ''

    DROPDOWNS = []
    for p in PARMS:
        if 'dropdown' in PARMS[p][1]:
            DROPDOWNS.append(PARMS[p][4])
        if 'location' in PARMS[p][1]:
            LOCATION = PARMS[p][3]

    if LOCATION == '':
        print "LOCATION not set, please specify a variable as 'location'"


loadConfiguration('search')
print 'Configuration successfully read'
