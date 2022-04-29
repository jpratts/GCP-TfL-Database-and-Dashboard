# London Bicycle Usage Database & Dashboard Project
-----------------------------

Documentation in Progress


Motivation: 

Transport for London (TfL) offers some very impressive data to the public. However, much of this is not easily accessible as it must be accessed via an API. Is there a way to easily extract this data and provide it in a more accessible form? Can we augment this data with information from other APIs in order to provide the public with some predictive analytics on TfL usage? 

We will address these questions by taking a look at one segment of TfL's data, it's bike point information (how many TfL Bicycles are being used). We will develop a set of **automated** ETL processes in Google Cloud Platform which will extract, store, and analyse the data of interest. Weather and datetime information will also be stored and used as predictors in our ML model - the aim of which is to provide an estimate of next-day bicycle usage. 

Setup instructions & comments can be found in the following sections.

-------------------------------

1. **Introduction**
2. **Scheduler & Pub/Sub**
3. **Cloud Functions**
4. **BigQuery**
5. **BigQuery ML**
6. **Data Studio**
7. **Model Retraining & Comments**

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
  
![Pipeline](https://user-images.githubusercontent.com/76081318/166061290-5fb93821-162f-408f-bf46-2151a5dd7191.jpg)

</details>

# 2. Scheduler & Pub/Sub
<details>
  <summary>Click to expand</summary>
  
-----------------
In order to trigger our Cloud Function on a daily basis, we must configure a system which acts as a scheduler. First, we must create a Pub/Sub topic:

- This requires minimal configuration, simply give it a Topic ID. 
![Pubsub](https://user-images.githubusercontent.com/76081318/166063568-11ca4457-6161-4747-9bea-69a950bce505.PNG)

- We can now set up a Scheduler function. Name, Region, Description and Timezone are self-explanatory. For Frequency, you must use a unix-cron schedule expression. This follows a minute hour day-of-month month day-of-week pattern. In this case, we are saying run at 45 minutes past 8am, every day, every month, etc.  
![Scheduler](https://user-images.githubusercontent.com/76081318/166063891-a19e7a75-2bad-4cc5-abc6-c44cd7eae7fe.PNG)

- Next, you must tell the Scheduler what to execute. In this case, we will tell it the Target Type is a Pub/Sub and then select the Pub/Sub we made earlier. The message body must contain some text, but in this case it does not matter what you enter. 
![Scheduler2](https://user-images.githubusercontent.com/76081318/166065282-82a4d2d4-d66b-4848-a986-d1ef36820b05.PNG)

The Scheduler and Pub/Sub are now configured. We will next create the script which will be triggered by this system.

