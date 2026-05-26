from pyspark.sql import SparkSession
from config.config import configuration

if __name__ == "__main__":
    spark = (SparkSession.builder.appName("RealTimeStreaming_aws")
            .config('spark.jars.packages',
                    'org.apache.hadoop:hadoop-aws:3.3.1,'
                    'com.amazonaws:aws-java-sdk:1.11.469' )
            .config('spark.hadoop.fs.s3a.impl' , 'org.apache.hadoop.fs.s3a.S3AFileSystem')
            .config('spark.hadoop.fs.s3a.access.key' , configuration.get('AWS_ACCESS_KEY'))
            .config('spark.hadoop.fs.s3a.secret.key' , configuration.get('AWS_SECRET_KEY'))
            .config('spark.hadoop.fs.s3a.aws.credentials.provider' , 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')
            .getOrCreate()
            )
    
    text_input_dir = 'file://'
            






    # Your code here
    spark.stop()
