## import file with med info --> add columns for ATC class --> save as new file
## 
## 1. read in file
## 2. look up ATC codes (for EACH hierarchy level)
## 3. look up NAMES for the ATC codes (for EACH hierarchy level)
## 4. save new files
##
##

import os
import sys
import pandas as pd
import numpy as np
sys.path.append('../data-preprocess/')
import queryRxNorm as qrx
import json

############################################################

l_all_med_files = ['./sample_data.csv']

col_idx_drug_indicator = 11
col_idx_med_name = 3
col_idx_reason_name = 7

## load json file for atc Hierarchy
file_hier_atc = '../data-preprocess/data/atcHierDict.json'
with open(file_hier_atc) as infile:
	d_hier_atc = json.load(infile)
file_atc_code_name = '../data-preprocess/data/atcDict.json'
with open(file_atc_code_name) as infile:
	d_atc_code_name = json.load(infile)

## master list of all meds
l_med_all = []
## load original data file, grab all med names
for filename in l_all_med_files:
	df_this_med_file = pd.read_csv(filename, header = None)
	### filter out just drugs
	df_this_med_file = df_this_med_file[df_this_med_file[col_idx_drug_indicator]=='D']
	## make list of all medications
	l_meds = list(df_this_med_file[col_idx_med_name])
	l_med_all = l_med_all + l_meds

l_unique_med = np.unique(l_med_all)

d_medName_atcL2name = dict()
d_medName_atcL3name = dict()
l_medName_no_ATC = []

print "num meds: " + str(len(l_unique_med))
for idx in range(len(l_unique_med)):
	if np.mod(idx, 5) == 0:
		print idx
	med_name = l_unique_med[idx]
	s_rxcui = qrx.get_rxcui(med_name)
	l_atc_cat = qrx.rxcui_to_category(s_rxcui, relaSource="ATC")
	if len(l_atc_cat) > 0: #IF THERES A HIT
		first_code = l_atc_cat[0]
		atc_cat_L2 = d_hier_atc[first_code]["L2"]
		atc_cat_L3 = d_hier_atc[first_code]["L3"]
		name_atc_cat_L2 = d_atc_code_name[atc_cat_L2]
		name_atc_cat_L3 = d_atc_code_name[atc_cat_L3]
		# store in new dict RAW_DATAFILE_NAME => ATC NAME
		d_medName_atcL2name[med_name] = name_atc_cat_L2
		d_medName_atcL3name[med_name] = name_atc_cat_L3
	elif len(med_name.split(' ')) > 1: #try to use just the first word
		med_name_mod = med_name.split(' ')[0]
		print med_name
		print med_name_mod
		s_rxcui = qrx.get_rxcui(med_name_mod)
		l_atc_cat = qrx.rxcui_to_category(s_rxcui, relaSource="ATC")
		if len(l_atc_cat) > 0: #IF THERES A HIT
			first_code = l_atc_cat[0]
			atc_cat_L2 = d_hier_atc[first_code]["L2"]
			atc_cat_L3 = d_hier_atc[first_code]["L3"]
			name_atc_cat_L2 = d_atc_code_name[atc_cat_L2]
			name_atc_cat_L3 = d_atc_code_name[atc_cat_L3]
			# store in new dict RAW_DATAFILE_NAME => ATC NAME
			d_medName_atcL2name[med_name] = name_atc_cat_L2
			d_medName_atcL3name[med_name] = name_atc_cat_L3
		elif '(' in med_name and ')' in med_name: ## if there are parenthesis in the name
			med_name_mod = med_name.split(')')[0].split('(')[-1]
			print med_name
			print med_name_mod
			s_rxcui = qrx.get_rxcui(med_name_mod)
			l_atc_cat = qrx.rxcui_to_category(s_rxcui, relaSource="ATC")
			if len(l_atc_cat) > 0: #IF THERES A HIT
				first_code = l_atc_cat[0]
				atc_cat_L2 = d_hier_atc[first_code]["L2"]
				atc_cat_L3 = d_hier_atc[first_code]["L3"]
				name_atc_cat_L2 = d_atc_code_name[atc_cat_L2]
				name_atc_cat_L3 = d_atc_code_name[atc_cat_L3]
				# store in new dict RAW_DATAFILE_NAME => ATC NAME
				d_medName_atcL2name[med_name] = name_atc_cat_L2
				d_medName_atcL3name[med_name] = name_atc_cat_L3
		elif '/' in med_name: ## if there is a slash in the name
			med_name_mod = med_name.split('/')[0].split(' ')[-1]
			print med_name
			print med_name_mod
			s_rxcui = qrx.get_rxcui(med_name_mod)
			l_atc_cat = qrx.rxcui_to_category(s_rxcui, relaSource="ATC")
			if len(l_atc_cat) > 0: #IF THERES A HIT
				first_code = l_atc_cat[0]
				atc_cat_L2 = d_hier_atc[first_code]["L2"]
				atc_cat_L3 = d_hier_atc[first_code]["L3"]
				name_atc_cat_L2 = d_atc_code_name[atc_cat_L2]
				name_atc_cat_L3 = d_atc_code_name[atc_cat_L3]
				# store in new dict RAW_DATAFILE_NAME => ATC NAME
				d_medName_atcL2name[med_name] = name_atc_cat_L2
				d_medName_atcL3name[med_name] = name_atc_cat_L3
		else: #IF NO HIT WITH FIRST WORD, word inside parenthesis, or first part of slash
			l_medName_no_ATC.append(med_name)
	else: #IF medname is only one word  and there was no hit, then theres no hit
		l_medName_no_ATC.append(med_name)

## for the datafiles, append the ATC classifications, save updated files
for filename in l_all_med_files:
	df_this_med_file = pd.read_csv(filename, header = None)
	### filter out just the drugs
	df_this_med_file = df_this_med_file[df_this_med_file[col_idx_drug_indicator]=='D']
	### append the ATC names
	l_meds = list(df_this_med_file[col_idx_med_name])
	l_atc_l2 = [d_medName_atcL2name[x] if x in d_medName_atcL2name else np.nan for x in l_meds]
	l_atc_l3 = [d_medName_atcL3name[x] if x in d_medName_atcL3name else np.nan for x in l_meds]
	df_this_med_file_to_save = df_this_med_file[[0,col_idx_reason_name, col_idx_med_name]]
	df_this_med_file_to_save['L2'] = l_atc_l2
	df_this_med_file_to_save['L3'] = l_atc_l3
	save_filename = filename.split('.csv')[0] + '_mappedATC.csv'
	df_this_med_file_to_save.to_csv(save_filename, index = False, header = False)


## save dictionaries
with open('d_ATC_L2.json', 'w'):
	json.dump(d_medName_atcL2name)
with open('d_ATC_L3.json', 'w'):
	json.dump(d_medName_atcL3name)
df_mednames_no_hit = pd.DataFrame([])
df_mednames_no_hit[0] = l_medName_no_ATC
df_mednames_no_hit.to_csv('df_mednames_no_ATC.csv', header = False, index = False)




