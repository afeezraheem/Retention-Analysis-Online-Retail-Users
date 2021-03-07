#!/usr/bin/env python
# coding: utf-8

# In[1]:


#In this project, I wish to complete a retention analysis of a UK-based online retail buyers/users
# The data set contains all the transactions occurring between 01/12/2010 and 09/12/2011 for the company.

#Importing the packages

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
import datetime as dt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


#Jmport the dataframe

df =pd.read_csv("online_retail.csv")


# In[4]:


#Exploring the data set further to see the missing values and proportion

df.head()

df.isnull().any()

df.isnull().sum()/df.shape[0]


# In[5]:


# I decided to check the date format and the Description columns

df.Description.value_counts()

df['InvoiceDate']

df.dtypes


# In[6]:


# I try to ensure that the variables match the correct data types

df['Quantity']= pd.to_numeric(df.Quantity, downcast= 'integer', errors='coerce')
df['UnitPrice']= pd.to_numeric(df.UnitPrice, downcast= 'integer', errors='coerce')
df['CustomerID']= pd.to_numeric(df.CustomerID, downcast= 'integer', errors='coerce')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])


# In[7]:


# After trying to adjust the data types, I checked the percentage of missing values after data type checks above. Only 0.2 Per cent of the Description is null, while 25 per cent of the customer ID is null. 
# CustomerID is unique record identifier, hence, I did not drop it. 

df.isnull().any()

df.CustomerID.value_counts()

df.isnull().sum()/df.shape[0]


# In[9]:


#Convert the InvoiceDate to an InvoiceMonth...

def getMonth(x):
    return dt.datetime(x.year, x.month,1)

df['InvoiceMonth']= df['InvoiceDate'].apply(getMonth)
df['InvoiceMonth']


# In[10]:


# Done differently, as getMonth() is an in-built function that works with the datatime i.e. dt
        
df.InvoiceDate.apply(lambda x: getMonth(x))


# In[11]:


# Great! Now let's get the first time each customer has purchased. 

df['CohortMonth']= df.groupby('CustomerID')['InvoiceMonth'].transform('min')
df['CohortMonth']


# In[13]:


#Next is the headers for the months a given user is active

def getDateDiff(df, column1, column2):
    year1 =  df[column1].dt.year
    month1= df[column1].dt.month
    year2 = df[column2].dt.year
    month2 =df[column2].dt.month
    year_diff = year1-year2
    month_diff = month1-month2
    return (year_diff*12 + month_diff +1)

# With these, we can derive the unique cohort intervals at which users are active

df['CohortActiveIntervals']= getDateDiff(df, 'InvoiceMonth', 'CohortMonth')
df['CohortActiveIntervals']


# In[14]:


# Note that CohortActiveIntervals above has some duplicate elements. 
# I'd group CustomerID by CohortMonth and CohortActiveIntervals( Referring back to this for my heat map)

df['CohortMonth']= df['CohortMonth'].astype(str)

df_grouped = df.groupby(['CohortMonth', 'CohortActiveIntervals'])['CustomerID'].apply(pd.Series.nunique).reset_index()

df_grouped


# In[15]:


#I decided to use pivot table so that CohortMonth is the first column, 
# the column header will be the CohortActiveIntervals and values will be counted/nunique CustomerID

df_pivoted= df_grouped.pivot_table(index='CohortMonth', columns= 'CohortActiveIntervals', values='CustomerID')

df_pivoted.head()


# In[17]:


# Great! Then I decided to convert the counts into percentages for the headmap. 
# Note that the first column(1.0 :axis=0) represents the total per cohort

# Adding together the number of customers in each cohort
Cohort_users_total = df_pivoted.iloc[:,0]
Cohort_users_total


# In[18]:


#Dividing the data_pivoted by the total number of users in each cohort

retention_rate= df_pivoted.divide(Cohort_users_total,axis=0)
retention_rate


# In[23]:


# Finally, I will put together this dataframe by putting it into a seaborn heatmap

plt.figure(figsize=(8, 8))

# Adding my chart title

plt.title('Users Retention Chart (in % of Total Per Cohort)')

#setting up the plot
ax = sns.heatmap(data = retention_rate, 
            #annotate the graph
            annot = True, 
            fmt = '.0%', 
            # set max value for color bar on seaborn heatmap
            vmax = 0.4,
            cmap = "Blues")

#To set the limits so we can see the entire chart

ax.set_ylim(13.5, 0)

#Yay!Let's show the plot!

plt.show()

