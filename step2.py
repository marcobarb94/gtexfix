#!/usr/bin/env python
# python gtexfix/step2.py tex_files/
#-----------------------------------------
# Google translate fix for LaTeX documents
# Copyright (c) Dmitry R. Gulevich 2020
# GNU General Public License v3.0
#-----------------------------------------
"""
Sistemo in modo che io passi solo il prefix e lui mi tira su tutti i file con quel prefix

"""

import re
import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

# if(re.search('.txt$',args.filename)==None):
#     sys.exit('The input should be .txt file. Exit.')

print('Input file (original):',args.filename)

from glob import glob

files = glob(args.filename+"_*")

print("I found these files: ")
print(files)

#backup orginal file 
try:
    from os import rename
    rename(args.filename+"T9N.tex", args.filename+"T9N.tex.bak")
except:
    print("Backup file not found")

source = ""

for filename in files:
    ### Load LaTeX data from binary files
    with open(filename, 'r', encoding="utf8") as fin:
        source += fin.read()
# one for each file?
with open ('gtexfix_comments.json', 'r', encoding="utf8") as fp:
    comments = json.load(fp)
with open ('gtexfix_commands.json', 'r', encoding="utf8") as fp:
    commands = json.load(fp)
with open ('gtexfix_latex.json', 'r', encoding="utf8") as fp:
    latex = json.load(fp)

### Replace weird characters introduced by translation
trtext=re.sub('\u200B',' ',source)

### Fix spacing
trtext = re.sub(r'\\ ',r'\\',trtext)
trtext = re.sub(' ~ ','~',trtext)
trtext = re.sub(' {','{',trtext)
trtext = re.sub(' *]',']',trtext)

### Restore LaTeX and formulas
here=0
newtext=''
nl=0 # count of latex commands found
nc=0
corrupted=[]
for m in re.finditer('\[ *[012][\.\,][0-9]+\]',trtext):
    t=int(re.search('(?<=[\[ ])[012](?=[\.\,])',m.group()).group())
    n=int(re.search('(?<=[\.\,])[0-9]+(?=\])',m.group()).group()) # latex command ID (it should be equal to nl or nc - ECC)
    if(t==1):
        if(n<nl):
            print('Token ',m.group(),'found in place of [%d.%d]. Edit manually and run again.'%(t,nl))
            break
        while(nl!=n):
            corrupted.append('[%d.%d]'%(t,nl))
            nl+=1
        newtext += trtext[here:m.start()] + latex[n]
        nl+=1
    elif(t==2):
        if(n<nc):
            print('Token ',m.group(),'found in place of [%d.%d]. Edit manually and run again.'%(t,nc))
            break
        while(nc!=n):
            corrupted.append('[%d.%d]'%(t,nc))
            nc+=1
        newtext += trtext[here:m.start()] + commands['[2.{}]'.format(str(n))]
        nc+=1
    here=m.end()
newtext += trtext[here:]
trtext=newtext

# new part 3 - I can avoid ECC since this part is not translated. 
newtext = trtext
for m in re.finditer('\[ *[3][\.][0-9]+\]',trtext):
    n=int(re.search('(?<=[\.\,])[0-9]+(?=\])',m.group()).group())
    newtext = newtext.replace(m.group(),commands['[3.{}]'.format(str(n))]) # best without update every time. Using m.start() breaks all
trtext=newtext

### Restore comments
here=0
ncomment=0
newtext=''
for m in re.finditer('___GTEXFIXCOMMENT[0-9]*___',trtext):
    n=int( re.search('[0-9]+',m.group()).group() )
    if(n!=ncomment):
        print('Comment token ',m.group(),'is broken. Stopping.')
        continue
    newtext += trtext[here:m.start()] + comments[n]
    ncomment+=1
    here=m.end()
newtext += trtext[here:]
trtext=newtext

### pulizia

# togli la traduzione free: 
trtext = re.sub("Tradotto con www.DeepL.com/Translator (versione gratuita)",' ',trtext) # online
trtext = trtext.replace("*** Tradotto con www.DeepL.com/translator (versione gratuita) ***",' ') # app

trtext = re.sub('  ',' ',trtext) # remove double space
trtext = re.sub('  ',' ',trtext) # remove double space - another time
trtext = re.sub(' ~ ','~',trtext)
trtext = re.sub('\n\n\n','\n\n',trtext) # remove double new line
# add space before new sentence [re: ([a-zàèéùì])(\.)([A-Z])]
pre = re.compile("([a-zàèéùì\)\]])(\.)([A-ZÈ])")
trtext = pre.sub(r"\1\2 \3",trtext) # I have 3 groups, a space between group 2 (dot) and group 3
# add space before percentage
pre2 = re.compile(r"([0-9])(\\\%)")
trtext = pre2.sub(r"\1 \2",trtext) # I have 3 groups, a space between group 2 (dot) and group 3


### Save the processed output to .tex file - Why T9N? https://www.linkedin.com/pulse/difference-between-g11n-i18n-t9n-l10n-satish-singh
output_filename = args.filename+"T9N.tex"
with open(output_filename, 'w+', encoding="utf8") as translation_file:
    translation_file.write(trtext)
print('Output file:',output_filename)

### Report the corrupted tokens
if(corrupted==[]):
    print('No corrupted tokens. The translation is ready.')	
else:
    print('Corrupted tokens detected:',end=' ')
    for c in corrupted:
        print(c,end=' ')
    print()
    print('To improve the output manually change the corrupted tokens in file',filename,'and run from.py again.')
