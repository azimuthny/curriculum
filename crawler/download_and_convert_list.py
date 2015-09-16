#!/usr/bin/python
import argparse
import urllib2
from boilerpipe.extract import Extractor
import subprocess
from premailer import transform
from mechanize import Browser
import os

parser = argparse.ArgumentParser(description='given a url, fetch the content and convert to plain text and save it in the provided output directory, creating directories for each search_term in the process')
parser.add_argument('--search-list', required=True, help = 'file containing the search list')
parser.add_argument('--output-dir',  required=True, help = 'output directory')
args = parser.parse_args()

mech = Browser()
mech.set_handle_robots(False)
mech.addheaders = [('user-agent', '   Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'), ('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]

extra_skip = 0
for i,line in enumerate(open(args.search_list)):
	unique_index, query, rank, title, url = line.strip().split('\t')
	unique_index = int(unique_index)
	directory = os.path.join(args.output_dir,query.replace(' ','_'))
	if not os.path.exists(directory):
		os.makedirs(directory)

	if extra_skip>0:
		print 'skipping',i
		extra_skip-=1
		continue

	if os.path.exists(os.path.join(directory,'%d.txt.html'%unique_index)) or os.path.exists(os.path.join(directory,'%d.txt'%unique_index)):
		print 'skipping',i
		extra_skip=1
		continue


	print query, title, '(%d) DOWNLOADING ....'%(i)
	try:
		result = mech.open(url)
		print '\tdownloaded. processing...'


		if not url.split('.')[-1]=='pdf':
			print ' this is an html file'
			''' html download '''
			html = result.read()
			print 'html contents available'
			extractor = Extractor(extractor='KeepEverythingExtractor',html=html)
			print 'extractor created'
			#extractor = Extractor(html=html)
			extracted_text = extractor.getText()
			
			#print '\n'.join([ line for line in extracted_text.split('\n') if len(line) > 40])
			output = '\n'.join([ line for line in extracted_text.split('\n') if len(line) > 40])
			with open(os.path.join(directory,'%d.txt.html'%unique_index),'w') as fout:
				fout.write(output.encode('utf-8'))
		else:
			print ' this is a pdf file'
			pdf_file = open('preview_downloads/dummy.pdf','w').write(result.read())
			p = subprocess.Popen('pdftohtml -xml preview_downloads/dummy.pdf',shell=True) 
			print 'waiting to finish converting to html'
			p.wait()
			xml_filename = 'preview_downloads/dummy.xml'
			xml_orig = open(xml_filename).read().decode('utf-8')
			xml_new = xml_orig.replace('<pdf2xml producer="poppler" version="0.29.0">','<pdf2xml>')
			open('preview_downloads/dummy.xml','w').write(xml_new.encode('utf-8'))
			p = subprocess.Popen('pdfreflow preview_downloads/dummy.xml',shell=True)
			p.wait()
			html_content = open('preview_downloads/dummy.html').read().decode('utf-8')
			html_premailed = transform(html_content)
			open('preview_downloads/dummy.html','w').write(html_premailed.encode('utf-8'))
			extractor = Extractor(extractor='KeepEverythingExtractor',html=html_content)
			extracted_text = extractor.getText()
			#print '\n'.join([ line for line in extracted_text.split('\n') if len(line) > 40])
			out = '\n'.join([ line for line in extracted_text.split('\n') if len(line) > 40])
			with open(os.path.join(directory,'%d.txt'%unique_index),'w') as fout:
				fout.write(out.encode('utf-8'))
	except:
		print '~~~~~~!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!~~~~~~~~~~~~~~'
