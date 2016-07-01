
What is TRACY?
--------------

TRACY is a search engine for binary functions, implemented in Python.
Given a query, a function in binary form (as a part of an executable),
TRACY searches other executables, and produces a similarity score between the search target and the query.

A full explenation about TRACY can be found in our paper, found here - https://www.cs.technion.ac.il/~yanivd/

** NEW ** - If you found this interesting, check our latest work @ http://www.binsim.com


Running the code
--------------
The version of TRACY found in this repository is the last CLI version used during our work, 
which will enable anyone to try it without complex setup, but will require some work.

It should be clearly said that this code comes without any guarantee 

The main file to run is 'findClonesCONS.py'
To run it successfully you will need python 2.7, and a number of other publicly avilavle libs (pip is your friend)
Then, you will need to change the source and target dirs pointed in the file.
Note the structure of the dirs needed, and that all files must be gmls.
To create gmls from elf or exe files use the 'extractFunctions.py' with IDA pro (tested 6.4)

what does each file do?
-----------------------
GetStats.py - generate stats for your db of samples <br>
GraphletRewritter.py - what the name say  <br>
GraphletsCompareMyNG.py	- this file contains the functions needed to compare 2 code blocks <br>
GraphletsConstraintsNG.py	- the wrapper for the constraint solver <br>
IgraphHelper.py	- helper functions for dealing with gmls <br>
SortedCollection.py	- helper class for printing csvs <br>
colorGraphs.py - this implements the other method we compared our method with, graphlets <br>
combinatorics.py	Last CLI enabled version.<br>
extractFunctions.py	Last CLI enabled version. <br>
findClonesCONS.py	- the main file (see previous explanation) <br>
myutils.py -	multiple helper functions	 <br>
ngrams.py - this implements the other method we compared our method with, n-grams  <br>
split2k.py - creates tracelets <br>
x86Analyzer.py - analyse code for compare and dataflow analysis <br>


