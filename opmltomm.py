#!/usr/bin/python
# -*- coding: utf-8 -*-# opmltomm.py
# opmltomm.py version 2
#
# History
# V1 - original version uploaded to github
# V2 - handles utf-8 characters correctly
#      Thanks to Volker on Freeplane forums for code for this improvement

"""Copyright 2016 ADXSoft

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
# OPMLtoMM
Python script to convert OPML files to Freeplane/Freemind files

## Background
I'm a keen Freeplane user but use other mindmapping tools on my mobile devices.
Would be nice if Freeplane had a mobile app :-)

I set up this script to import opml files I send to my desktop Freeplane environment.

## Pre-requisites
This script assumes you have previously installed Python 2.7. 
(It has not been tested with Python 3)

## Installation
Simply download the zip file and unzip wherever you wish. 
Leave the folder structure as is so the unittests can be run correctly

## opmltomm.py
Before you run this script you MUST change the following lines to set up your input and output
file locations.

<pre>
# ==========================================================================
# =========== CHANGE THE FOLLOWING SETTINGS BEFORE YOU RUN THIS SCRIPT!!
# ==========================================================================
#
# Full path to the input .opml file
input_opml_file='YOURFULLPATH/YOURINPUTOPMLFILE.opml'

# Full path to the output .mm which can be imported into Freemind 1.x or FreePlane 1.5.x
output_mm_file='YOURFULLPATH/YOUROUTPUTMMFILE.opml.mm'

# ==========================================================================
# ==========================================================================
</pre>

## Running the script
Execute the script as follows from the terminal

<B>python opmltomm.py</B>

## Script operation

The script will import each 'outline' element in the opml file as a freeplane/freemind node. 
 
If the outline element contains an attribute named '_note' 
   this will be imported as a plain text node note 

   NOTE. Your original note is preserved if possible 
          i.e. the note data in the _note tag in the opml file
               has valid xml/html syntax
          
          If the note data is invalid xml/html then it is still added but
          the html symbols are escaped e.g. < becomes &lt;
          this avoids any confusion for the Freemind/Freeplane parsers
          which interpret the note
          
## unittests.py
Run this script to execute several test conversions from 
opml format to .mm files (Freeplane and Freemind format)
included are tests for 
- scrivener exported opml files with rich and plain text notes
- freeplane exported opml (freeplane does not export notes only nodes at this time)
- omnioutliner 3 opml with rich and plain text notes
- mindly opml with plain text notes

Execute the script as follows from the terminal

<B>python unittests.py</B>

Note. This script must be run in the folder you unzipped into during the installation step
which has the <B>TestData</B> folder expected by the unittests module
"""

# ==========================================================================
# =========== CHANGE THE FOLLOWING SETTINGS BEFORE YOU RUN THIS SCRIPT!!
# ==========================================================================
#
# Full path to the input .opml file
input_opml_file='/Users/adxsoft/opmltomm/TestData/fromsample.opml'

# Full path to the output .mm which can be imported into Freemind 1.x or FreePlane 1.5.x
output_mm_file='/Users/adxsoft/opmltomm/TestData/fromsample.mm'

# ==========================================================================
# ==========================================================================

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import iterparse
import sys, getopt
from HTMLParser import HTMLParser
import cgi
from xml.sax.saxutils import escape

