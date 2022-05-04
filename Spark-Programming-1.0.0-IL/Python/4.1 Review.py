# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 400px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC # Review
# MAGIC ##![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) De-Duping Data Lab
# MAGIC 
# MAGIC In this exercise, we're doing ETL on a file we've received from some customer. That file contains data about people, including:
# MAGIC 
# MAGIC * first, middle and last names
# MAGIC * gender
# MAGIC * birth date
# MAGIC * Social Security number
# MAGIC * salary
# MAGIC 
# MAGIC But, as is unfortunately common in data we get from this customer, the file contains some duplicate records. Worse:
# MAGIC 
# MAGIC * In some of the records, the names are mixed case (e.g., "Carol"), while in others, they are uppercase (e.g., "CAROL"). 
# MAGIC * The Social Security numbers aren't consistent, either. Some of them are hyphenated (e.g., "992-83-4829"), while others are missing hyphens ("992834829").
# MAGIC 
# MAGIC The name fields are guaranteed to match, if you disregard character case, and the birth dates will also match. (The salaries will match, as well,
# MAGIC and the Social Security Numbers *would* match, if they were somehow put in the same format).
# MAGIC 
# MAGIC Your job is to remove the duplicate records. The specific requirements of your job are:
# MAGIC 
# MAGIC * Remove duplicates. It doesn't matter which record you keep; it only matters that you keep one of them.
# MAGIC * Preserve the data format of the columns. For example, if you write the first name column in all lower-case, you haven't met this requirement.
# MAGIC * Write the result as a Parquet file, as designated by *destFile*.
# MAGIC * The final Parquet "file" must contain 8 part files (8 files ending in ".parquet").
# MAGIC 
# MAGIC <img alt="Hint" title="Hint" style="vertical-align: text-bottom; position: relative; height:1.75em; top:0.3em" src="https://files.training.databricks.com/static/images/icon-light-bulb.svg"/>&nbsp;**Hint:** The initial dataset contains 103,000 records.<br/>
# MAGIC The de-duplicated result haves 100,000 records.
# MAGIC 
# MAGIC ##### Methods
# MAGIC - DataFrameReader (<a href="https://spark.apache.org/docs/latest/api/python/pyspark.sql.html?highlight=dataframereader#pyspark.sql.DataFrameReader" target="_blank">Python</a>/<a href="http://spark.apache.org/docs/latest/api/scala/org/apache/spark/sql/DataFrameReader.html" target="_blank">Scala</a>)
# MAGIC - DataFrame (<a href="https://spark.apache.org/docs/latest/api/python/pyspark.sql.html?highlight=dataframe#pyspark.sql.DataFrame" target="_blank">Python</a>/<a href="http://spark.apache.org/docs/latest/api/scala/org/apache/spark/sql/Dataset.html" target="_blank">Scala</a>)
# MAGIC - Built-In Functions (<a href="https://spark.apache.org/docs/latest/api/python/pyspark.sql.html?highlight=functions#module-pyspark.sql.functions" target="_blank">Python</a>/<a href="http://spark.apache.org/docs/latest/api/scala/org/apache/spark/sql/functions$.html" target="_blank">Scala</a>)
# MAGIC - DataFrameWriter (<a href="https://spark.apache.org/docs/latest/api/python/pyspark.sql.html?highlight=dataframereader#pyspark.sql.DataFrameWriter" target="_blank">Python</a>/<a href="http://spark.apache.org/docs/latest/api/scala/org/apache/spark/sql/DataFrameWriter.html" target="_blank">Scala</a>)

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup

# COMMAND ----------

# MAGIC %md
# MAGIC It's helpful to look at the file first, so you can check the format. `dbutils.fs.head()` (or just `%fs head`) is a big help here.

# COMMAND ----------

# MAGIC %fs head dbfs:/mnt/training/dataframes/people-with-dups.txt

# COMMAND ----------

spark.conf.set("spark.sql.shuffle.partitions", "8")

# COMMAND ----------

# TODO

sourceFile = "dbfs:/mnt/training/dataframes/people-with-dups.txt"
destFile = workingDir + "/people.parquet"

# In case it already exists
dbutils.fs.rm(destFile, True)

# Complete your work here...

df = sc.textFile(sourceFile)
header = df.first()
df = df.filter(lambda line: line != header)
tmp_df = df.map(lambda l: l.split(":"))

log_df = tmp_df.toDF(header.split(":"))
from pyspark.sql.functions import *
df1 = log_df.withColumn("n_firstName", initcap(log_df.firstName)).withColumn("n_middleName", initcap(log_df.middleName)).withColumn("n_lastName", initcap(log_df.lastName)).withColumn("n_ssn", regexp_replace(log_df.ssn, "-", ""))


df2 = df1.select("n_firstName", "n_middleName", "n_lastName", "gender", "birthDate", "salary", "n_ssn").dropDuplicates()
df2.count()
people=df2
people.repartition(8).write.parquet("dbfs:/user/sbolanos@minsait.com/spark_programming/people", "overwrite")

# COMMAND ----------

# MAGIC %fs ls dbfs:/user/sbolanos@minsait.com/spark_programming/people

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ##### <img alt="Best Practice" title="Best Practice" style="vertical-align: text-bottom; position: relative; height:1.75em; top:0.3em" src="https://files.training.databricks.com/static/images/icon-blue-ribbon.svg"/> Check your work
# MAGIC 
# MAGIC Verify that you wrote the parquet file out to **destFile** and that you have the right number of records.

# COMMAND ----------

partFiles = len(list(filter(lambda f: f.path.endswith(".parquet"), dbutils.fs.ls("dbfs:/user/sbolanos@minsait.com/spark_programming/people"))))

finalDF = spark.read.parquet(destFile)
finalCount = finalDF.count()

assert partFiles == 8, "expected 8 parquet files located in destFile"
assert finalCount == 100000, "expected 100000 records in finalDF"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clean up classroom
# MAGIC Run the cell below to clean up resources.

# COMMAND ----------

# MAGIC %run "./Includes/Classroom-Cleanup"