
What is TRACY?
--------------

TRACY is a search engine for binary functions, implemented in Python.
Given a query, a function in binary form (as a part of an executable),
TRACY searches other executables, and produces a similarity score between the search target and the query.

A full explenation about TRACY can be found in my paper, found here - https://www.cs.technion.ac.il/~yanivd/


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
GetStats.py - generate stats for your db of samples
GraphletRewritter.py - what the name say
GraphletsCompareMyNG.py	- this file contains the functions needed to compare 2 code blocks
GraphletsConstraintsNG.py	- the wrapper for the constraint solver
IgraphHelper.py	- helper functions for dealing with gmls
SortedCollection.py	- helper class for printing csvs
colorGraphs.py - this implements the other method we compared our method with, graphlets
combinatorics.py	Last CLI enabled version.	2 months ago
extractFunctions.py	Last CLI enabled version.	2 months ago
findClonesCONS.py	- the main file (see previous explanation)
myutils.py	Last CLI enabled version.	2 months ago
ngrams.py - this implements the other method we compared our method with, n-grams
split2k.py - creates tracelets
x86Analyzer.py - analyse code for compare and dataflow analysis


