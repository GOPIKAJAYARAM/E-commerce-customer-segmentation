# -*- coding: utf-8 -*-
"""Project based on E-commerce customer segmentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KPlRAn0Pi_Hpb0FbcqK8TQbzxehFAnqt
"""

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 

import nltk
nltk.download('punkt')

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler 

import warnings
warnings.filterwarnings('ignore')

df=pd.read_csv("/content/data.csv",encoding= 'unicode_escape')
df.head()

aa=df.groupby(["CustomerID"]).Country.nunique()
aa=aa.reset_index()
aa[aa["Country"]>1]

print(f"The dataset has {df.shape[0]} and {df.shape[1]} columns")

#looking for null values
pd.DataFrame(df.isnull().sum()).T

#deleting null values 
df=df.dropna()
pd.DataFrame(df.isnull().sum()).T

print("There are ", df.duplicated().sum()," duplicate values")
#Deleting duplicates 
df=df.drop_duplicates()
print("Existing duplicates after deleting: ",df.duplicated().sum())

df.info()

#changing invoice date from object type to datetime .
df_date = df['InvoiceDate'].str.split(" ", expand = True)
df['InvoiceDate'] = df_date[0]
df['InvoiceDate'] = df['InvoiceDate'].astype('datetime64[ns]')

#changing customerID from float to int 
df["CustomerID"]=df["CustomerID"].astype(int)

df.info()

print(f"The resulting dataset 'df' has {df.shape[0]} and {df.shape[1]} columns")

#cancelled stocks
df[df["Quantity"]<0][:5]

#since the data includes samples of cancelled stock as well , it is better to delete it.
cancelled_items=df[df["InvoiceNo"].str[0]=="C"]
print("There are ",cancelled_items.shape[0],"cancelled items in the dataset.")
cancelled_item_index=df[df["InvoiceNo"].str[0]=="C"].index
df.drop(cancelled_item_index,inplace=True)
print("After dropping it we have ",df.shape[0],"datas left in the dataset.")

#since invoice number gives us details about transactions only it wont make any difference if we delete it .
df.drop("InvoiceNo",axis=1,inplace=True)
df=df.reset_index(drop=True)
df.shape

df.head()

#United kingdom has the most number of customers
plt.figure(figsize=(20,10))
sns.set_theme(style="whitegrid")
chart=sns.countplot(x=df["Country"],orient="v")
chart.set_xticklabels(chart.get_xticklabels(), rotation=45)
plt.show()

df[df["UnitPrice"]<0]

dff=pd.DataFrame()
dff['Description']=df['Description'] 
print("The description column alone contains ",dff.duplicated().sum(),"duplicate descriptions ")
dff=dff.drop_duplicates()
print("Dropping it leaves us with",dff.shape[0],"unique number of descriptions.")

#description dataset 
dff

"""**Preprocessing description data for NLP.**

1)Removing numerical values and punctuations.
"""

dff['description_processed'] = dff['Description'].str.replace("[^a-zA-Z]", " ")
dff[["Description",'description_processed']].sample(10)

"""2)Changing to lowercase & deleting the short words."""

# It seems like the corpus normally consists of lowercase words.
dff['description_processed'] = [review.lower() for review in dff['description_processed']] 

dff['description_processed'] = dff['description_processed'].apply( lambda row:" ".join([word for word in row.split() if len(word)>2 ]))
dff[["Description",'description_processed']].sample(10)

"""3)Lemmatization"""

nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

lemmatizer = WordNetLemmatizer()

def nltk_tag_to_wordnet_tag(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:          
        return None

def lemmatize_sentence(sentence):
    nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))  
    wordnet_tagged = map(lambda x: (x[0], nltk_tag_to_wordnet_tag(x[1])), nltk_tagged)
    lemmatized_sentence = []
    for word, tag in wordnet_tagged:
        if tag is None:
            lemmatized_sentence.append(word)
        else:        
            lemmatized_sentence.append(lemmatizer.lemmatize(word, tag))
    return " ".join(lemmatized_sentence)


dff['description_processed'] = dff['description_processed'].apply(lambda x: lemmatize_sentence(x))

