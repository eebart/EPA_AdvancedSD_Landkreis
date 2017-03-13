import sys
import pandas as pd
import numpy as np
import os
from data_handling import checkNameCommonality
from data_handling import selectLandkreise
from data_handling import saveEverything


# Birth rate (Births/total population)                          |/
# Population 20-40                                              |/
# Population Adults and pre-retirees (40-retirement age)        |/
# Retirement age = 65                                           |/
# Population retired (retirement age >)                         |/
# Population density (population/area)                          |/
# Hospital beds                                                 |/
# Housing price (Kaufsumme)                                     |/
# Total working_age                                             |/
# hospitals                                                     |/
# Total Unemployed_unemployed                                   |/
# Average life expectancy (men and women)                       |/
# Spendable income average (already merged into file, by hand)  |/

# Calculating/restructuring input data
# Input data to the model with EMA
# Save according to landkreise
# Generate one big output file, process to same format
# Analyse the data.

def extract_spendable_income(df):
    spendable_income = pd.read_csv('GUEST_6spendableinkomen.csv', sep=';')
    spendable_income.rename(columns={' Wert': 'Spendable Income'}, inplace=True)

    df = df.join(spendable_income['Spendable Income'])
    return df

def extract_life_expectancy(df):
    # Extract life expectancy
    life_expectancy = pd.read_excel('aggregation Landkreis data.xlsx', sheetname='averge life per landkreis')
    life_expectancy.drop(['Unnamed: 1', 'Unnamed: 2', 'Unnamed: 7'], axis=1, inplace=True)
    life_expectancy.rename(columns={'Unnamed: 3': 'Avg life men 50 years ago',
                            'Unnamed: 4': 'Avg life women 50 years ago',
                            'Unnamed: 5': 'Avg life men 2011',
                            'Unnamed: 6': 'Avg life women 2011'}, inplace=True)

    # Filter only 2011
    life_expectancy_2011 = life_expectancy[['Schleswig-Holstein', 'Avg life men 2011', 'Avg life women 2011']]
    life_expectancy_2011 = life_expectancy_2011.rename(columns={'Schleswig-Holstein': 'Name',
                                                                'Avg life men 2011': 'Avg life exp men',
                                                                'Avg life women 2011': 'Avg life exp women'})
    # Compare names of landkreise in df and life exp file
    Landkreise_Names = pd.DataFrame()
    d = life_expectancy_2011['Name'].isin(df['Name'])
    for i, check in enumerate(d):
        if check:
            Landkreise_Names = Landkreise_Names.append(life_expectancy_2011.iloc[i], ignore_index=True)
        else:
            continue
            # Part for checking if part of landkreise is contained
            #print(life_expectancy_2011['Name'].iloc[i], 'does not exist in orig.')
            #check = all_data['Name'].str.contains(life_expectancy_2011['Name'].iloc[i], case=False)
            #print(check.loc[check == True])
            #for idx in check.loc[check == True].index.tolist():
                #print('\t', all_data['Name'].iloc[idx])
    data = df.merge(Landkreise_Names, on=['Name'], how='outer', left_index=True, right_index=True)

    return data

