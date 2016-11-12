import boto3
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

code_pipeline = boto3.client('codepipeline', region_name='ap-southeast-1')
ec2con = boto3.client('ec2', region_name='ap-southeast-1')
elb_client = boto3.client('elb', region_name='ap-southeast-1')

def put_job_success(job, message):
    """Notify CodePipeline of a successful job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_success_result()

    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)

def lambda_handler(event, context):

    reservations = ec2con.describe_instances().get('Reservations',[])
    instances = sum([[
      i for i in r['Instances']]
        for r in reservations
    ], [])
    instanceslist = len(instances)
    for i in instances:
      for tags in i['Tags']:
        value = tags['Value']
        key = tags['Key']
        if key == 'status':
          ec2 = boto3.resource('ec2')
          instance = ec2.Instance(i['InstanceId'])
          if value == 'active':
            instance.create_tags(
              Tags=[
                {
                  'Key': key,
                  'Value': 'inactive'
                },
              ]
            )
            response = elb_client.deregister_instances_from_load_balancer(
                LoadBalancerName='WebGoat-ELB',
                Instances=[
                    {
                        'InstanceId': i['InstanceId']
                    },
                ]
            )
            logger.info(i['InstanceId'] + ': active to inactive')
          elif value == 'inactive':
            instance.create_tags(
              Tags=[
                {
                  'Key': key,
                  'Value': 'active'
                },
              ]
            )
            response = elb_client.register_instances_with_load_balancer(
                LoadBalancerName='WebGoat-ELB',
                Instances=[
                    {
                        'InstanceId': i['InstanceId']
                    },
                ]
            )
            logger.info(i['InstanceId'] + ': inactive to active')

            # Extract the Job ID
            job_id = event['CodePipeline.job']['id']
            # Extract the Job Data
            job_data = event['CodePipeline.job']['data']
            put_job_success(job_id, 'Updated Active')
            return "Complete."