"""4)Removing stopwords."""

nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk import word_tokenize

stop_words = stopwords.words('english')

add_words = ['large','small','mini','set','design','red','purple','blue','pink','white','black','dark','pack','green','yellow','orange','rise','love','water','round','shape','square','oval','ivory','charm','polkadot','heart','home','sweet']

stop_words.extend(add_words)

def remove_stopwords(rev):
    review_tokenized = word_tokenize(rev)
    rev_new = " ".join([i for i in review_tokenized  if i not in stop_words])
    return rev_new

dff['description_processed'] = [remove_stopwords(r) for r in dff['description_processed']]

"""Plotting"""

## Plotting most frequent words

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = 'white')
from nltk import FreqDist #function to find the frequent words in the data


#Extracts words into list and count frequency
all_words = ' '.join([text for text in dff['description_processed']])
all_words = all_words.split()
words_df = FreqDist(all_words)

# Extracting words and frequency from words_df object
words_df = pd.DataFrame({'word':list(words_df.keys()), 'count':list(words_df.values())})
words_df
# Subsets top 30 words by frequency
words_df = words_df.nlargest(columns="count", n = 40) 

words_df.sort_values('count', inplace = True)

# Plotting 30 frequent words
plt.figure(figsize=(20,10))
ax = plt.barh(words_df['word'], width = words_df['count'])
plt.show()

## Bilding a Word Cloud

from wordcloud import WordCloud
all_words = ' '.join([text for text in dff['description_processed']])
 

wordcloud = WordCloud(width = 800, height = 800, 
                      background_color ='white', 
                      min_font_size = 10).generate(all_words)

#plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
plt.show()

"""Creating bag of words - by Tfidf (Term Frequency inverse document frequency) method."""

# Creating matrix of top 2500 tokens
tfidf = TfidfVectorizer(max_features=2500)
X = tfidf.fit_transform(dff.description_processed)
features = tfidf.get_feature_names()
print("The bag of words contains ",len(features),"features")

"""**CLUSTERING-1**

*Finding optimum K value by elbow method.*
"""

from sklearn.cluster import KMeans
wcss = []
for i in range(1,500,50):
    kmeans = KMeans(n_clusters=i,init='k-means++',max_iter=300,n_init=10,random_state=0)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)

fig, ax= plt.subplots(figsize = (15, 8), facecolor = None) 
ax.plot(range(1,500,50),wcss)

ax.set_title('The Elbow Method')
ax.set_xlabel('Number of clusters')
ax.set_ylabel('WCSS')

plt.minorticks_on()
# plt.grid(True, 'major', color='k')
plt.grid(True, 'minor', 'x')

plt.grid(True, color = "purple", linewidth = "1.4",axis = 'x')
plt.show()

"""From the graph above there is a considerable change in the descent at the k value 50 and 100 (even though not obvious as 50)."""

from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=50)
kmeans.fit(X)
clusters=kmeans.labels_
print("Cluster values for first 10 datapoints: ",clusters[:10])

dff["cluster"]=clusters
dff[["Description",'description_processed',"cluster"]].head(10)

# grp=df.groupby(["cluster_value"])["Description"].apply(list)
grp=dff.groupby(["cluster"])["description_processed"].apply(list)

#Representing each clusters
import random 
a,b,c,d,e=map(int,[random.randrange(1, 50, 1) for i in range(5)])
df_cluster=pd.DataFrame({f"cluster:{a}":grp[a][:6],f"cluster:{b}":grp[b][:6],f"cluster:{c}":grp[c][:6],f"cluster:{d}":grp[d][:6],f"cluster:{e}":grp[e][:6]})
df_cluster

merged_data = df.merge(dff,left_on="Description",right_on="Description")
merged_data.sample(5)
#copying merged_data to data 
data=merged_data

#since stockcode alligns with description it may not make any difference by deleting it 
data.drop(["Description","description_processed","StockCode"],axis=1,inplace=True)

#As invoiceDate consists of only 2 years 2010 and 2011,the date is changed to month for better analysis.
data["Month"]=data["InvoiceDate"].dt.month
data.sample(5)

