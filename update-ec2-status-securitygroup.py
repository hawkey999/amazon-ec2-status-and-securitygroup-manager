# Sync Security Group to MyIP or ALL
import boto3
import requests
import copy
import json
import os
import IPy
input_update = input(">Show EC2 and SecurityGroup status(Dryrun) or Update as ec2List? (d/u)")

# Display all EC2 status

# For public users, please use this to get your public IP
# requestsIP = requests.get('http://checkip.amazonaws.com/')
# MYIPaddress = requestsIP.text[0:-1]+'/32'

# For amazon users working within amazon VPN, please us this to get your public IP
requestsIP = requests.get('https://1wi4of3f4e.execute-api.cn-north-1.amazonaws.com.cn/checkip')
MYIPaddress = requestsIP.text+'/32'

print('MYIP Address: ', MYIPaddress)
print()
# import ec2List
print('Loading EC2 List from: ', os.getcwd()+'/ec2List.json')
with open('./ec2List.json', 'r') as f:
    ec2List = json.load(f)

print('Checking all EC2 security group...')
for i in ec2List:
    try:
        access_range = i['access_range']
        if access_range != 'all' and access_range != 'ALL' \
                and access_range != 'myip' and access_range != 'MYIP':
            if access_range[-3] != '/':
                access_range += '/32'
            try:
                IPy.IP(access_range)
            except Exception as e:
                print(e)
                quit()
        ec2client = boto3.session.Session(
            profile_name=i['profile'],
            region_name=i['region']
        )
        ec2 = ec2client.client('ec2')

        # get status and Security Group of EC2
        response_instance = ec2.describe_instances(
            InstanceIds=[i['ec2id']]
        )
        if response_instance['Reservations'] != []:
            for j in response_instance['Reservations']:
                for k in j['Instances']:
                    # get EC2 name
                    try:
                        for keys in k['Tags']:
                            if keys['Key'] == 'Name':
                                name = keys['Value']
                    except Exception as e:
                        name = 'no-name'
                    status = k['State']['Name']
                    print(i['ec2id'], status, i['region'], name)
                    
                    # update EC2 status 
                    switch = i['status']
                    if input_update == 'u' and status != switch:
                        if switch == 'running':
                            re_switch = ec2.start_instances(
                                InstanceIds=[i['ec2id']],
                            )
                            print("Starting EC2 ...")
                        elif switch == 'stopped':
                            re_switch = ec2.stop_instances(
                                InstanceIds=[i['ec2id']],
                            )
                            print("Stopping EC2 ...")

                    # check security group's ip permission
                    for sg in k['SecurityGroups']:
                        re_sg = ec2.describe_security_groups(
                            GroupIds=[sg['GroupId']]
                        )
                        # verify security group policy and update ChangeFlag
                        ChangeFlag = False
                        for permission in re_sg['SecurityGroups'][0]['IpPermissions']:
                            permission_orgin = copy.deepcopy(permission)
                            print('  Port:',permission['FromPort'],permission['IpRanges'],permission['ToPort'])
                            if access_range == 'ALL' or access_range == 'all':
                                if permission['IpRanges'] != [{'CidrIp': '0.0.0.0/0'}]:
                                    ChangeFlag = True
                                    permission['IpRanges'] = [{'CidrIp': '0.0.0.0/0'}]
                                    print('    Change SecurityGroup to allow 0.0.0.0/0...')
                            elif access_range == 'MYIP' or access_range == 'myip':
                                if permission['IpRanges'] != [{'CidrIp': MYIPaddress}]:
                                    ChangeFlag = True
                                    permission['IpRanges'] = [{'CidrIp': MYIPaddress}]
                                    print('    Change SecurityGroup to MYIP:', MYIPaddress,'...')
                            else:
                                # TODO verify ip address access_range
                                ChangeFlag = True
                                permission['IpRanges'] = [{'CidrIp': access_range}]
                                print('    Change SecurityGroup to specific IP:', access_range,'...')

                            # update ip permission
                            if ChangeFlag:
                                if input_update == 'u':
                                    ec2.revoke_security_group_ingress(
                                        GroupId=sg['GroupId'],
                                        IpPermissions=[permission_orgin]
                                    )
                                    ec2.authorize_security_group_ingress(
                                        GroupId=sg['GroupId'],
                                        IpPermissions=[permission]
                                    )
                                else:
                                    print('    Dry run! Ignore update')
                        print()
        else:
            print('No such EC2: ', i['ec2id'], 'in region: ',i['region'])

    except Exception as e:
        print(e)
