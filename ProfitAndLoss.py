

################ TO DO #####################################
# where mapping does not work?  Maybe just a manual overide
# column in underlying data
#
# Describe format of data files particularly the mapping file
# (the file needs to be sorted in order of priority




import pandas as pd


data_dir='/home/charl/Documents_Charl/010_EncryptForCloudBackup/Roll_Forward'\
        '/Roll_Forward_Data/'



def ReadData():
    """Read data into globally scoped pandas dataframes"""

    # Set data frames with global scope to avoid passing between subs
    global df_transactions
    global df_mapping
    global df_expensedetails

    # Read transaction data into pandas dataframes 
    df_transactions = pd.read_csv(data_dir+ 'transactions.csv', dayfirst=True, \
            parse_dates=[1])
    df_mapping = pd.read_csv(data_dir+ 'mapping.csv', index_col=0)
    df_expensedetails = pd.read_csv(data_dir+ 'expense_details.csv', \
            index_col=0)




def TempGrouping():

    # TEMP 
    # df_temp = df_transactions.groupby(["Description"]).sum())
    #unq = df_transactions['Description'].unique()
    #print(unq)
    grp = df_transactions['Amount'].groupby(df_transactions['Description'])\
            .sum()
    print (grp)


def TempSumIf():

    str_to_match="EZIDEBIT HEALTHFIT MB    FORTITUDE VA"
  
    mysumif = sum(df_transactions[\
                    (df_transactions.Description == str_to_match ) & \
                    (df_transactions.Date == '2016/06/30')]\
                .Amount)

    print (mysumif) 


    # Alternative method commented out    
    #     mysumif = df_transactions.query("Description == '""EZIDEBIT HEALTHFIT MB    FORTITUDE VA""'")['Amount'].sum()




def MapDescriptionToExpenseAccount(description):
    """Map bank text transaction desciption to expense accounts"""

    for description_contains in df_mapping.index:
        if description_contains.upper() in description.upper():
            return df_mapping.loc[description_contains, 'ExpenseAccount']

    # if not matches found
    return ('Unmatched')


   

def GetTransactionMonthEnd():
    """Adds a month end date to the transactions panda dataframe"""

    df_transactions['MonthEnd'] = df_transactions['Date'] + \
            pd.offsets.MonthEnd(0) 




if __name__=='__main__':


    ReadData()
    
    GetTransactionMonthEnd()

    df_transactions['ExpenseAccount'] = df_transactions['Description'].apply\
            (MapDescriptionToExpenseAccount)

    
    #TempSumIf()

