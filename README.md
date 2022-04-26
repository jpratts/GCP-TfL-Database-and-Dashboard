# London Bicycle Usage Database & Dashboard Project
-----------------------------

Documentation in Progress


Motivation: 

Transport for London (TfL) offers some very impressive data to the public. However, much of this is not easily accessible as it must be accessed via an API. Is there a way to easily extract this data and provide it in a more accessible form? Can we augment this data with information from other APIs in order to provide the public with some predictive analytics on TfL usage? 

We will address these questions by taking a look at one segment of TfL's data, it's bike point information (how many TfL Bicycles are being used). We will develop a set of **automated** ETL processes in Google Cloud Platform which will extract, store, and analyse the data of interest. Weather and datetime information will also be stored and used as predictors in our ML model - the aim of which is to provide an estimate of next-day bicycle usage. 

-------------------------------

1. **Introduction**

------------------------------

# 1. Introduction.
<details>
  <summary>Click to expand</summary>
  
----------------- 

We will create our entire pipeline, from data extraction to dashboarding, using the following functions on GCP:

- Cloud Scheduler: Will be used to trigger a Pub/Sub Topic when we are ready to pull data from various APIs. Functions like a cron job & is on a daily schedule.
- Pub/Sub topic: Is used to trigger the Cloud Function which is what holds the extraction Python script. 
- Cloud Function: Contains a Python script that pulls data from API and writes it to Big Query.
- Big Query: GCPs Data Warehouse offering. Queried using SQL and fed with data daily from the Cloud function.
- Data Studio: Dashboard of TfL usage and predictions, updated daily.
- Big Query ML: Allows for the execution of ML models in standard SQL queries. We will use this to make some basic predictions on bicycle usage. 

--------------------

