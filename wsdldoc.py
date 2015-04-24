#!/usr/bin/python

from sys import argv
from lxml import *
from lxml import etree
from lxml import objectify
import sys, traceback
from os import system,getcwd
import subprocess

try:
	print 'opening '+argv[1]
	url = argv[1]
	
	try:
		url2 = argv[2]
		print 'output directory: ',url2
	except:
		url2 = '.'
except:
	print 'no file specified.\nusage: wsdlDoc input_file [output_directory (optional)]'
	exit()

tree = etree.parse(url)
root = tree.getroot()

class Wsdl():
	def __init__(self):
		self.operations = {}
		self.namespaces = {}
		self.root = ''
		
	def __init__(self,root):
		self.operations = {}
		self.namespaces = {}
		self.root = root
		self.elements = root.findall('.//{*}element')
		self.setOperations()

	def setOperations(self):
		operations = self.root.findall('.//{*}operation')
		for o in operations:
			par = o.getparent()
			if 'portType' in str(par):
				opName = o.tag.split('{')[1].split('}')[0]+o.attrib['name']
				name = opName.split('/')[-1]
				self.operations[opName] = {'completeName':opName,'name':name,'input':[],'output':[],'fault':[]}
				inputMessages = self.root.findall(".//{*}operation/[@name='"+name+"']/{*}input")
				for i in inputMessages:
					try:
						self.operations[opName]['input'].append(i.attrib['message'])
					except: pass
				outMessages = self.root.findall(".//{*}operation/[@name='"+name+"']/{*}output")
				for i in outMessages:
					try:
						self.operations[opName]['output'].append(i.attrib['message'])
					except: pass
				faultMessages = self.root.findall(".//{*}operation/[@name='"+name+"']/{*}fault")
				for i in faultMessages:
					try:
						self.operations[opName]['fault'].append(i.attrib['message'])
					except: pass
	
	def operations2html(self):
		html = ''
		for o in self.operations:
				htmltmp = ''
				htmltmp = htmltmp + '\n<H1>%s - %s</H1>' % (url.split('/')[-1].split('.')[0],self.operations[o]['name'])
				htmltmp = htmltmp + "\n<h3>Request Messages:</h3>\n"
				for i in self.operations[o]['input']:
					htmltmp = htmltmp + "\n<p>%s</p>" % (i)
				if len(self.operations[o]['output'])>0:
					htmltmp = htmltmp + "\n<h3>Response operations:</h3>\n"
				for i in self.operations[o]['output']:
					htmltmp = htmltmp + "\n<p>%s</p>" % (i)
				if len(self.operations[o]['fault'])>0:
					htmltmp = htmltmp + "\n<h3>Fault operations:</h3>\n"
				for i in self.operations[o]['fault']:
					htmltmp = htmltmp + "\n<p>%s</p>" % (i)
				html = html + htmltmp
		return html
		
	def complexTypes2html(self,el):
		html=''
		for e in el:
			htmlTmp = ''
			try:
				name = htmlTmp,e.attrib['name']
			except:
				try:
					name = htmlTmp,e.getparent().attrib['name']
				except:
					name = htmlTmp,e.getparent().getparent().attrib['name']
			try:
				htmlTmp = '%s\n<table border="0" width="1000px">\n\t<tr>\n\t\t<th colspan="4" bgcolor="#92CDDC">~ %s ~</th>\n  </tr><tr>\n\t\t<th colspan="4"></th>\n\t</tr>'% (name)
				htmlTmp = htmlTmp +'<tr>\n\t\t<td width="30%"><b>Nome Parametro</b></td>\n\t\t<td width="30%"><b>Obbligatorio</b></td>\n\t\t<td width="30%"><b>Formato</b></td>\n\t\t<td width="10%"><b>Descrizione</b></td>\n\t</tr>' 
				for c in e.getchildren():
					htmlTmp = htmlTmp+'<tr>\n    <td>%s</td><td>' % (c.attrib['name'])
					mandatory='si'
					type_=c.attrib['type'].split(':')[1]
					try:
						if c.attrib['minOccurs']=='0':
							mandatory='no'
					except: pass
					htmlTmp=htmlTmp+"%s</td><td>%s</td><td></td>\n  </tr>\n" % (mandatory,type_)
				htmlTmp=htmlTmp+"</table>"
				html = html+htmlTmp
			except:
				pass
		return html
	
	def simpleTypes2html(self,el):
		html=''
		for e in el:
			try: 
				htmlTmp=''
				try: t = e.getchildren()[0].tag.split('}')[1]
				except: pass
				if t=='enumeration':
					htmlTmp = '%s\n<table border="0" width="1000px">\n  <tr>\n    <th colspan="4" bgcolor="#92CDDC">~%s ~ (enumeration)</b></th>\n  </tr><tr>\n    <th colspan="4" align="left" ><h5>'%(htmlTmp, e.getparent().attrib['name'])
					for e in e.getchildren():
						enum = e.attrib['value']
						htmlTmp=htmlTmp+enum+"; "
					htmlTmp=htmlTmp+'</th>\n  </tr></b></h5></table>'
				html=html+htmlTmp	
			except: pass
		return html
	
	def extension2html(self,el):
		html=''
		for e in el:
			types=' '
			htmlTmp=''
			try: 
				name=e.getparent().getparent().getparent().attrib['name']
				htmlTmp = htmlTmp+'\n<table border="0" width="1000px">\n  <tr>\n    <th colspan="4" bgcolor="#92CDDC">~ '+name+' ~ (extension)</b></th>\n  </tr><tr>\n    <th colspan="4" align="left" ><h5>'
				for c in e.getchildren():
					try:
						htmlTmp = htmlTmp+'<tr>\n    <td>'+c.attrib['name']+"</td><td>"
						mandatory='si'
						try:
							if c.attrib['minOccurs']=='0':
								mandatory='no'
						except:
							pass
						atype=''
						atype=c.attrib['type'].split(':')[1]
						htmlTmp=htmlTmp+mandatory+"</td><td>"+atype+"</td>"
						if (" "+atype+" ") not in types:
							types = types + atype + " "
						htmlTmp=htmlTmp+"<td></td>\n  </tr>\n"
					except: htmlTmp=htmlTmp+"<tr>\n    <td></td></tr><tr>\n    <td></td></tr><tr>\n    <td></td></tr><tr>\n    <td>campo non parsificato.</td></tr>"
				htmlTmp=htmlTmp+'</th>\n  </tr></b></h5>tipi presenti in '+name+':'+types+' </table>'
				html=html+htmlTmp
			except: pass
		return html
		
	def type2html(self):
		imp = root.findall(".//{*}import")
		inc = root.findall(".//{*}include")
		elc = root.findall(".//{*}complexType/")
		els = root.findall(".//{*}simpleType/")
		ext = root.findall(".//{*}extension/")
		imports = []
		for i in imp+inc:
			try:
				n = i.attrib['schemaLocation']
				if n not in imports:

					imports.append(n)
					urlimp='.'+('/'.join(url.split('/')[:-1]))+'/'+i.attrib['schemaLocation']
					print urlimp
					if len(root.findall(".//{*}import")+root.findall(".//{*}include"))>0:
						for z in root.findall(".//{*}import")+root.findall(".//{*}include"):
							
							urlimp3=('/'.join(urlimp.split('/')[:-1]))+'/'+z.attrib['schemaLocation']
							tree3 = etree.parse(urlimp3)
							root3 = tree3.getroot()
							elc=elc+root3.findall(".//{*}complexType/")
							els=els+root3.findall(".//{*}simpleType/")
							ext = ext+root3.findall(".//{*}extension/")
							
					tree2 = etree.parse(urlimp)
					root2 = tree2.getroot()
					elc=elc+root2.findall(".//{*}complexType/")
					els=els+root2.findall(".//{*}simpleType/")
					ext = ext+root2.findall(".//{*}extension/")
					print 'caricato',i.attrib['schemaLocation']
			except Exception as e: print e
		html=self.complexTypes2html(elc)
		html=html+self.extension2html(ext)
		html=html+self.simpleTypes2html(els)
		return html
		
	def html(self,html):
		title=url.split('/')[-1].split('.')[0]+"DOC"
		html = '<head><title>%s</title>\n<style>\nh1 {color: #4f81bd;\nbackground-color:#000000; \n}\n</style></head><body>%s</body>'%(title,html)
		output = open(url2+'/'+title+'.html','w')
		print 'scrivo file',title+'.html'
		output.write(html)
		output.close()
	

wsdl = Wsdl(root)
html=wsdl.operations2html()+wsdl.type2html()
wsdl.html(html)

