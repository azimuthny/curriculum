#!/usr/bin/python
import urllib2, base64
from code import interact
import json
from time import sleep
import pprint
from code import interact
from search_web import dump_results_to_file, consolidate_results
import argparse
import os

parser = argparse.ArgumentParser(description='Given a file with a listing of search terms, create a joint file containing a mapping of each search term to a retrieved URL for that search term by bing ')
parser.add_argument('--search-list',required=True,help='list of search terms separated by newline')
args    = parser.parse_args()
prefix  = args.search_list.split('.')[0]
dirname = prefix

unique_index = 0
with open('%s.search_urls'%(prefix),'w') as fout:
	for i,line in enumerate(open('%s.search_list'%(prefix))):
		search_term = line.strip()
		print 'searching for [', search_term, ']'
		dump_results_to_file(search_term) # a file will always be created for each corresponding search term
		results = consolidate_results(search_term)
		for  term_rank, (url, title) in enumerate(results):
			fout.write('%d\t%s\t%d\t%s\t%s\n'%(unique_index,search_term,term_rank,title,url))
			unique_index+=1
