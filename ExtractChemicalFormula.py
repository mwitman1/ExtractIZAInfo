#! usr/bin/env python3

import wget
import sys, re, os
import requests, json
from html.parser import HTMLParser


#class HTMLtoJSONParser(HTMLParser):
#    """
#    Class from http://www.xavierdupre.fr/blog/2013-10-27_nojs.html
#    """
#    
#    def __init__(self, raise_exception = True) :
#        HTMLParser.__init__(self)
#        self.doc  = { }
#        self.path = []
#        self.cur  = self.doc
#        self.line = 0
#        self.raise_exception = raise_exception
#         
#    @property
#    def json(self):
#        return self.doc
#         
#    @staticmethod
#    def to_json(content, raise_exception = True):
#        parser = HTMLtoJSONParser(raise_exception = raise_exception)
#        parser.feed(content)
#        return parser.json
#         
#    def handle_starttag(self, tag, attrs):
#        self.path.append(tag)
#        attrs = { k:v for k,v in attrs }
#        if tag in self.cur :
#            if isinstance(self.cur[tag],list) :
#                self.cur[tag].append(  { "__parent__": self.cur } )
#                self.cur = self.cur[tag][-1]
#            else :
#                self.cur[tag] = [ self.cur[tag] ]
#                self.cur[tag].append(  { "__parent__": self.cur } )
#                self.cur = self.cur[tag][-1]
#        else :
#            self.cur[tag] = { "__parent__": self.cur }
#            self.cur = self.cur[tag]
#             
#        for a,v in attrs.items():
#            self.cur["#" + a] = v
#        self.cur[""] = ""
#                 
#    def handle_endtag(self, tag):
#        if tag != self.path[-1] and self.raise_exception :
#            raise Exception("html is malformed around line: {0} (it might be because of a tag <br>, <hr>, <img .. > not closed)".format(self.line))
#        del self.path[-1]
#        memo = self.cur
#        self.cur = self.cur["__parent__"]
#        self.clean(memo)
#                 
#    def handle_data(self, data):
#        self.line += data.count("\n")
#        if "" in self.cur :
#            self.cur[""] += data
#             
#    def clean(self, values):
#        keys = list(values.keys())
#        for k in keys:
#            v = values[k]
#            if isinstance(v, str) :
#                #print ("clean", k,[v])
#                c = v.strip(" \n\r\t")
#                if c != v : 
#                    if len(c) > 0 : 
#                        values[k] = c
#                    else : 
#                        del values[k]
#        del values["__parent__"]





def get_structures(IZA_file):

    f = open(IZA_file, "r")
    IZA_list = f.read().strip().split('\n')
    return IZA_list

def sed_chemicalize_regex(string):

    string=re.sub(r"<SUB>",r"_(",string,flags=re.IGNORECASE)
    string=re.sub(r"</SUB>",r")",string,flags=re.IGNORECASE)
    string=re.sub(r"<SUP>",r"^(",string,flags=re.IGNORECASE)
    string=re.sub(r"</SUP>",r")",string,flags=re.IGNORECASE)
    string=re.sub(r"<b>",r"",string,flags=re.IGNORECASE)
    string=re.sub(r"</b>",r"",string,flags=re.IGNORECASE)
    string=re.sub(r"<br>",r"",string,flags=re.IGNORECASE)
    string=re.sub(r"<br/>",r"",string,flags=re.IGNORECASE)
    string=re.sub(r"<td>",r"",string,flags=re.IGNORECASE)
    string=re.sub(r"</td>",r"",string,flags=re.IGNORECASE)
    #print(string)

    return string

def sed_for_ChemicalFormula(htmlContent):

    if(os.path.isfile(htmlContent)):
        f = open(htmlContent,"r")
        htmlContent = f.read()
    else:
        htmlContent=htmlContent.split("\n")

    found=False
    for i in range(len(htmlContent)-1):
        line=htmlContent[i]

        if("Chemical Formula" in line):
            #print(line)
            chem_from_line=htmlContent[i+1]
            #print(chem_from_line)
            found = True
            break

    if(found==False):
        print("Chemical Formula not found")
        return "None"
    else:
        #chem_from_html=re.search(r"\&nbsp\;(.+)\n", chem_from_line)
        chem_from_html=re.findall(r"^([^;]+);([^;]+)", chem_from_line)[0][1]

        #print(chem_from_html)
        return chem_from_html



    

def extract_data(IZA_list):

    IZA_data=[]
    IZA_chem_form=[]

    for IZA in IZA_list:
        print(IZA)
        url = "http://america.iza-structure.org/IZA-SC/material_tm.php?STC="+IZA
        #wget.download(url, out=IZA+".html")
        htmlContent=requests.get(url,verify=False)
        data = htmlContent.text

        chem_form_html=sed_for_ChemicalFormula(data)
        chem_form_text=sed_chemicalize_regex(chem_form_html)
        IZA_chem_form.append(chem_form_text)

        IZA_data.append(json.dumps({
            'url': str(url),
            'uid': str(IZA),
            #'page_content': HTMLtoJSONParser.to_json(htmlContent.text, raise_exception=False),
            'page_content': data,
            'chemical_formula':chem_form_text
            })
        )

    print(IZA_chem_form)

    return IZA_data, IZA_chem_form


def write_chem_form(IZA_list, IZA_chem_form):
    
    f=open("IZA_list_chem_form.txt","w")

    for i in range(len(IZA_list)):
        f.write("%s@%s\n"%(IZA_list[i], IZA_chem_form[i]))

    f.close()


if __name__=="__main__":
    
    IZA_file = sys.argv[1]
    IZA_list = get_structures(IZA_file)
    IZA_data, IZA_chem_form = extract_data(IZA_list)

    write_chem_form(IZA_list, IZA_chem_form) 
    

    
