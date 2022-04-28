# Our pipeline is now automatically collecting data from various APIs and storing them in various tables. How can we turn this into a training dataset for our ML model? 

### We can submit a SQL query on GCP to create a new table holding the information of interest.

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

### Using this table, we can now create a simple regression model using BigQuery ML. This is also done via a query. For example, in the following scripts we will predict crowd levels at London Bridge Station using weather data. 

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

### We can then use this trained model to make predictions

```sql
SELECT * FROM ML.PREDICT(MODEL `PROJECT_NAME.tfl_data.crowd_model`, (SELECT * FROM tfl_data.prediction_table))
```

### Notably, this is just going to create predictions using all previous data. If we want to predict crowdedness for the upcoming day we could use

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