def redefine_age_groups(data):
    # Define age groups 20-40
    # 40-65
    # 65 and older
    # Replace NaN value for in 0 value,
    # Since the int() can't translate NaN to int
    data['Total, 20 to under 25 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 25 to under 30 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 30 to under 35 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 35 to under 40 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 40 to under 45 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 45 to under 50 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 50 to under 55 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 55 to under 60 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 60 to under 65 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 65 to under 75 years_age'].replace(np.nan, 0, inplace=True)
    data['Total, 75 years and older_age'].replace(np.nan, 0, inplace=True)

    age2040_lst = []
    age4065_lst = []
    ageretired_lst = []
    for i in range(len(data)):
        age2025 = data['Total, 20 to under 25 years_age'].iloc[i]
        age2530 = data['Total, 25 to under 30 years_age'].iloc[i]
        age3035 = data['Total, 30 to under 35 years_age'].iloc[i]
        age3540 = data['Total, 35 to under 40 years_age'].iloc[i]
        age4045 = data['Total, 40 to under 45 years_age'].iloc[i]
        age4550 = data['Total, 45 to under 50 years_age'].iloc[i]
        age5055 = data['Total, 50 to under 55 years_age'].iloc[i]
        age5560 = data['Total, 55 to under 60 years_age'].iloc[i]
        age6065 = data['Total, 60 to under 65 years_age'].iloc[i]
        age6575 = data['Total, 65 to under 75 years_age'].iloc[i]
        age75ao = data['Total, 75 years and older_age'].iloc[i]

        age2040 = int(age2025) + int(age2530) + int(age3035) + int(age3540)
        age4065 = int(age4045) + int(age4550) + int(age5055) + int(age5560)
        ageretired = int(age6575) + int(age75ao)
        age2040_lst.append(age2040)
        age4065_lst.append(age4065)
        ageretired_lst.append(ageretired)

    popdf = pd.DataFrame(data=[age2040_lst, age4065_lst, ageretired_lst], index=['20-40 year olds', '40-65 year olds', '65 year and older']).T
    data = pd.concat([data, popdf], axis=1)

    return data

# ConstructionHouses, NumberHouses
def HouseConstruction_NumberHouses(totaldf):
    # Read both files
    HouseConstruction = pd.read_csv('ConstructionOfHouses.csv', sep=';', encoding='UTF-8')
    NumberHouses = pd.read_csv('NumberOfHouses.csv', sep=';', encoding='UTF-8')
    # Construct dictionary for following functions
    # Retrieved from former datahandling file
    bothFiles = {'ConstructionOfHouses': HouseConstruction,
                 'NumberOfHouses': NumberHouses}

    checkNameCommonality(bothFiles)
    saveEverything(bothFiles)

    bothfiles_cleaned = selectLandkreise("")

    checkNameCommonality({"bothfiles":bothfiles_cleaned,
                          "rest": totaldf})

    totaldf = pd.merge(totaldf, bothfiles_cleaned, how='outer', on=['Index', 'Name', 'Type']).drop('Unnamed: 0', axis=1)
    totaldf.rename(columns={'Construction_ConstructionOfHouses': 'Construction of houses',
                    'Houses_NumberOfHouses': 'Number of houses'}, inplace=True)

    return totaldf


def main():
    # Read csv file with all previously cleaned data
    all_data = pd.read_csv('data_final.csv')
    # Move to the Database folder
    os.chdir('AllDataFromDatabase')
    # Adding spendable income to all data
    all_data = extract_spendable_income(all_data)
    # Extract life expectancy
    all_data = extract_life_expectancy(all_data)

    # Replace missing data for NaN value
    all_data = all_data.replace('-', np.nan)
    all_data = all_data.replace('', np.nan)
    # Redefine the age groups
    all_data = redefine_age_groups(all_data)

    all_data = HouseConstruction_NumberHouses(all_data)
    # Calculate the differences in life exp between women and men
    all_data['Differences in life exp'] = all_data['Avg life exp women'] - all_data['Avg life exp men']

    # Calculate birthrate
    all_data['Birthrate/1000 inh'] = all_data['Total_births'] / all_data['Total_age']*1000

    # Calculate population density
    all_data['Population density (inh/km2)'] = all_data['Total_age'] / all_data['Area (km^2)_surface']
    # Select data that can be used as input for the model
    data4model = all_data[['Index', 'Name', 'Birthrate/1000 inh', 'Beds in hospitals (JD)_hospital',
                       '20-40 year olds', '40-65 year olds', '65 year and older',
                       'Total_workingAge', 'Total Unemployed_unemployed',
                       'Population density (inh/km2)', 'Kaufsumme - Total (Tsd. EUR)_worthArea',
                       'Hospitals_hospital', 'Avg life exp men', 'Avg life exp women',
                       'Differences in life exp', 'Spendable Income', 'Area (km^2)_surface',
                       'Construction of houses', 'Number of houses']]

    # Save to csv
    data4model.to_csv('ModelInputData.csv', index=False)

if __name__ == '__main__':
    main()
    sys.exit()
