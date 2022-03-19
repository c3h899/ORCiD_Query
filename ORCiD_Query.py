## Imports
from datetime import date
import json
import orcid
import pprint

## Methods
def get_api_obj(api_conf):
	api = None
	search_token = None
	with open(api_conf, "r") as infile:
		conf = json.load(infile)
		api = orcid.PublicAPI(conf['CID'], conf['PRIV'], sandbox=False)
		search_token = api.get_search_token_from_orcid()
	return ((api, search_token))
def get_user_list(users):
	Users = None
	# Import User List
	with open(users, "r") as infile:
		Users = json.load(infile)
	return Users
def gen_report(users, search_token):
	out_report = list()	
	for name, user_id in users:
		out_report.append(dict({
			'Name' : name,
			'ID' : user_id,
			'Works' : query_user_works(user_id, search_token)
		}))
	return out_report
def query_user_works(USER_ID, search_token):
	# Queries Specified ORCiD User_ID for list of Works
	# Returns Flattened Summary
	summary = api.read_record_public(USER_ID, 'works', search_token)['group']
	rec = list()
	for entry in summary:
		# Convenient Names
		external_id = None if not entry['external-ids']['external-id'] else entry['external-ids']['external-id'][0]
		work_summary = entry['work-summary'][0]
		# Resolve Publication Date
		pub_date = work_summary['publication-date']
		pub_year = int(1 if pub_date['year'] is None else pub_date['year']['value'])
		pub_month = int(1 if pub_date['month'] is None else pub_date['month']['value'])
		pub_day = int(1 if pub_date['day'] is None else pub_date['day']['value'])
		# (Optional) Publication URL
		try:
			pub_url = None
			pub_doi = None
			if (external_id is None):
				pub_url = None
			else:
				if (external_id['external-id-type'] == 'doi'):
					pub_doi = external_id['external-id-value']
				else:
					pub_doi = None
				if (external_id['external-id-url'] is None):
					pub_url = None
				else:
					pub_url = external_id['external-id-url']['value']
		except:
			pub_url = None
			#print(external_id)
		# Construct a flattened record
		temp_rec = dict({
			'doi' : pub_doi,
			'url' : pub_url,
			'source' : work_summary['source']['source-name']['value'],
			'title' : work_summary['title']['title']['value'],
			'type' : work_summary['type'],
			'publication-date' : str(date(pub_year, pub_month, pub_day))
		})
		rec.append(temp_rec)
	return rec

## Config
api_conf = "ORCiD_API.json"
user_conf = "ORCiD_Users.json"

## ORCiD Query
(api, search_token) = get_api_obj(api_conf)
user_list = get_user_list(user_conf)
Report = gen_report(user_list, search_token)

## Dump Records to JSON
with open("ORCiD_Summary.json", "w") as outfile:
    json.dump(Report, outfile)

