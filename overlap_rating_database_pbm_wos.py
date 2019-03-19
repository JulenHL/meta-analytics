import os
import pandas as pd
#import numpy as np
import re

# Set path
work_dir = "C:\\Users\\hernandez\\Documents\\meta_temp"
os.chdir(work_dir)
# Verify the path
cwd = os.getcwd() 
# Print the current directory 
print("Current working directory is:", cwd) 

# List files in dir
files = os.listdir(os.curdir)
nFiles = len(files)
print("files in directory are:", files)

# Get data from Web of Science
database_correct = pd.read_excel(files[2])
# Add -1 column to fill the ratings from old database
# hence -1 will indicate rows that were not present in old database
# most likely studies from 2017&2018
database_correct.insert(loc=0, column='Ratings', value=1)
database_correct.loc[:,'Ratings'] *= -1
# Get data from old database's rating
database_ratings = pd.read_excel(files[5])
# Make a column to store rows that are found in new database

# This is the mask to get rid of special characters
pattern=re.compile("[^a-zA-Z\d\s]")
# Some titles have special characters, so I get rid of those in a new column
database_ratings['Corrected Titles'] = database_ratings['Title'].map(lambda x: re.sub(pattern, '', x))
# Lower case everything
database_ratings['Corrected Titles'] = database_ratings['Corrected Titles'].str.lower()
# I apply the same operation to the new database to make sure hits are found
database_correct['Corrected Titles'] = database_correct['Title'].map(lambda x: re.sub(pattern, '', x))
# Lower case everything
database_correct['Corrected Titles'] = database_correct['Corrected Titles'].str.lower()


papers_not_included = 0
# Fill the rating column in the new database
for i in range(1,len(database_ratings)-1):
    to_cross_ref = database_ratings['Corrected Titles'][i]   
    #to_cross_ref = re.escape(to_cross_ref)
    found_title_idx = database_correct['Corrected Titles'].str.contains(to_cross_ref)
    if found_title_idx.sum() == 0:
        papers_not_included = papers_not_included + 1   
    # Extract the position of the row in the old database    
    else: 
        found_title_pos = found_title_idx[found_title_idx].index[0]
        # Copy the rating of the old database for that row in the new database
        database_correct["Ratings"][found_title_pos] = database_ratings['rejection code'][i]

# Check
len(database_correct.index)-database_correct.count()
len(database_ratings.index)-database_ratings.count()
database_correct.groupby('Ratings').size()  
database_correct.to_excel('database_correct.xlsx', sheet_name='sheet1', index=False)     


idx_non_present = database_correct['Ratings'] == -1
database_to_check = database_correct[idx_non_present]

t2 = database_to_check['Year'] == 2018
t1 = database_to_check['Year'] == 2017
idx_papers_2017_2018 = t1+t2
idx_papers_2017_2018 = ~idx_papers_2017_2018

filtered = database_to_check[idx_papers_2017_2018]

idx_selected_ratings = database_ratings['rejection code'].isnull().values
t = sorted(database_ratings['Title'][idx_selected_ratings])

idx_selected_correct =  database_correct['Ratings'].isnull().values
t2 =sorted(database_correct['Title'][idx_selected_correct])

for i in range(1,len(t)):
    matching = [s for s in t2 if t[3] in s]
    
    

