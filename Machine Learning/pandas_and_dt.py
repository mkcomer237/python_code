

import pandas as pd 
import numpy as np 
from sklearn import cross_validation
from sklearn import tree 
from sklearn.externals.six import StringIO
import os
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn import ensemble
from inspect import getmembers 
#import pydot


def get_criteria(nodelist):
	criteria = ''
	#print nodelist
	for item in nodelist:

		try:
			feature = item[3]
			threshholder = item[2]
			split = item[1]
		except(IndexError):
			continue 

		if split == 'l': splitsymbol = '<='
		if split == 'r': splitsymbol = '>'
		node_crit = '(df[\'' + feature + '\'] ' + splitsymbol + ' ' + str(threshholder) + ') & '
		criteria += node_crit
	return criteria[:-3]


def get_lineage(tree, feature_names):
	left      = tree.tree_.children_left
	right     = tree.tree_.children_right
	threshold = tree.tree_.threshold
	features  = [feature_names[i] for i in tree.tree_.feature]

	# get ids of child nodes
	idx = np.argwhere(left == -1)[:,0]     

	def recurse(left, right, child, lineage=None):          
		if lineage is None:
			lineage = [child]
		if child in left:
			parent = np.where(left == child)[0].item()
			split = 'l'
		else:
			parent = np.where(right == child)[0].item()
			split = 'r'

		lineage.append([parent, split, threshold[parent], features[parent]])

		if parent == 0:
			lineage.reverse()
			return lineage
		else:
			return recurse(left, right, parent, lineage)

	return_criteria = []

	for child in idx:
		nodelist = []
		for node in recurse(left, right, child):
			#print node
			nodelist.append(node)
		#print nodelist

		criteria = get_criteria(nodelist)
		#print criteria
		return_criteria.append(criteria)

	return return_criteria


def print_resultset(features_test, labels_test, pred):
	combined_data = zip(features_test.tolist(), labels_test.tolist(), pred.tolist())

	#print features_test.tolist()

	outfile = open('predicted.txt', 'w')

	outfile.write('\t'.join(['relatives', 'birthyear', 'residence', 'gendernum','marriage', 'responsenum_actual', 'responsenum_pred']))
	outfile.write('\n')

	for line in combined_data:

		outlist = list(line)
		features = outlist[0]
		labels = outlist[1][0]
		pred_labels = outlist[2]
		outlist2=[]
		for value in features:
			outlist2.append(str(value))
		outlist2.append(str(labels))
		outlist2.append(str(pred_labels))
		#[0].extend(list(line)[2])
		#.extend(list(line)[1]).extend(list(line)[2])
		outfile.write('\t'.join(outlist2))
		outfile.write('\n')



def leaf_pct(criteria, df):

	outleaf = open('leaf_stats.txt', 'w')

	outleaf.write('\t'.join(['Conditions', 'Pct Connected', 'Leaf Size']))
	outleaf.write('\n')

	for conditions in criteria:
		
		code = 'subdf = df[' + conditions + ']'
		exec(code)
	
		outleaf.write('\t'.join([conditions, str(subdf['responsenum'].mean()), str(subdf['responsenum'].count())]))
		outleaf.write('\n')






def decision_tree(cleandata, use_variables, df, seed):

	features_train = cleandata[0]
	features_test = cleandata[1]
	labels_train = cleandata[2]
	labels_test = cleandata[3]


	clf = tree.DecisionTreeClassifier(min_samples_split= 15000, criterion='entropy', min_samples_leaf = 2000)
	#clf = ensemble.RandomForestClassifier(min_samples_split=10000, criterion='entropy', min_samples_leaf = 2000)

	#min samples split - how many observations left to keep splitting
	clf.fit(features_train, labels_train)

	pred = clf.predict(features_test)

	precision = precision_score(labels_test, pred)
	recall = recall_score(labels_test, pred)
	print "Precision is: ", precision
	print "Recall is: ", recall
	print "Accuracy Score is: ", accuracy_score(labels_test, pred)

	names = use_variables[1:]

	outfile = 'outtree' + str(seed) + '.dot'
	with open(outfile, 'w') as f:
		f = tree.export_graphviz(clf, out_file=f, feature_names=names)

	#print (getmembers(clf.tree_))
	#print clf.tree_.children_left
	#print clf.tree_.children_right
	#print clf.tree_.feature
	#print clf.tree_.threshold
	#print clf.tree_.value

	criteria = get_lineage(clf, names)

	leaf_pct(criteria, df)


	print_resultset(features_test, labels_test, pred)


