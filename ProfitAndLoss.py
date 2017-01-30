

################ TO DO #####################################
#
# Describe format of data files particularly the mapping file
# (the file needs to be sorted in order of priority
#
#
# Am I going to have to build in an overide for cases 
# where mapping does not work?  Maybe just a manual overide
# column in underlying data
#
# Need to rethink when I should use indices on dataframes
#
# Add below fields
#   (1) Total expense for month
#   (2) Prepayment




import pandas as pd


data_dir='/home/charl/Documents_Charl/010_EncryptForCloudBackup/Roll_Forward'\
        '/Roll_Forward_Data/'



def ReadData():


    # Set data frames with global scope to avoid passing between subs
    global df_transactions
    global df_mapping
    global df_expensedetails

    # Read transaction data into pandas dataframes 
    df_transactions = pd.read_csv(data_dir+ 'transactions.csv', dayfirst=True, \
            parse_dates=[1])
    df_mapping = pd.read_csv(data_dir+ 'mapping.csv')
    df_expensedetails = pd.read_csv(data_dir+ 'expense_details.csv')




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



# def TempStringContains():
#
#    StringContains = sum(df_transactions\
#            [df_transactions.Description.str.contains('EZI')]\
#            .Amount)
#
#    print (StringContains)


#def MapDescriptionToDisclosureOne(description):
#
#    #works but is pretty slow
#    for index, series  in df_mapping.iterrows():
#        if description in series['DescriptionContains']:
#            return (series['Disclosure'])
#
#    # if no matches found:
#    return ('Unmatched')



def MapDescriptionToExpenseAccount():

    
    for index, series in df_mapping.iterrows():

        df_transactions.loc[df_transactions['Description'].str.contains(\
               series['DescriptionContains']), 'ExpenseAccount'] = \
               series['ExpenseAccount']  

    # Replace any Nan values with Unmapped ('Nan' is not picked up in 
    # pivot tables.
    df_transactions['ExpenseAccount'] = df_transactions['ExpenseAccount']\
            .fillna('Unmapped')

   
   
   

def GetTransactionMonthEnd():

    df_transactions['MonthEnd'] = df_transactions['Date'] + \
            pd.offsets.MonthEnd(0) 




if __name__=='__main__':


    ReadData()
    
#    df_transactions['tempdisclosureOne'] = df_transactions['Description'].apply\
#            (MapDescriptionToDisclosureOne)

    MapDescriptionToExpenseAccount()
    GetTransactionMonthEnd()

    #TempStringContains()
    #TempSumIf()
    #TempTesting()