#creating new feature ie: totalprice from existing feature
data["Total_price"]=data["Quantity"]*data["UnitPrice"]
data.sample(10)

#Dropping InvoiceDate along with Quantity and unit price as its product total_price remains as a new column.
data.drop(["InvoiceDate","Quantity","UnitPrice"],axis=1,inplace=True)
print("We have",len(data["Country"].unique())," unique countries , and the data set contains ",data.shape[0]," rows and ",data.shape[1]," columns.")
data.head()

"""*One hot encoding*"""

#Grouping customerID based on country and taking its mode
country_df = data.groupby("CustomerID").agg({'Country':pd.Series.mode})
country_df.reset_index()
country_dummy=pd.get_dummies(country_df["Country"])
country_dummy=country_dummy.reset_index()
print(country_dummy.shape)
country_dummy.head()

#Column Month 
month_df=data[['CustomerID','Month']]
pd.get_dummies(month_df["Month"])
month_dummy= pd.get_dummies(month_df, columns = ['Month'])
month_dummy=month_dummy.groupby("CustomerID").agg("sum").astype(int)
month_dummy=month_dummy.reset_index()
print(month_dummy.shape)
month_dummy.head()

#column cluster 
cluster_df=data[['CustomerID','cluster']]
pd.get_dummies(cluster_df["cluster"])
cluster_dummy= pd.get_dummies(cluster_df, columns = ['cluster']).astype(int)
cluster_dummy=cluster_dummy.groupby("CustomerID").agg("sum")
cluster_dummy=cluster_dummy.reset_index()
print(cluster_dummy.shape)
cluster_dummy.head()

#column Total_price
Total_price_df=data[['CustomerID','Total_price']]
Total_price=Total_price_df.groupby('CustomerID').agg("mean")
Total_price=Total_price.reset_index()
# print(Total_price.isnull().sum())
Total_price.head()

#Binning Total price
print(Total_price["Total_price"].describe())
Total_price['mean_price_binned'] = pd.cut(Total_price['Total_price'], [-1, 13, 18,25,772000], labels=[0,1,2,3])
Total_price.drop("Total_price",axis=1,inplace=True)
print(Total_price.shape)
Total_price.sample(5)

from functools import reduce
dummy_list=[country_dummy,month_dummy,cluster_dummy,Total_price]
final_data = reduce(lambda  left,right: pd.merge(left,right,on=['CustomerID'],
                                            how='outer'), dummy_list)
print("The resulting data set has ",final_data.shape[0]," rows and ",final_data.shape[1]," columns.")
final_data

data_1=final_data.copy()
data_1.drop("CustomerID",axis=1,inplace=True)
X1=data_1

"""**CLUSTERING-2**

Scaling for furthur clustering.
"""

scaler = StandardScaler()
X1 = scaler.fit_transform(X1)
X1[1][:10]

"""Elbow plot """

from sklearn.cluster import KMeans
wcss = []
for i in range(1,400,30):
    kmeans = KMeans(n_clusters=i,init='k-means++',max_iter=300,n_init=10,random_state=0)
    kmeans.fit(X1)
    wcss.append(kmeans.inertia_)
fig, ax= plt.subplots(figsize = (15, 8), facecolor = None) 
ax.plot(range(1,400,30),wcss)

ax.set_title('The Elbow Method')
ax.set_xlabel('Number of clusters')
ax.set_ylabel('WCSS')

plt.minorticks_on()
# plt.grid(True, 'major', color='k')
plt.grid(True, 'minor', 'x')

plt.grid(True, color = "purple", linewidth = "1.4",axis = 'x')
plt.show()

# Clustering with k as 30
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=30)
kmeans.fit(X1)
customer_IDcluster=kmeans.labels_

final_data["cluster"]=customer_IDcluster
final_data.head()

customer_cluster_data=final_data[["CustomerID","cluster"]]
customer_cluster_data

op = df.merge(customer_cluster_data,left_on="CustomerID",right_on="CustomerID")
op.sample(10)

#No of clusters in each groups 
cluster_costumer_no = op.groupby(["cluster"]).CustomerID.nunique()
cluster_costumer_no

