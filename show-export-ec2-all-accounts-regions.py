import boto3
import json
import os
import IPy

profiles = ['default', 'oregon', 'hongkong']

input_access_range=input(">Input your EC2 Security Group setting: ALL, MYIP or specific ragne e.g. 50.12.1.0/24 : ")
if input_access_range != 'all' and input_access_range != 'ALL' \
        and input_access_range != 'myip' and input_access_range != 'MYIP':
    if input_access_range[-3]!='/':
        input_access_range += '/32'
    print('Set Security Group Inbound range to: ', input_access_range)
    try:
        IPy.IP(input_access_range)
    except Exception as e:
        print(e)
        quit()

ec2List = []
for profile in profiles:
    regionclient = boto3.session.Session(
        profile_name=profile
    )
    ec2 = regionclient.client('ec2')
    response = ec2.describe_regions()

    for i in response['Regions']:
        ec2client = boto3.session.Session(
            profile_name=profile,
            region_name=i['RegionName']
        )
        ec2 = ec2client.client('ec2')
        response_instance = ec2.describe_instances()
        if response_instance['Reservations'] != []:
            for j in response_instance['Reservations']:
                for k in j['Instances']:
                    try:
                        for keys in k['Tags']:
                            if keys['Key'] == 'Name':
                                name = keys['Value']
                    except Exception as e:
                        name = 'no-name'
                    print(k['InstanceId'], k['State']['Name'], i['RegionName'], name)
                    ec2List.append({
                        "name": name,
                        "profile": profile,
                        "region": i['RegionName'],
                        "ec2id": k['InstanceId'],
                        "status": k['State']['Name'],
                        "access_range": input_access_range
                    })
with open('./ec2List-export.json', 'w') as f:
    json.dump(ec2List, f, indent=4)

print('EC2 List exported to file:', os.getcwd()+'/ec2List-export.json')
print('Please verify it and change file name to ec2List.json for update program to import')
