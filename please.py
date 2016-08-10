import sys, subprocess, os, math, os.path
import urllib, urllib2, urlparse
try:

	#import urllib2.urlparse
	import requests
	import lxml
	import lxml.html
	import lxml.cssselect
except ImportError:
	lxml = None

def fpjoin(aa):
	ret = os.path.join(aa[0], aa[1])
	for a in aa[2:]:
	 	ret = os.path.join(ret,a)
	return ret
def fphere():
	return os.path.dirname(os.path.realpath(__file__))
def fpjoinhere(aa):
	return fpjoin([fphere()]+aa)
def fptemp():
	return fpjoin([fphere(), 'temp'])
def cwdtemp():
	os.chdir(fptemp())
def mktemp():
	if os.path.isdir(fptemp()) == False:
		os.mkdir(fptemp())
def randfilename(dir, pre, ext):
	i = 1
	while True:
		fname = "{}{}.{}".format(pre, i, ext)
		if (os.path.isfile(os.path.join(dir, fname)) == False):
			return fname
		i=i+1
def fileSize(num, suffix='b'):
	for unit in ['','K','M','G','T','P','E','Z']:
	    if abs(num) < 1024.0:
	        return "%3.1f %s%s" % (num, unit, suffix)
	    num /= 1024.0
	return "%.1f %s%s" % (num, 'Y', suffix)
def long_substr(data):
	substr = ''
	if len(data) > 1 and len(data[0]) > 0:
		for i in range(len(data[0])):
			for j in range(len(data[0])-i+1):
				if j > len(substr) and is_substr(data[0][i:i+j], data):
					substr = data[0][i:i+j]
	return substr
def is_substr(find, data):
	if len(data) < 1 and len(find) < 1:
		return False
	for i in range(len(data)):
		if find not in data[i]:
			return False
	return True
def process_scrape(arg):
	if lxml == None:
			print "You need to install 'lxml' and 'requests' first."
			return
	mktemp()
	temps = []
	#try to get main page as pdf
	src_pdf_fp = fpjoinhere(['temp', 'scrape_source.pdf'])
	print ' Converting {} -> {} ...'.format(arg, src_pdf_fp)
	pop_in = ['wkhtmltopdf', arg, src_pdf_fp]
	pop = subprocess.Popen(' '.join(pop_in), shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = pop.communicate()
	if err and len(err):
		print '  Failed to convert source page'
	else:
		temps.append(src_pdf_fp)
	urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
	print ' Reading \n  {} ...'.format(arg), ;sys.stdout.flush();
	page = requests.get(arg)
	dom =  lxml.html.fromstring(page.text)
	selAnchor = lxml.cssselect.CSSSelector('a')
	foundElements = selAnchor(dom)
	#print [e.get('href') for e in foundElements if e.get('href') and e.get('href').endswith('.pdf')]
	foundPdf = [e.get('href') for e in foundElements if e.get('href') and e.get('href').endswith('.pdf')]
	#print foundPdf
	print ' [{} files]'.format(len(foundPdf)); sys.stdout.flush();
	print ' Downloading {} files...'.format(len(foundPdf))
	for pdf in foundPdf:
		fn = urllib2.urlparse.urlsplit(pdf).path.split('/')[-1]
		fp = fpjoinhere(['temp', fn])
		furl = urlparse.urljoin(arg, pdf).replace('\\', '/')
		print '  {} -> {} ...'.format(furl,  fp),; sys.stdout.flush();
		if (os.path.isfile(fp)):
			print ' (cached)',
		else:
			urllib.urlretrieve(furl, fp)
		temps.append(fp)
		print '[{}]'.format(fileSize(os.path.getsize(fp)))
	return temps
def join_files(files):
	fname_substr = long_substr(files)
	if len(fname_substr) and (os.path.isdir(fname_substr) == False):
		out_name = '{}.pdf'.format(fname_substr)
	else:
		out_dir = fname_substr if os.path.isdir(fname_substr) else fptemp()
		out_name = fpjoin([out_dir, randfilename(out_dir, 'join_', 'pdf')])
	pop_in = [fpjoinhere(['concat_pdf']), '--output', out_name] + files
	pop = subprocess.Popen(' '.join(pop_in), shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = pop.communicate()
	return out_name
def move_tabs_to_new_window():
	scpt = """
	tell application "Safari"
	set l to tabs of window 1 where index >= (get index of current tab of window 1)
	make new document
	repeat with t in (reverse of l)
		move t to beginning of tabs of window 1
	end repeat
	delete tab -1 of window 1
	end tell
	"""
	args = []
	p = subprocess.Popen(['osascript', '-'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	out = p.communicate(scpt)
	#print (p.returncode, stdout, stderr)
def process(text_):
	patts = []
	def new_patt(name):
		patts.append(name); return name;
	text = text_.strip()
	patt1 = new_patt('find files with ')
	patt2 = new_patt('find files named ')
	patt3 = new_patt('find duplicates')
	patt4 = new_patt('join files named ')
	patt5 = new_patt('show ')
	patt6 = new_patt('count files')
	patt7 = new_patt('scrape and join ')
	patt8 = new_patt('scrape ')
	patt9 = new_patt('move tabs')
	if text.startswith(patt1):
		arg = text[len(patt1):]
		pop_in = ['grep', '-ril', '"{}"'.format(arg), '.']
		pop = subprocess.Popen(' '.join(pop_in), shell = True, stdout=subprocess.PIPE)
		out, err = pop.communicate()
		print out
	elif text.startswith(patt2):
		arg = text[len(patt2):]
		pop_in = ['find', '.', '-maxdepth', '1', '-iname', '"*{}*"'.format(arg)]
		pop = subprocess.Popen(' '.join(pop_in), shell = True, stdout=subprocess.PIPE)
		out, err = pop.communicate()
		print out
	elif text.startswith(patt3):
		pop_in = ['fdupes', '.']
		pop = subprocess.Popen(' '.join(pop_in), shell = True, stdout=subprocess.PIPE)
		out, err = pop.communicate()
		print out
	elif text.startswith(patt4):
		arg = text[len(patt4):]
		pop_in = ['find', '.', '-maxdepth', '1', '-iname', '"*{}*"'.format(arg)]
		pop = subprocess.Popen(' '.join(pop_in), shell = True, stdout=subprocess.PIPE)
		out, err = pop.communicate()
		files = [x for x in sorted(out.split('\n')) if len(x)]
		print join_files(files)
	elif text.startswith(patt5):
		arg = text[len(patt5):]
		if arg.endswith('.txt'):
			pop_in = ['cat', arg]
			pop = subprocess.Popen(' '.join(pop_in), shell = True)
			pop.wait()
			print ''
		else:
			pop_in = ['open', '-a', 'Preview.app', arg]
			subprocess.Popen(' '.join(pop_in), shell = True)
	elif text.startswith(patt6):
		pop_in = ['find', '.', '-type', 'f', '-maxdepth', '1']
		pop = subprocess.Popen(' '.join(pop_in), shell = True, stdout=subprocess.PIPE)
		out, err = pop.communicate()
		print len([x for x in out.split('\n') if x.strip() != ''])
	elif text.startswith(patt7):
		arg = text[len(patt7):]
		temps = process_scrape(arg)
		print ' Joining ...'
		print '  {}'.format(join_files(temps))
	elif text.startswith(patt8):
		arg = text[len(patt8):]
		process_scrape(arg)
	elif text.startswith(patt9):
		move_tabs_to_new_window()
	else:
		print "Apologies, I could not understand what you said."
		print "I understand:"
		print '\n'.join([' ' + x for x in patts])

process(' '.join(sys.argv[1:]))
