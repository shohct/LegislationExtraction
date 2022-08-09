# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 22:13:15 2022

@author: shohct
"""

from lxml import etree
import pandas as pd

# =============================================================================
# MVA Fines
# =============================================================================

# URL = https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/89_97_04/xml
file = r'C:\Users\000276194\Documents\Working Codes\MVA\MVA_VT2022.xml'
doc = etree.parse(file)
root = doc.getroot()

# Strip all inline tags as it won't be extracted out of text
etree.strip_tags(doc,'{http://www.qp.gov.bc.ca/2013/inline}br')
etree.strip_tags(doc, '{http://www.qp.gov.bc.ca/2013/inline}strong')
etree.strip_tags(doc, '{http://www.qp.gov.bc.ca/2013/inline}hr')
etree.strip_tags(doc, '{http://www.qp.gov.bc.ca/2013/inline}doc')

tablerows = []

for child in root.findall('.//{http://docs.oasis-open.org/ns/oasis-exchange/table}tbody/*'):
    s = []
    for elem in child.iter():
        if elem.tag == '{http://docs.oasis-open.org/ns/oasis-exchange/table}line':
            s.append(elem.text)
    tablerows.append(s)
    
mvavt = pd.DataFrame(tablerows)
mvavt.columns = ['provision', 'contravention', 'fine', 'reducedFine', 'victimLevySurcharge', 'ticketedAmount', 'reducedTicketedAmount']

# Split between MVA, Electric Scooter, and MVA Reg
scooterrow = mvavt[mvavt['provision'].astype(str).str.startswith('Electric Kick Scooter')].index[0]
mvaregrow = mvavt[mvavt['provision'].astype(str).str.startswith('Motor Vehicle Act Regulations, B.C. Reg.')].index[0]

# MVA Regulations
mvareg = mvavt.iloc[mvaregrow:]

# Scooter
scooter = mvavt.iloc[scooterrow:mvaregrow]

# MVA
mvavt = mvavt.iloc[:scooterrow]

# Drop empty rows
mvavt = mvavt.dropna(subset=['reducedTicketedAmount'])
mvareg = mvareg.dropna(subset=['reducedTicketedAmount'])
scooter = scooter.dropna(subset=['reducedTicketedAmount'])

# Add source
mvavt['source'] = 'Motor Vehicle Act'
mvareg['source'] = 'Motor Vehicle Act Regulations'
scooter['source'] = 'Electric Kick Scooter Pilot Project Regulation'

mvavt = pd.concat([mvavt, mvareg, scooter])

mvavt = mvavt.reset_index(drop = True)

# Add Provision to Plus addendum line
rownum = mvavt[mvavt['contravention'].astype(str).str.startswith('plus an additional penalty')].index[0]
mvavt.at[rownum, 'provision'] = mvavt.at[rownum-1, 'provision']

# Temporarily exclude Provision for Section 831.1
mvavt = mvavt[~mvavt['provision'].str.startswith('section 83.1 ')]

# Dummy text
import numpy as np
mvavt['sectionText'] = 'If a highway has been divided into 2 roadways by a physical barrier or clearly indicated dividing section constructed so that it impedes vehicular traffic, a driver must not'


mvavt['sectionSubsection'] = np.where(mvavt['provision'].str.contains('\('), 
                                 'A person commits an offence if the person drives, operates, parks or is in charge of a motor vehicle or trailer on a highway',
                                 None)


mvavt['sectionParagraph'] = np.where(mvavt['provision'].str.contains('\([1-9]*\) \([a-z]\)'), 
                                      'without the licence required by this Act for the operation of that motor vehicle or trailer having been first obtained and being then in force,', 
                                      None)

mvavt['sectionSubparagraph'] = np.where(mvavt['provision'].str.contains('\([1-9]*\) \([a-z]\) \(i*\)'), 
                                      'that the officer, constable or inspector finds detached from a motor vehicle or trailer or displayed on a motor vehicle or trailer other than the one for which it was issued, or', 
                                      None)

# Export
mvavt.to_json(r'C:\Users\000276194\Desktop\mvavt_index.json', orient='index')

# Add index
mvavt = mvavt.reset_index()

# Export
mvavt.to_json(r'C:\Users\000276194\Desktop\mvavt_records.json', orient='records')

# =============================================================================
# MVA
# =============================================================================

file = r'C:\Users\shohct\Documents\Work\Criminal Code\MVA.xml'

doc = etree.parse(file)
root = doc.getroot()

# Strip all inline tags as it won't be extracted out of text
etree.strip_tags(doc,'{http://www.qp.gov.bc.ca/2013/inline}doc')
etree.strip_tags(doc, '{http://www.qp.gov.bc.ca/2013/inline}term')
etree.strip_tags(doc, '{http://www.qp.gov.bc.ca/2013/inline}abrUnderline')

tablerows = []

d = [elem.tag for elem in root.iter()]

d = []

for child in root.findall('.//{http://www.gov.bc.ca/2013/bclegislation}section/*'):
    d.append([elem.tag for elem in child.iter() if elem is not child])

ctag = []
etag = []
eatt = []
estr = []

#
for child in root.findall('.//{http://www.gov.bc.ca/2013/bclegislation}section/*'):
    if child.tag == '{http://www.gov.bc.ca/2013/bclegislation}num':
        section = child.text
    
    if child.tag == '{http://www.gov.bc.ca/2013/bclegislation}subsection':
        for elem in child.iter():
            print(section, elem.tag, elem.text)
            if elem.tag == '{http://www.gov.bc.ca/2013/bclegislation}num':
                subsection = elem.text
            print(section, subsection, elem.text)
    
    print(child[0])
    
    for elem in child.iter():
        print(child.text, elem.text)
        
    for elem in child.iter():
        ctag.append(child.tag)
        etag.append(elem.tag)
        eatt.append(elem.attrib)
        estr.append(elem.text)
        
mvadf = pd.DataFrame({'ctag':ctag,
                      'etag':etag,
                      'estr':estr})


# Marginal note & section 
mva_mn = []
mva_sec = []

for child in root.findall('.//{http://www.gov.bc.ca/2013/bclegislation}section/*'):
    if child.tag == '{http://www.gov.bc.ca/2013/bclegislation}marginalnote':
        mva_mn.append(child.text)
    if child.tag == '{http://www.gov.bc.ca/2013/bclegislation}num':
        section = child.text
        mva_sec.append(section)
        
testdf = pd.DataFrame({'MarginalNote':mva_mn, 'Section':mva_sec})

# Number of subsections within sections
length = []
lengthtag = []
lengthstr = []
for child in root.findall('.//{http://www.gov.bc.ca/2013/bclegislation}part/*'):
    length.append(len(child))
    lengthtag.append(child.tag)
    lengthstr.append(child.text)

lengthdf = pd.DataFrame({'Tag':lengthtag, 'Text':lengthstr, 'Length':length})

# Number of elements within subsection
slength = []
slengthtag = []
slengthstr = []
for child in root.findall('.//{http://www.gov.bc.ca/2013/bclegislation}section/*'):
    slength.append(len(child))
    slengthtag.append(child.tag)
    slengthstr.append(child.text)

slengthdf = pd.DataFrame({'Tag':slengthtag, 'Text':slengthstr, 'Length':slength})

# itertext function
itertag = []
for child in root.findall('.//{http://www.gov.bc.ca/2013/bclegislation}section/*'):
    itertag.append(' '.join(child.itertext()))

# preceding test
subtag=[]
sube =[]
subet = []
for child in root.findall('.//{http://www.gov.bc.ca/2013/bclegislation}section/*'):
    for elem in child.iter():
        if elem.tag == '{http://www.gov.bc.ca/2013/bclegislation}text':
            subelem = elem.getprevious()
            if subelem is not None:
                subtag.append(subelem.tag)
                sube.append(subelem.text)
                subet.append(elem.text)
                
                print(subelem.tag, subelem.text, elem.text)
            

testdf = pd.DataFrame({'parenttag':subtag, 'parenttext':sube, 'childtext':subet})


    
    for elem in child.iter():
        print(elem.tag, elem.text)
        if elem.tag == '{http://www.gov.bc.ca/2013/bclegislation}paragraph':
            d = elem.getparent()
            print(d.tag, d.text, elem.tag, elem.text)
    slength.append(len(child))
    slengthtag.append(child.tag)
    slengthstr.append(child.text)



    
    if child.tag == '{http://www.gov.bc.ca/2013/bclegislation}num':
        section = child.text
    
    print(child.tag, len(child))
    
    
    # Within subsection
    if child.tag == '{http://www.gov.bc.ca/2013/bclegislation}subsection':
        print()
    
    if child.tag == '{http://www.gov.bc.ca/2013/bclegislation}subsection':
        for elem in child.iter():
            print(section, elem.tag, elem.text)
            if elem.tag == '{http://www.gov.bc.ca/2013/bclegislation}num':
                subsection = elem.text
            print(section, subsection, elem.text)