class Opml2Mm:

    def __init__(self):
        self.nodetree = []          #tree that will contain the elements for the .mm output file 
        self.nodetree.append("")    #initialise tree
        self.previous_level = 0     #initialise depth control

    # def open(self, inputfile):
    #     """ get opml data and load into ElementTree tree """
    #     if inputfile.endswith('.opml'):
    #         try:
    #             # self.tree = ET.parse(inputfile)
    #             return self.tree
    #         except:
    #             print "Cannot open file "+inputfile+'\n' \
    #                   "File may not exist or file may not be a valid xml file\n" \
    #                   "\nUSAGE\n"
    #             closedown()

    def convert_to_mm(self, inputfile,outputfile):
        """write output .mm file"""

        # Create the tree self.mm and add the map element
        self.mm = ET.Element("map",version="1.5.9")
        
        depth = 0

        # Iterate through the opml file looking for 'outline' tags
        for (event, node) in iterparse(inputfile, ['start', 'end', 'start-ns', 'end-ns']):
            
            # end of outline tag encountered
            if event == 'end':
                if node.tag=='outline':
                    # drop back a level
                    depth -= 1
                
            # start of outline tag encountered
            if event == 'start' and node.tag=='outline':
                
                #bump the depth 
                depth += 1
                
                # get the outline tags text
                # may be in the node.text field or the text attribute
                if node.text==None or node.text.strip()=='':
                    try:
                        nodetext=node.attrib['text'].strip()
                    except:
                        nodetext=''
                else:
                    nodetext=node.text.strip()
                
                # log where we're at
                print depth*' ',depth,'Added',node.tag,'text => '+nodetext+''
                
                # if at new level create a node element
                if depth > self.previous_level:
                    self.nodetree.append("")
                    attributes={}
                    attributes['TEXT']=nodetext
                    self.nodetree[depth] = ET.SubElement(self.nodetree[depth-1], "node",attrib=attributes)
                    
                    # if theres a note in the 'outline' tag ie attribute with tag '_node'
                    # create the note element
                    try:
                        # obtain note
                        node_note=node.attrib['_note']
                        
                        # remove any non ascii characters to avoid unicode problems
                        # node_note=self.removeNonAscii(node_note)
                    except:
                        # couldn't get a note for this node so set blank
                        node_note=''
                        
                    #if we have a note then add the richcontent element Freemind and Freeplane expect
                    if node_note<>'':
                            try:                                
                                # create richnote tag with note details embedded 
                                attributes={}
                                attributes['TYPE']='DETAILS'
                                note_element='<html><head></head><body>'+ \
                                        node_note + \
                                    '</body></html>'
                                self.nodetree[depth] = ET.SubElement(self.nodetree[depth], "richcontent",attrib=attributes)                                
                                
                                # inserting the note into node tag
                                # if note contains html and it is valid note is added as html
                                # 
                                # however if ElementTree rejects note due to parsing errors
                                # such as badly formed html then the exception below will be 
                                # triggered and note is added with raw 'escaped' text
                                # for example <b> is &lt:b&gt;

                                self.nodetree[depth].append(ET.fromstring(note_element))  
                                
                                # log result
                                print depth*' ','++ Added Note',node_note
                            except:
                                # ElementTree could not parse the opml note in the current outline tag
                                # so no note is added
                                
                                # note data is invalid xml so add the note data as xml CDATA tag
                                print '!!Warning: Invalid data. Note added as raw character data\nNote data=',node_note
  
                                # unescape html characters to avoid clashes with Freemind/Freeplane parsers
                                node_note=HTMLParser.unescape.__func__(HTMLParser, node_note)
                                
                                # escape utf-8 characters
                                node_note=escape(node_note).encode('ascii', 'xmlcharrefreplace')

                                # remove any non ASCII characters from note
                                # node_note=self.removeNonAscii(node_note)

                                # wrap escaped note in CDATA tag
                                # note_element='<html><head></head><body>'+ \
                                #     '<![CDATA['+ \
                                #         node_note + \
                                #     ']]>' + \
                                #     '</body></html>'
                                # 
                                note_element='<html><head></head><body>'+ \
                                        node_note + \
                                    '</body></html>'
                     
                                self.nodetree[depth].append(ET.fromstring(note_element))  
                 
                else:
                    # finished at current level so jump back a level
                    self.previous_level = depth-1

            if event == 'start' and node.tag=='title':
                # log title found
                print 'Added tag ',node.tag,'==>',node.text
                
                # add title tag as the first node
                self.nodetree[0]=ET.SubElement(self.mm, "node", attrib={'TEXT':node.text})

        # get the output data
        tree = ET.ElementTree(self.mm)
        root=tree.getroot()
        outputdata=ET.tostring(root)
        # print outputdata
        
        # create the output .mm file
        f=open(outputfile,'w')
        f.write(self.removeNonAscii(outputdata))
        f.close()
        
        return

    def removeNonAscii(self,s): 
        return "".join(i for i in s if ord(i)<128) #this gem gets rid of unicode characters

def closedown():
    print __doc__
    quit()
def main():
    opml2mm = Opml2Mm()
    opml2mm.convert_to_mm(input_opml_file,output_mm_file)
    print output_mm_file + " created."

if __name__ == "__main__":
    main()
    
