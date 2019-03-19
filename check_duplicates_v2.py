import os
import pandas as pd
#import math

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
wos = pd.read_excel(files[2])
# Keep only colums of interest
wos = wos[['AU', 'TI', 'SO', 'DI', 'PY']]
# Rename Columns
wos.columns = ['Author List', 'Title', 'Journal', 'DOI', 'Year']
# Isolate WoS DOI for future duplicate analysis
wos_DOI = wos['DOI']

# Get data from PubMed
pbm = pd.read_csv(files[1], index_col=False)
# split data so as to have same format as in WoS
pbm['Journal'], pbm['Year'] = pbm['ShortDetails'].str.split('.', 1).str
# Keep only colums of interest
pbm = pbm[['Description', 'Title', 'Journal', 'Details', 'Year']]
# Rename Columns
pbm.columns = ['Author List', 'Title', 'Journal', 'DOI', 'Year']

# DOI in the pubmed database are mixed with other information
# So I need to isolate these DOI
# Isolate the column of interest
# Note that whatever happens to this copied column will happen to source column
pbm_DOI = pbm['DOI']

# Define function to find substring in a string
def find_substring(substring, string):
    """ 
    Returns list of indices where substring begins in string

    >>> find_substring('me', "The cat says meow, meow")
    [13, 19]
    """
    indices = []
    index = -1  # Begin at -1 so index + 1 is 0
    while True:
        # Find next index of substring, by starting search from index + 1
        index = string.find(substring, index + 1)
        if index == -1:  
            break  # All occurrences have been found
        indices.append(index)
    return indices

for iDOI in range(1,len(pbm_DOI)+1):
    # exclude characters before "doi"
    start_pos = pbm_DOI[iDOI-1].find('doi')    
    # If no DOI can be found, store a NaN
    if start_pos == -1:
        # enter NaN for missing DOI, and add the DOI number to avoid them being duplicates later on
        str_of_interest = 'NaN'+str(iDOI)
    else:
    # Eliminate the char before the actual DOI
        start_pos = start_pos + 5
        # store that in a temp array
        str_of_interest = pbm_DOI[iDOI-1][start_pos:len(pbm_DOI[iDOI-1])]
        # what comes after the DOI can be a space, a quote or nothing
        space_pos = find_substring(' ', str_of_interest)
        quote_pos = find_substring('"', str_of_interest)
        # depending what comes first, use that to exlude characters after DOI
        # If both quote and space are nowhere to be found, then just erase the last point
        if not (quote_pos + space_pos): 
               # lenght -1 to erase the last point
               select = len(str_of_interest)
               # transform to list to avoid conflict in following if loop
               #select = list(map(int, str(select)) )
               # reverse so as to get position correct
               #select = select[::-1]
        elif not quote_pos:
             select = space_pos[0]
        elif space_pos[0] < quote_pos[0]:
               select = space_pos[0]
        else:
               select = quote_pos[0]
    if str_of_interest == 'NaN':
        pbm_DOI[iDOI-1] = str_of_interest
    else:
        pbm_DOI[iDOI-1] = str_of_interest[0:select-1]   

# Before duplicate analysis, reorganize the pbm to fit wos format
# and only keep important information
# that is, 

# Now concatenate both series for comparison
DOI_concat = pd.concat([pbm_DOI,wos_DOI])
# and create an index of duplicates
DOI_concat_bool = pd.Series.duplicated(DOI_concat)   

# Find duplicates between the WoS and PubMed DOI
pos_duplicate = [i for i, x in enumerate(DOI_concat_bool) if x]
# Normalize the position of the duplicates by substracting the positions of pubmed DOI
# I substract 2 to account for the header and the starting position at 0
# pos_duplicate gives then the row numbers in the excel sheet that contains duplicates
pos_duplicate[:] = [i - (len(pbm_DOI) - 2) for i in pos_duplicate]

# Generate a list of DOI without duplicates
DOI_concat_no_dups = DOI_concat[~DOI_concat_bool]
# Generate a complete reference list without duplicates
ref_concat = pd.concat([pbm,wos])
ref_concat_no_dups = ref_concat[~DOI_concat_bool]

print("Number of duplicates is :", len(DOI_concat) - len(DOI_concat_no_dups))

# Output the no duplicate database 
# Note that we still have the missing DOI, we should use title to make sure they are not duplicated
ref_concat_no_dups.to_excel('search_pbm_wos_no_dups.xlsx', sheet_name='sheet1', index=False)






    