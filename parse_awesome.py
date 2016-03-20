import time
import os
import cPickle as pickle
import argparse

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--db_path', dest='db_path', type=str, default='awesomedb.p', help='database pickle filename that we enrich')
args = parser.parse_args()

# -----------------------------------------------------------------------------
# main loop where we build list of already added papers
db = {}
fname = 'README.md'
md = open(fname, 'r').read()

# just handle the 'Applications' part
md_parse = md[ md.find('## Applications') : md.rfind('## Datasets') ]

# get links and titles of existing papers
links = []
titles = []
fp = 0
while md_parse.find('[Paper', fp) != -1:
    link_start = md_parse.find('](', md_parse.find('[Paper', fp)) + 2
    fp = md_parse.find(')', link_start)
    links.append( md_parse[link_start:fp] )
fp = -1
while md_parse[:fp].rfind('*,') != -1:
    title_end = md_parse[:fp].rfind('*,')
    fp = md_parse[:title_end].rfind('*')
    titles.append( md_parse[fp+1:title_end] )
titles.reverse()

db['_links'] = links
db['_titles'] = titles

# save the database before we quit
print 'saving database with %d papers to %s' % (len(db['_titles']), args.db_path)
pickle.dump(db, open(args.db_path, 'wb'))
