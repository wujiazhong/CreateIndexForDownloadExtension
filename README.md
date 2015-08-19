# CreateIndexForDownloadExtension
This script used to create index for download extension.

INTRODUCTION:
	Usage: CreateIndexForDownloadExtension [options] arg1 arg2 arg3
	Options:
		-h, --help			show help message and exit  
		-s, --spedir        Directory to save spe.
		-o, --output        Choose a dir to save index file.
		-p, --product       Choose index for which product: 1. SPSS Modeler 2. SPSS Statistics. //Currently there are only two products name here.

HOW TO USE:
1. input in Windows cmd:
	python CreateIndexForDownloadExtension.py -s C:\spe -o C:\index -p "SPSS Statistics"

2. Tips:
	Please use quotation marks ("") on product name.