import urllib2
import shutil
import time
import os
import random
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
pos = [0]        # for saving positions where new section starts
classes = []    # for classification
fp = 0
while md_parse.find('### ', fp+1) != -1:
    paper_start = md_parse.find('[Paper', fp+1)
    fp = md_parse.find('### ', fp+1)
    if paper_start < fp:
        pos.append(fp)
fp = 0
while md_parse.find('[Paper', fp) != -1:
    link_start = md_parse.find('](', md_parse.find('[Paper', fp)) + 2
    fp = md_parse.find(')', link_start)
    links.append( md_parse[link_start:fp] )
    for i in range(len(pos)-1):
        if link_start >= pos[i] and link_start < pos[i+1]:
            classes.append(i)
            break
fp = -1
while md_parse[:fp].rfind('*,') != -1:
    title_end = md_parse[:fp].rfind('*,')
    fp = md_parse[:title_end].rfind('*')
    titles.append( md_parse[fp+1:title_end] )
titles.reverse()

'''''''''''''''''''''''''''''''''''
# download pdf files in awesome-X
'''''''''''''''''''''''''''''''''''
# This part currently has some problem in that we cannot download
# version-upgraded arxiv paper due to the already existing rawid in pdf/

os.system('mkdir -p pdf') # ?

timeout_secs = 10 # after this many seconds we give up on a paper
numok = 0
numtot = 0
have = os.listdir('pdf') # get list of all pdfs we already have
for i in range(len(links)):
    pdf_url = links[i]

    basename = pdf_url.split('/')[-1]
    if basename[-4:] != '.pdf':
        basename = basename + '.pdf'
    fname = os.path.join('pdf', basename)

    # try retrieve the pdf
    numtot += 1
    try:
        if not basename in have:
            print 'fetching %s into %s' % (pdf_url, fname)
            req = urllib2.urlopen(pdf_url, None, timeout_secs)
            with open(fname, 'wb') as fp:
                shutil.copyfileobj(req, fp)
            time.sleep(0.1 + random.uniform(0,0.2))
        else:
            print '%s exists, skipping' % (fname, )
        numok += 1
    except Exception, e:
        print 'error downloading: ', pdf_url
        print e

print '%d/%d of %d downloaded ok.' % (numok, numtot, len(links))

'''''''''''''''''''''''''''''''''
# parse pdf to txt for awesome-X
'''''''''''''''''''''''''''''''''
os.system('mkdir -p txt') # ?

have = os.listdir('txt')
files = os.listdir('pdf')
for i,f in enumerate(files):
  pdf_path = os.path.join('pdf', f)
  txt_basename = f + '.txt'
  txt_path = os.path.join('txt', txt_basename)
  if not txt_basename in have:
    cmd = "pdftotext %s %s" % (pdf_path, txt_path)
    os.system(cmd)
    print '%d/%d %s' % (i, len(files), cmd)

    # check output was made
    if not os.path.isfile(txt_path):
      # there was an error with converting the pdf
      os.system('touch ' + txt_path) # create empty file, but it's a record of having tried to convert

    time.sleep(0.02) # silly way for allowing for ctrl+c termination
  else:
    print 'skipping %s, already exists.' % (pdf_path, )


db['_links'] = links
db['_titles'] = titles
db['_classes'] = classes

# save the database before we quit
print 'saving database with %d papers to %s' % (len(db['_titles']), args.db_path)
pickle.dump(db, open(args.db_path, 'wb'))
