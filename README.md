# London Bicycle Usage Database & Dashboard Project
-----------------------------

Documentation in Progress


### Motivation: 

Transport for London (TfL) offers some very impressive data to the public. However, much of this is not easily accessible as it must be accessed via an API. Is there a way to easily extract this data and provide it in a more accessible form? Can we augment this data with information from other APIs in order to provide the public with some predictive analytics on TfL usage? 

We will address these questions by taking a look at one segment of TfL's data, it's bike point information (how many TfL Bicycles are being used). We will develop a set of **automated** ETL processes in Google Cloud Platform which will extract, store, and analyse the data of interest. Weather and datetime information will also be stored and used as predictors in our ML model - the aim of which is to provide an estimate of next-day bicycle usage. 

Pipeline design, setup instructions & comments can be found in the following sections.

-------------------------------

1. **Introduction**
2. **Scheduler & Pub/Sub**
3. **Cloud Functions**
4. **BigQuery ML**
5. **Data Studio**
6. **Model Retraining & Comments**

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
  
![Pipeline](https://user-images.githubusercontent.com/76081318/166077680-41dc6a76-4104-46bf-8a32-da709a1795bc.png)

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

</details>

# 3. Cloud Functions
<details>
  <summary>Click to expand</summary>
  
-----------------
- When creating the Cloud Function, you will first need to configure some settings before entering code. Most of these are self-explanatory (Function Name, Region, etc) or vary depending on use-case (e.g. Memory allocation; can be left default in this case). One setting which must be configured is Trigger. Ensure this is set to Cloud Pub/Sub and then select the Pub/Sub Topic we created in the last section. 
![Func1](https://user-images.githubusercontent.com/76081318/166066339-9c740e5a-25cc-4977-b224-a4ea193e7e94.PNG)

- We will then be presented with the Code view. We will be using Python 3.9.
  
- You can upload the Main.py and requirements.txt files or enter your own code depending on your requirements. In this case, the provided main.py script performs some ETL processes on TfL and weather data with the data being loaded into Big Query.
  
- Ensure that the Entry Point is the name of the defined function, in this case "pull_data". 
  
- The code, as provided here, also requires a gcp auth key, obtaining such a key is outside the scope of this guide but once attained, it can also be uploaded here. 
  
</details>

# 4. BigQuery ML
<details>
  <summary>Click to expand</summary>
  
----------------
## Our pipeline is now automatically collecting data from various APIs and storing them in various tables. How can we turn this into a training dataset for our ML model? 

- We can submit a SQL query on GCP to create a new table holding the information of interest.

```sql
INSERT INTO 
  `PROJECT_NAME.tfl_data.ml_train`
  (percentageOfBaseline, feels_day, clouds, uv, date, dow)

SELECT
  ct.percentageOfBaseline,
  wt.feels_day,
  wt.clouds,
  wt.uv,
  wt.dt,
  CAST(EXTRACT(DAYOFWEEK FROM (PARSE_DATE("%d/%m/%Y", wt.dt))) AS STRING ) AS dow

FROM
  `PROJECT_NAME.tfl_data.crowd_table` AS ct

INNER JOIN
  PROJECT_NAME.tfl_data.weather_table AS wt
ON
  ct.date = wt.dt;
```

- Using this table, we can now create a simple regression model using BigQuery ML. This is also done via a query. For example, in the following scripts we will predict crowd levels at London Bridge Station using weather data. 

```sql
CREATE OR REPLACE MODEL
  `PROJECT_NAME.tfl_data.crowd_model`
OPTIONS
  (model_type='linear_reg',
  input_label_cols=['percentageOfBaseline']) AS
SELECT
  *
FROM
  tfl_data.ml_train
WHERE
  percentageOfBaseline IS NOT NULL

```

- We can then use this trained model to make predictions

```sql
SELECT * FROM ML.PREDICT(MODEL `PROJECT_NAME.tfl_data.crowd_model`, (SELECT * FROM tfl_data.prediction_table))
```

- Notably, this is just going to create predictions using all previous data. If we want to predict crowdedness for the upcoming day we could use

```sql
SELECT * FROM ML.PREDICT(MODEL `PROJECT_NAME.tfl_data.crowd_model`,
(SELECT
  wt.dt,
  wt.feels_day,
  wt.clouds,
  wt.uv,
  CAST(EXTRACT(DAYOFWEEK FROM (PARSE_DATE("%d/%m/%Y", wt.dt))) AS STRING ) AS dow

FROM
  tfl_data.weather_table AS wt

ORDER BY PARSE_DATE("%d/%m/%Y", wt.dt) DESC

LIMIT 1)
)
```
</details>
