#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# written by Wim Han

"""
* 1. GUI added
* 2. only convert UTF-8 plain text files (subtitle files) to chs & cht by using opencc@byvoid
* 3. run in Python 3 under windows 10, not ubuntu
* 4. download python 3:  https://www.python.org/downloads/
     open IDLE of Python 3 Shell (GUI), File->Open->choose this .py file->set cursor in the .py content and press F5 to run it 
* 5. windows 10使用opencc的方法之一:
下載 opencc-python-master -> click icon "Clone or download"
https://github.com/yichen0831/opencc-python
or
https://codeload.github.com/yichen0831/opencc-python/zip/master
解壓後放在一個folder裡，例如 C:/
如果放在別處，需要改動下列path:
sys.path.append("C:/opencc-python-master/opencc/")
"""


import os,sys
import shutil
from chardet.universaldetector import UniversalDetector
from tkinter import Tk
from tkinter.filedialog import askopenfilename

sys.path.append("C:/opencc-python-master/opencc/")  # pay attention => change the path for your environment!!!
from opencc import OpenCC

global inputPath, outputPath_cht, outputPath_chs, outputPath_utf8


# open a dialog window
Tk().withdraw()
FULLfilenames_listing = askopenfilename(title = "Select only UTF-8 file(s)",multiple=True)   # selected 1 or more file(s)

# get input path
if not FULLfilenames_listing:            # List is empty
    sys.exit(1)
else:
    path = FULLfilenames_listing[0]      # full path with file name
    inputPath = path[:path.rfind("/")]   # only path without file name
    os.chdir(inputPath)

# create 3 folders
outputPath_cht = inputPath+"/utf8-cht"
if not os.path.exists(outputPath_cht):
    os.makedirs(outputPath_cht)
else:
    deleteFiles = os.listdir(outputPath_cht)
    for item in deleteFiles:
        os.remove(os.path.join(outputPath_cht, item))
        
outputPath_chs = inputPath+"/utf8-chs"
if not os.path.exists(outputPath_chs):
    os.makedirs(outputPath_chs)
else:
    deleteFiles = os.listdir(outputPath_chs)
    for item in deleteFiles:
        os.remove(os.path.join(outputPath_chs, item))

outputPath_utf8 = inputPath+"/convert2utf8"
if not os.path.exists(outputPath_utf8):
    os.makedirs(outputPath_utf8)
else:
    deleteFiles = os.listdir(outputPath_utf8)
    for item in deleteFiles:
        os.remove(os.path.join(outputPath_utf8, item))


def detect_encoding(file_path):
    # Detect file encoding
    detector = UniversalDetector()
    detector.reset()
    with open(file_path, mode='rb') as f:
        for b in f:
            detector.feed(b)
            if detector.done: break
    detector.close()
    return detector.result

"""
### dictionaries

* `hk2s`: Traditional Chinese (Hong Kong standard) to Simplified Chinese
* `s2hk`: Simplified Chinese to Traditional Chinese (Hong Kong standard)
* `s2t`: Simplified Chinese to Traditional Chinese
* `s2tw`: Simplified Chinese to Traditional Chinese (Taiwan standard)
* `s2twp`: Simplified Chinese to Traditional Chinese (Taiwan standard, with phrases)
* `t2hk`: Traditional Chinese to Traditional Chinese (Hong Kong standard)
* `t2s`: Traditional Chinese to Simplified Chinese
* `t2tw`: Traditional Chinese to Traditional Chinese (Taiwan standard)
* `tw2s`: Traditional Chinese (Taiwan standard) to Simplified Chinese
* `tw2sp`: Traditional Chinese (Taiwan standard) to Simplified Chinese (with phrases)
"""



def convertFile(InputFileName1, result_T, result_S):
    cc_s2t = OpenCC('s2t')  # convert from Simplified Chinese to Traditional Chinese
    cc_t2s = OpenCC('t2s')  # convert from Traditional Chinese to Simplified Chinese

    # check inputfile encoding
    file_encoding = detect_encoding(inputPath + '/' + InputFileName1)
    file_encoding= str(file_encoding['encoding'])
    if "UTF-8" not in file_encoding:   # not an utf-8 file
        f = open(inputPath + '/' + InputFileName1, 'r', encoding=file_encoding)
        try:
            content= f.read()    # read the whole file
        except Exception:
            print(InputFileName1+ ": encoding =",file_encoding,"=> cannot convert to UTF-8")
            sys.exit(1)
        f.close()
        f = open(outputPath_utf8+ '/' +InputFileName1, 'w', encoding="utf-8")
        f.write(content)     # convert the file to utf-8
        f.close()
        if "ISO-8859-1" in file_encoding:   # ANSI
            print(InputFileName1+ ": encoding =",file_encoding,"=> cannot convert to UTF-8")

        file1 = open(outputPath_utf8 + '/' + InputFileName1,"r",encoding='utf8', errors="surrogateescape")
    else:
        file1 = open(inputPath + '/' + InputFileName1,"r",encoding='utf8', errors="surrogateescape")

    #file1 = open(inputPath + '/' +InputFileName1, 'r', encoding = 'utf-8', errors="surrogateescape")
    file2 = open(outputPath_cht + '/' +result_T, 'w', encoding = 'utf-8', errors="surrogateescape")
    file3 = open(outputPath_chs + '/' +result_S, 'w', encoding = 'utf-8', errors="surrogateescape")

    line = file1.readline()
    while line:
        line = line.replace("\n","")
        line = line.replace("\r","")
        line = line + "\n"                   # newline for MS windows

        line2 = cc_s2t.convert(line)         # convert chs to cht
        file2.write(line2)

        line3 = cc_t2s.convert(line)         # convert cht to chs
        file3.write(line3)

        line = file1.readline()
    file1.close()
    file2.close()
    file3.close()

    print(InputFileName1 + " -> convert to cht & chs")


FileNames = []
for f in FULLfilenames_listing:
    name = f[f.rfind("/")+1:]
    FileNames.append(name.split(','))
    InputFileName = name
    if os.path.isdir(InputFileName):
        pass
    else:
        if InputFileName.lower().find(".cht.") > 0:     # replace ".cht." to ".chs."
            result_T = InputFileName
            result_S = InputFileName[0:(InputFileName.lower().find(".cht."))]+".chs."+InputFileName[(InputFileName.lower().find(".cht."))+5:]
        elif InputFileName.lower().find(".chs.") > 0:   # replace ".chs." to ".cht."
            result_T = InputFileName[0:(InputFileName.lower().find(".chs."))]+".cht."+InputFileName[(InputFileName.lower().find(".chs."))+5:]
            result_S = InputFileName
        else:
            result_T = InputFileName
            result_S = InputFileName

        convertFile(InputFileName,result_T,result_S)

FileNames.clear()


# delete outputPath_utf8
outputPath_utf8 = inputPath+"/convert2utf8"
if os.path.exists(outputPath_utf8):
    deleteFiles = os.listdir(outputPath_utf8)
    for item in deleteFiles:
        os.remove(os.path.join(outputPath_utf8, item))
    shutil.rmtree(outputPath_utf8)  # delete
