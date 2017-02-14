

################ TO DO #####################################
#
#
# Add below columns to df_trx_summary
#    - Amortisation
#    - True_up_down
#    - P&L
#    - opening accrual or prepayment
#    - closing accrual or prepayment
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




def MapDescriptionToExpenseAccount(row):
    """Map bank text transaction desciption to expense accounts"""
    
    for description_contains in df_mapping.index:
        if description_contains.upper() in row['Description']:
            return(df_mapping.loc[description_contains]['ExpenseAccount'])
   
   # if not matches found
    return ('Unmatched')




def PreviousMonthPaid(row):
    """Return the previous month paid for given ExpenseAccount"""

    series_EarlierPaymentMonths = df_trx[
                        (df_trx['MonthEnd'] < row['MonthEnd']) & \
                        (df_trx['ExpenseAccount'] == row['ExpenseAccount']) & \
                        (df_trx['Amount'] != 0)
                                        ]\
                                        ['MonthEnd']

    if series_EarlierPaymentMonths.empty == False:
        return (max(series_EarlierPaymentMonths))
    elif row['ExpenseAccount'] in df_expensedetails.index:
        return (df_expensedetails.loc[row['ExpenseAccount']]\
                ['OpeningPaymentMonthEnd'])
    else:
        return np.NaN




def PreviousAmountPaid(row):
    """Returns previous amount paid for given ExpenseAccount"""


    if pd.isnull(row['PreviousMonthPaid']):
        return (0)
    elif row['OpeningPaymentMonthEnd'] == row['PreviousMonthPaid']:
        return (row['OpeningPaymentAmount'])
    else:
        return (sum(df_trx[\
                    (df_trx['ExpenseAccount'] == row['ExpenseAccount']) & \
                    (df_trx['MonthEnd'] == row['PreviousMonthPaid'])
                      ]\
                    ['Amount'])
        )





#    elif row['PreviousMonthPaid'] == df_expensedetails.loc\
#            [row['ExpenseAccount']]['OpeningPaymentMonthEnd']:
#            return (df_expensedetails.loc[row['ExpenseAccount']]\
#                    ['OpeningPaymentAmount'])
#
#





if __name__=='__main__':


    # Read transaction data and mapping tables into pandas dataframes 
    df_trx_input = pd.read_csv(data_dir+ 'transactions.csv', dayfirst=True, \
            parse_dates=[1])
    df_mapping = pd.read_csv(data_dir+ 'mapping.csv', index_col=0)
    df_expensedetails = pd.read_csv(data_dir+ 'expense_details.csv', \
                index_col=0, parse_dates=[4,6])

    # Create a copy for working so that original dataframe still exists for
    # reference and debugging
    df_trx = df_trx_input

    # Add a month end date into the transaction dataframe
    df_trx['MonthEnd'] = df_trx['Date'] + \
        pd.offsets.MonthEnd(0) 

   
    # Add in the mapped expense account
    df_trx['ExpenseAccount'] = df_trx.apply(\
            func = MapDescriptionToExpenseAccount, axis =1)

    # Summarise by unique MonthEnd /  ExpenseAccount index
    df_trx = pd.pivot_table(df_trx, index=['MonthEnd', 'ExpenseAccount'],\
            values='Amount', aggfunc=np.sum)

    # Reindex to get a complete Cartesian product of MontheEnd / ExpenseAccount
    # indices (need Expense account for every month even if no payment as it
    # may have an amortised value)
    complete_index = pd.MultiIndex.from_product([df_trx.index.levels[0],\
            df_trx.index.levels[1]], names=['MonthEnd', 'ExpenseAccount'])
    df_trx = df_trx.reindex(complete_index, fill_value=0)

    # convert back to a dataframe (as above results in a series as only
    # has one column
    df_trx=pd.DataFrame(df_trx)

    # Use join rather than merge with expensedetails to join single index
    # to multi-index dataframe
    # http://pandas-docs.github.io/pandas-docs-travis/merging.html#merging-join-on-mi
    df_trx = df_trx.join(df_expensedetails, how='left')

    # Move index into columns to make dataframe easier to work with
    df_trx = df_trx.reset_index()

    # Add various other calculated fields to the dataframe & save output
    df_trx['PreviousMonthPaid'] = df_trx.apply(\
            func = PreviousMonthPaid, axis = 1)
    
    df_trx['PreviousAmountPaid'] = df_trx.apply(\
            func = PreviousAmountPaid, axis =1)

    df_trx.loc[df_trx['IsPrepayment'] != True, 'CashExpense'] = \
            df_trx['Amount']
    df_trx['CashExpense'] = df_trx['CashExpense'].fillna(0)

  


    df_trx.to_csv(data_dir + 'transaction_output.csv')




