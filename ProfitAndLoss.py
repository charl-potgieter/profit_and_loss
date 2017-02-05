

################ TO DO #####################################
#
# 
# 
# 
#
#
# where mapping does not work?  Maybe just a manual overide
# column in underlying data
#
# Describe format of data files particularly the mapping file
# (the file needs to be sorted in order of priority




import pandas as pd
import numpy as np


data_dir='/home/charl/Documents_Charl/010_EncryptForCloudBackup/Roll_Forward'\
        '/Roll_Forward_Data/'





def TempSumIf():

    str_to_match="EZIDEBIT HEALTHFIT MB    FORTITUDE VA"
  
    mysumif = sum(df_trx[\
                    (df_trx.Description == str_to_match ) & \
                    (df_trx.Date == '2016/06/30')]\
                .Amount)

    print (mysumif) 





def MapDescriptionToExpenseAccount(description):
    """Map bank text transaction desciption to expense accounts"""

    for description_contains in df_mapping.index:
        if description_contains.upper() in description.upper():
            return df_mapping.loc[description_contains, 'ExpenseAccount']

    # if not matches found
    return ('Unmatched')



def ExpenseForMonth(row):
    """ Return expense for the month.   Row is a pandas dataframe row
    passed to this funtion as a series"""

    if row['IsPrepayment'] == False:
        return(row['Amount'])
    else:
        return ('TBA')
    



if __name__=='__main__':


    # Read transaction data and mapping tables into pandas dataframes 
    df_trx = pd.read_csv(data_dir+ 'transactions.csv', dayfirst=True, \
            parse_dates=[1])
    df_mapping = pd.read_csv(data_dir+ 'mapping.csv', index_col=0)
    df_expensedetails = pd.read_csv(data_dir+ 'expense_details.csv', \
            index_col=0)


    # Add a month end date into the transaction dataframe
    df_trx['MonthEnd'] = df_trx['Date'] + \
            pd.offsets.MonthEnd(0) 


    # Add in the mapped expense account
    df_trx['ExpenseAccount'] = df_trx['Description'].apply\
            (MapDescriptionToExpenseAccount)

    # Merge transaction with expense account details (e.g. amortisation period)
    # Note use of fillna to prevent this data being dropped in pivot_table
    df_trx = pd.merge(df_trx, df_expensedetails, how='left', right_index=True,\
            left_on='ExpenseAccount').fillna("[NULL]")


    # Create a summary version
    df_trx_summary = df_trx.pivot_table\
            (index=['MonthEnd', 'ExpenseAccount', 'ExpenseGroup',\
                    'IsPrepayment', 'AmortisationMonths',\
                    'LastAmortisationMonthEnd', 'StartingCost'],\
            values='Amount',\
            aggfunc=np.sum)

    # Move the index to columns.  Can't seem to get this to work directly
    # in pivot_table command above
    df_trx_summary = df_trx_summary.reset_index()

    
    # Write expense impact to dataframe
    df_trx_summary['PandL'] = df_trx_summary.apply(ExpenseForMonth, axis=1)


    # Export summary
    df_trx_summary.to_csv(data_dir + 'transactions_summary.csv')
