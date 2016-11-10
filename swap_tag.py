import boto3

def lambda_handler(event, context):

    ec2con = boto3.client('ec2', region_name='ap-southeast-1')
    elb_client = boto3.client('elb', region_name='ap-southeast-1')

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
            print i['InstanceId'] + ': active to inactive'
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
            print i['InstanceId'] + ': inactive to active'
