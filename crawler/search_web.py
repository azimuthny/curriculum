#!/usr/bin/python
import urllib2, base64
from code import interact
import json
import argparse
from time import sleep
import pprint
from code import interact


def search_bing(query, page):
	skip = page*50
	url = 'https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%27web%27&Query=%27' + query.replace(' ', '%20') + '%27&$format=json&$skip='+str(skip)


	request = urllib2.Request(url)
	base64string = base64.encodestring('%s:%s' % ('', 'oOnqVKMvJW//NKDLvdM6LUfxqbYCxdS8+bKNe9S0Y+c')).replace('\n', '')
	request.add_header('Authorization', 'Basic %s' % base64string)
	result = urllib2.urlopen(request)
	sleep(0.2)
	
	return result.read()

def get_results(result_string):
	json_results = json.loads(result_string)	
	result_list = json_results['d']['results'][0]['Web']
	return result_list

def results_to_dict(query, page=0):
	results = []
	results_list = get_results(search_bing(query,page))
	for result in results_list:
		result_dict = dict()
		try:
			title       = result['Title']
			description = result['Description']
			#source 	    = result['Source']
			url         = result['Url']
			meta        = result['__metadata']
			ID          = result['ID']

			result_dict['title']       = title
			result_dict['description'] = description
			result_dict['url']         = url
			result_dict['meta']	   = meta
			result_dict['ID']          = ID
			#result_dict['source']	   = source

			#print source, '|', title
			#print title, '|', url
			results.append(result_dict)
			#results.append(url)
		except KeyError:
			pass
			#print 'result key error'

	return results

def format_results_for_query(query, max_pages=1):
	result_file = ''
	for page in range(0, max_pages):
		for result in get_results(search_bing(query, page)):
			result_file += result['Title'].strip() + '\t' + result['Url'].strip() + '\n'
	return result_file

def dump_results_to_file(query, npages=10):
	fout = open(query+'.results','w')
	for page in range(npages):
		print '\tsearching ', page
		results = results_to_dict(query,page)
		for result in results:
			url   = result['url']
			title = result['title']
			try:
				fout.write('%s\t%s\n'%(title.encode('utf8'),url))
			except (UnicodeDecodeError,UnicodeEncodeError):
				print '\tpassing'

def consolidate_results(query,write_to_file=False):
	ranked_results = {}
	for i, line in enumerate(open(query+'.results')):
		title, url = line.strip().split('\t')
		if not url in ranked_results:
			if i<320:
				ranked_results[url] = {'rank':i,'title':title}

	ranked_list = [ (url,item['title']) for (url,item) in sorted(ranked_results.items(),key=lambda x: x[1]['rank']) ]
	if write_to_file:
		with open(query.replace(' ','_')+'.ranked','w') as fout:
			for url,title in ranked_list:
				fout.write('%s\t%s\t%s\n'%(query,title,url))
	return ranked_list
		
def main(search_term='linear regression'):
    dump_results_to_file(search_term)
    consolidate_results(search_term,True)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Given a search term, generate a list of urls returned by BING for that search query')
    parser.add_argument('--search-term',required=True,help='search term')
    args = parser.parse_args()
    print 'search term: ', args.search_term.strip()
    main(args.search_term.strip())
