__author__ = 'thk22'
from argparse import ArgumentParser
from copy import copy
from glob import glob
import os

from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import bibtexparser

parser = ArgumentParser()
parser.add_argument('-ip', '--input-path', type=str, help='path to input file')
parser.add_argument('-o', '--output-file', type=str, help='output file')
parser.add_argument('-op', '--output-path', type=str, help='output path')
parser.add_argument('-e', '--extension', type=str, default='bib', help='extension of bib files')


if (__name__ == '__main__'):
	args = parser.parse_args()

	titles = set()
	keys = set()
	bib_entries = []
	for f in glob(os.path.join(args.input_path, '*.{}'.format(args.extension))):
		with open(f, 'r') as bibfile:
			bib = bibtexparser.load(bibfile)

			for e in bib.entries:
				if ('title' in e):
					if ('author' in e):
						if ('year' in e):
							t = e['title'].strip().lower()

							if (not t in titles):
								# Extract author 1 (and his/her last name)
								authors = e['author'].split(' and ')
								a1 = authors[0]
								if (',' in a1):
									a1 = a1.split(',')[0]
								else:
									a1 = a1.split()[-1]

								# Check that no funny characters are in the last name
								if ('\\' in a1 and '{' in a1):
									parts = a1.split('\\')
									a1 = parts[0] + parts[1][2:3] + parts[1][4:]
								elif (a1.startswith('{') and a1.endswith('}')):
									a1 = a1[1:-1]

								# Post-Clean
								a1 = a1.strip()
								if (' ' in a1):
									a1 = a1.replace(' ', '')
								if ('~' in a1):
									a1 = a1.replace('~', '')

								key = '_'.join([a1, e['year']])

								# Check if there already is an Author_Year combination
								c = 0
								for k in keys:
									if k.startswith(key):
										print('\tFound Match: {} -> {}'.format(k, key))
										c += 1
								if (c > 0):
									key += chr(ord(str(c)) + 0x30) # Hehehehe, everybody needs some dirty pleasures sometimes...

								keys.add(key)

								# Build new bib entry
								cleaned_entry = copy(e)
								cleaned_entry['ID'] = key

								bib_entries.append(cleaned_entry)
						else:
							print('[WARNING] - No year found in {}!'.format(e))
					else:
						print('[WARNING] - No author found in {}!'.format(e))
				else:
					print('[WARNING] - No title found in {}!'.format(e))

	print('Merged Bib Entries: {}'.format(len(bib_entries)))
	db = BibDatabase()
	db.entries = bib_entries

	writer = BibTexWriter()
	with open(os.path.join(args.output_path, args.output_file), 'w') as bibfile:
		bibfile.write(writer.write(db))

