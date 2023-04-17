Here's how you can approach the deployment:

 Launch an EC2 instance with Ubuntu or any other suitable operating system. You can install all the necessary dependencies on this instance.

Install and configure PostgreSQL on your EC2 instance, and create a database for your application.

Deploy your Flask API to the EC2 instance using gunicorn or uwsgi as a web server.

Create an RDS instance with PostgreSQL as the database engine. Use the same database credentials that you used for the database created in step 2.

Create a Lambda function that runs your data ingestion code, and configure a schedule using Amazon CloudWatch Events.

Use AWS CloudFormation to define and deploy your entire stack, including your EC2 instance, RDS instance, API Gateway, and Lambda function.

Configure API Gateway to route incoming requests to your Flask API.

Alternatively, you can deploy your Flask API using AWS Elastic Beanstalk. Elastic Beanstalk will automatically handle the deployment, scaling, and management of your application.

Set up CloudWatch to monitor your resources and applications in the cloud, and set up alerts and notifications for any issues.

Finally, use Amazon S3 to store any files or data that your application needs.

This approach will give you a highly scalable and reliable deployment of your Flask API and PostgreSQL database on AWS, along with a scheduled version of your data ingestion code.