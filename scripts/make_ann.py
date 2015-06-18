#!/usr/bin/env python3 
"""
make_ann.py: 
	Takes in a list of papers generated by pubcrawl and formats them with the annotation format.

"""

from modules import paperparse as pp
import argparse
import os

"""
Paper():
	Class representation of a single paper. Contains the title, abstract, and their respective stemmed and tokenized forms
"""
class Paper():
	def __init__(self, pmid, title, abstract,  spSet = {}):
		self.spSet = spSet
		self.pmid = pmid
		self.title = title
		self.abstract = abstract

	def export(self):
		print("-------PAPER--------")
		print(self.spSet)
		print(self.title)
		print(self.abstract)
		print("-------PAPER--------")

	def writeAnn(self, path):
		with open(path, 'a') as f:
			f.write('> PMID == ' + self.pmid + '\n')
			f.write("TI == " + self.title + '\n')
			f.write("AB == " + self.abstract + '\n')
			f.write("TIHIT == \n")
			f.write("ABHIT == \n")


"""
Pair():
	Class contained of paper objects for all papers for a species pair. 
	Takes in a filePath to a set of line-separated, initalizer-tagged papers
	from that pair and packages them into Paper() objects

	paperSplit:
		takes a list of papers and converts them into a list of (Title, abstract) tuples. Currently discards any anomalous data
		TODO: Implement logging of discarded data
"""
class Pair():
	def __init__(self, filePath):
		#initalize the species sets
		sja, sjb = pp.getNames(filePath)[0], pp.getNames(filePath)[1]
		self.spSet1 = set(sja)
		self.spSet2 = set(sjb)
		self.spSet = self.spSet1.union(self.spSet2)

		#Load the papers
		self.rawPapers = pp.loadFile(filePath)
		self.papers = [Paper(pmid, title, abstract, self.spSet) for pmid, title, abstract in self.paperSplit(self.rawPapers) ]

	#Splits the papers into (Title, Abstract) 2-tuples
	def paperSplit(self, paperList):
		#Handle Missing Dat ahere
		holder, res = [], []
		for i in paperList:
			if i[:4] == "PMID" or i[:4] == "pmid":
				if holder == []:
					holder.append(pp.tagStrip(i))
				elif len(holder) != 3:
					print("Warning: Erronous data detected")
					print(holder)
					print(i)
					holder = [pp.tagStrip(i)]
				else:
					res.append(holder)
					holder = [pp.tagStrip(i)]
			else:
				holder.append(pp.tagStrip(i))
		if len(holder) == 0:
			pass
		elif len(holder) != 3:
			print("Warning2: Erronous data detected")
			print(holder)
		else:
			res.append(holder)
		return res

	def writeAnn(self, path):
		print("Writing annotations to: ", path)
		with open(path, 'w') as f:
			f.write("@BEGIN::SUMMARY\n")
			f.write("INTERACTS == \n")
			f.write("POSITIVE == \n")
			f.write("NEGATIVE == \n")
			f.write("@BEGIN::ABSTRACTS\n")
		for paper in self.papers:
			paper.writeAnn(path)

def execute(filePath, outDir = "output/ann_format/", terms = 'PMID:TI:AB'):
	if not os.path.exists(outDir):
		os.makedirs(outDir)
	outFile = os.path.basename(filePath)
	outFile = os.path.splitext(outFile)[0] + '.sp'
	print(outFile)
	papers = Pair(filePath)
	papers.writeAnn(outDir + outFile)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("target", help= "Path to pubcrawl output file")
	parser.add_argument("-o", "--outDir", help= "Directory to output data to")
	args = parser.parse_args()
	
	outDir = "output/ann_format/"
	if args.outDir:
		outDir = args.outDir
		execute(args.target, outDir)
	