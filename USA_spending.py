"""###########################################################################
"                          Public spending data                              "
"                       Elena Casanovas - Jan 2021                           "
###########################################################################""" 

import os
import requests
import pandas as pd
os.chdir('') # set working directory here


''' Prameters '''
year = '2019' # choose year 


''' 01. Agency list '''
page      = 1
next_page = True
output    = []
cols_ag   = ['agency_name', 'abbreviation', 'agency_code', 'agency_id', 
             'current_total_budget_authority_amount']

while next_page:
    payload   = {'fiscal_year': year, 'limit': '100', 'page': page}
    response  = requests.get('https://api.usaspending.gov/api/v2/reporting/agencies/overview/', params = payload).json()
    output   += response['results']
    page      = response['page_metadata']['page'] + 1    
    next_page = response['page_metadata']['hasNext']      

agency_list = pd.DataFrame(list(output), columns = cols_ag)

del page, next_page, output, cols_ag, payload, response


''' 02. Payroll per Agency '''
mynums = agency_list['agency_id']
output = []

for i in mynums:
    print(i)
    agencyn     = i
    payload     = {'fiscal_year': year, 'limit': '100', 'funding_agency_id': agencyn}
    response    = requests.get('https://api.usaspending.gov/api/v2/financial_spending/major_object_class/', params = payload).json()
    for item in response['results']:
        item.update({'agency_id': agencyn})
    output     += response['results']
    budget_data = pd.DataFrame(output)
    budget_data = budget_data.pivot(index='agency_id', columns='major_object_class_code', values='obligated_amount')

del agencyn, i, item, mynums, output, payload, response  


''' 03. Budget categories/ codes translation ''' 
payload     = {'fiscal_year': year, 'limit': '100', 'funding_agency_id': 315}
response    = requests.get('https://api.usaspending.gov/api/v2/financial_spending/major_object_class/', params = payload).json()
translation = pd.DataFrame(response['results'], columns = ['major_object_class_code', 'major_object_class_name'])

translation.to_stata("USASp_transl.dta") 

del payload, response


''' 04. Combine and export '''
uspending = pd.merge(agency_list, budget_data, on='agency_id')   
uspending.to_stata("USASp_budget.dta") 


''' END OF THE SCRIPT '''