################################################################################
#                OLDER EXPERIMENTATION TO BE DELETED LATER
################################################################################

    # Merge transaction with expense account details (e.g. amortisation period)
#    df_trx = pd.merge(df_trx, df_expensedetails, how='left', \
#            left_on='ExpenseAccount',left_index=True, right_index=True)



#def CartesianLists(L1, L2):
#    """returns cartesian product of 2 pandas series L1 and L2 as a list of 2 lists"""
#
#    outerlist=[]
#    innerlist=[]
#    for x in L1:
#        for y in L2:
#            outerlist.append(x)
#            innerlist.append(y)
#    return ((outerlist, innerlist))
#    #return(list(zip(*[outerlist, innerlist])))


   # temp_index = pd.MultiIndex.from_product([list(df_trx['MonthEnd'].unique()),\
   #         list(df_trx['ExpenseAccount'].unique())])


    # Create summary dataframe with Cartesian product of monthend and Expense 
    # Accounts
#    df_trx_summary = pd.DataFrame({'MonthEnd' : MonthEndCartesian, \
#            'ExpenseAccount' : ExpenseAccountCartesian})





    # Create a cartesian product with MonthEnd and Expense Account.  Need to
    # do this as there may be some expense accounts with no payments for the 
    # month but need to be amortised
#    MonthEndSeries = pd.Series(df_trx['MonthEnd']).unique()
#    ExpenseAccountSeries = pd.Series(df_trx['ExpenseAccount']).unique()
#    (MonthEndCartesian, ExpenseAccountCartesian) = CartesianLists (\
#            MonthEndSeries, ExpenseAccountSeries)




    # Create a summary version
    #df_trx_summary = df_trx.pivot_table\
    #        (index=['MonthEnd', 'ExpenseAccount', 'ExpenseGroup',\
    #                'IsPrepayment', 'AmortisationMonths',\
    #                'LastAmortisationMonthEnd', 'StartingCost'],\
    #        values='Amount',\
    #        aggfunc=np.sum)

    # Move the index to columns.  Can't seem to get this to work directly
    # in pivot_table command above
    # df_trx_summary = df_trx_summary.reset_index()

    
    # Write expense impact to dataframe
# UNCOMMENT BELOW LINE ONCE SUMMARY IS RECREATED
    #df_trx_summary['PandL'] = df_trx_summary_summary(ExpenseForMonth, axis=1)

    

    # Export summary
#    df_trx_summary.to_csv(data_dir + 'transactions_summary.csv')

#def TempSumIf():
#
#    str_to_match="EZIDEBIT HEALTHFIT MB    FORTITUDE VA"
#  
#    mysumif = sum(df_trx[\
#                    (df_trx.Description == str_to_match ) & \
#                    (df_trx.Date == '2016/06/30')]\
#                .Amount)
#
#    print (mysumif) 
#
#def TestMultiIndexCreateWithCartesian():
#
#  #  index = pd.MultiIndex.from_tuples(CartesianLists(['a', 'b', 'c'], [1,2,3]), names=['first', 'second'])
#   
#    (L1, L2) = CartesianLists(['a','b','c'], ['d','e','f'])
#    # L2= CartesianLists(['a','b','c'], ['d','e','f'])[1]
#    df_temp = pd.DataFrame({'head_a' : L1, 'head_b': L2 })
#    print (df_temp)
#

#def MapDescriptionToExpenseAccount(description):
#    """Map bank text transaction desciption to expense accounts"""
#
#    for description_contains in df_mapping.index:
#        if description_contains.upper() in description.upper():
#            return df_mapping.loc[description_contains, 'ExpenseAccount']
#
#    # if not matches found
#    return ('Unmatched')
#


# Add in the mapped expense account
#    df_trx['ExpenseAccount'] = df_trx['Description'].apply\
#            (MapDescriptionToExpenseAccount)



#def ExpenseForMonth(row):
#    """ Return expense for the month.   Row is a pandas dataframe row
#    passed to this funtion as a series"""
#
#    if row['IsPrepayment'] == False:
#        return(row['Amount'])
#    else:
#        return ('TBA')
#
