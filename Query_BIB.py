import bibtexparser
from datetime import date
import json
import pprint

bib_conf = "Bib_sources.json"

with open(bib_conf, "r") as infile:
	Bib_List = json.load(infile)

parser = bibtexparser.bparser.BibTexParser(common_strings=True)
parser.ignore_nonstandard_types = True
parser.homogenise_fields = False

def safe_read_dict(key, source):
	return None if key not in source else source[key]
def conv_bib_file(parser, fname, source_str):
	entry_list = list()
	with open(fname) as bib_file:
		bib_db = parser.parse_file(bib_file)
		for entry in bib_db.entries:
			log = False
			conv = dict()
			ent_type = entry['ENTRYTYPE']
			conv['doi'] = safe_read_dict('doi', entry)
			conv['url'] = safe_read_dict('url', entry)
			conv['source'] = Bib_List[0][0]
			conv['title'] = safe_read_dict('title', entry)
			# Typing
			if ent_type == 'article':
				conv['type'] = "JOURNAL_ARTICLE"
				log = True
			elif ent_type == 'inproceedings':
				conv['type'] = "CONFERENCE_PAPER"
				log = True
			else: conv['type'] = "MISC"
			# Continue Conversion
			conv['publication-date'] = safe_read_dict('year', entry)
			if log: entry_list.append(conv)
	return entry_list

summary = list()
for src_name, file_name in Bib_List:
	entry = {
		'Name' : src_name,
		'ID' : '0000-000X-XXXX-XXXXX',
		'Works' : conv_bib_file(parser, file_name, src_name)
	}
	summary.append(entry)

## Dump Records to JSON
with open("BIB_Summary.json", "w") as outfile:
    json.dump(summary, outfile)