#split into 4 arrays for training and validation 


def get_arrays(df, use_variables, seed):

	labels = df[['responsenum']].values

	features_df = df.drop(['responsenum'], axis=1)
	features = features_df.values

	features_train, features_test, labels_train, labels_test = cross_validation.train_test_split(features, labels, test_size=0.25, random_state=seed)

	print "labels length: ", len(labels_train), len(labels_test)
	print "features length: ", len(features_train), len(features_test)

	return [features_train, features_test, labels_train, labels_test]


def clean_data(fp):

	df = pd.read_csv(fp, header=0, sep='\t')

	grouped = df.groupby('gender').count()
	#print grouped[['gender', 'gid']]

	grouped = df.groupby('response').count()
	#print grouped[['response', 'gid']]


	df['gendernum'] = df['gender'].map({'m':1, 'f':0, 'u':0, 'M':1, 'F':0}).astype(int)
	df['responsenum'] = df['response'].map({'Yes':1, 'No':0, 'nothing':0}).astype(int)

	df['date1920'] = np.where(df['birthyear'] < 1920, 1, 0); df

	df['hasrelative'] = np.where(df['relatives'] > 0, 1, 0); df


	dummy_ranks = pd.get_dummies(df['birthregion'], prefix='region')
	df = df.join(dummy_ranks)
	#print df.head(10)

	df.to_csv('pandas_data.txt', sep='\t')


	full_varlist = ['responsenum', 'gendernum', 'relatives', 'birthyear', 'namecount', 'first', 'middle', 'last', 'eventsum','birth', 'residence', 'death', 'marriage', 'burial', 'arrival', 'military', 'occupation', 'divorce', 'date1920', 'region_west', 'region_south', 'region_midwest', 'region_non-us', 'region_northeast', 'hasrelative']
	use_variables = ['responsenum', 'gendernum', 'relatives', 'namecount', 'first', 'middle', 'last', 'eventsum', 'birth', 'residence', 'death', 'marriage', 'date1920', 'region_west', 'region_south', 'region_midwest', 'region_non-us', 'region_northeast']
	dup_variables = ['gid', 'gendernum', 'namecount', 'first', 'middle', 'last', 'eventsum', 'birth', 'residence', 'death', 'marriage', 'date1920', 'region_west', 'region_south', 'region_midwest', 'region_non-us', 'region_northeast']


	#print df.head(10)
	#print df.info()
	#print df.describe()
	#print df[df['responsenum'].isnull()][['response', 'responsenum']]


	#replace the dataframe 
	df = df[['gid'] + use_variables]

	#remove duplicate rows: 

	df = df.drop_duplicates(take_last=True, subset = dup_variables)
	df = df.drop(['gid'], axis=1)

	print df.info()
	print df[use_variables].describe()
	#print df.head(20)
	return [df, use_variables]


def main(): 

	fp = 'dataset_full_mobile_filtered2.txt'

	df = clean_data(fp)

	for seed in range(1,11): 
		cleandata = get_arrays(df[0], df[1], seed)
		decision_tree(cleandata, df[1], df[0], seed)

if __name__ == '__main__':
  main()



#  dot -Tpng outtree.dot -o treeview.png  --or--  dot -Tpng outtree.dot -o treeview.png


