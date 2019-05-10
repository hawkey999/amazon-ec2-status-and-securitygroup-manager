# Amazon EC2 status and Security Group Manager  

This tool list all your Amazon EC2 in your multiple account, export to a json list. You can change the EC2 status to run or stop. You can change the Security Group to open access by all, only your own IP or a specific IP range. And update them all in one command.  
本工具是方便地列出多个AWS Account里面所有Region的EC2， 自动导出到JSON列表。你可以修改EC2实例状态，开机或关机。可以改变安全组规则，允许所有访问，允许本机IP访问，或者允许一个特定的IP地址范围。一个命令就可以完成所有更新工作。

Steps:  
* Config your aws configure profile with region, aws_access_key_id and aws_secret_access_key. The file is usually in /Users/myuser/.aws  
   You just need to setup one credentail for each account, you don't have to set each for ever region, the tool will scan all regions.  
   配置aws config，一个account只需要一个credential，不需要为每个region配置，本工具会自动扫描所有region。

```
   ./config


[default]
region=cn-north-1
output=text

[profile oregon]
region=us-west-2
output=text

[profile bjs]
region=cn-north-1
output=text


   ./credentials

[default]
aws_access_key_id=xxxxxxxxxxxxx
aws_secret_access_key=xxxxxxxxxxxxx

[oregon]
aws_access_key_id=xxxxxxxxxxxxx
aws_secret_access_key=xxxxxxxxxxxxx

[bjs]
aws_access_key_id=xxxxxxxxxxxxx
aws_secret_access_key=xxxxxxxxxxxxx
```
   
* Edit show-export-ec2-all-accounts-regions.py line 16, input your profile name into the list. E.g.  
  编辑 show-export-ec2-all-accounts-regions.py 代码中16行的配置profile name ，例如：   
profiles = ['default', 'oregon', 'bjs']

* Run show-export-ec2-all-accounts-regions.py  and input what kind of Security Group Inbound access range you want to set.  You can input ALL, MYIP, or a specific IP range as you need. For example:   
  运行 show-export-ec2-all-accounts-regions.py ，输入设置你导出列表时候批量设置的安全组开放规则，示例：  
```
python show-export-ec2-all-accounts-regions.py
>Input your EC2 Security Group setting: ALL, MYIP or specific ragne e.g. 50.12.1.0/24 : MYIP
i-66661fooaaaaa1 running cn-north-1 Bastion-BJS
i-66661fooaaaaa2 stopped cn-northwest-1 Bastion-ZHY
i-66661fooaaaaa3 running us-west-2 WinRDP
```
* Change the ec2List-export.json file name to ec2List.json, open and edit it.  
  修改 ec2List-export.json 文件名为 ec2List.json，打开并编辑。  
   Change the EC2 status as you like.   
   E.g. you want to turn off a EC2, change the "running" status to "stopped", or reverse it.   
   Change the Security Group Inbound access range of this specific one EC2.  
   E.g. ALL, MYIP, '54.10.3.5' or '50.11.2.0/24'  
   改变对应的EC2开关，或者单独修改某个安全组规则，ALL代表开放所有，MYIP代表自动设置本机公网IP，或者设置一个特定的IP地址范围。  

```
[
    {
        "name": "Bastion-BJS",
        "profile": "default",
        "region": "cn-north-1",
        "ec2id": "i-66661fooaaaaa1",
        "status": "running",
        "access_range": "myip"
    },
    {
        "name": "Bastion-ZHY",
        "profile": "default",
        "region": "cn-northwest-1",
        "ec2id": "i-66661fooaaaaa2",
        "status": "stopped",
        "access_range": "all"
    },
    {
        "name": "WinRDP",
        "profile": "oregon",
        "region": "us-west-2",
        "ec2id": "i-66661fooaaaaa3",
        "status": "running",
        "access_range": "50.11.2.0/24"
    }
]
```
* Run update-ec2-status-securitygroup.py and you can input to select "d" for dryrun or "u" for update EC2 status and Security Group rules as you describe in ec2List.json  For example:   
  运行 update-ec2-status-securitygroup.py ，可以选择 "d" 试运行，即只显示，或者 "u" 则按照 ec2List 更新EC2实例的状态和安全组规则。  
```
python update-ec2-status-securitygroup.py
>Show EC2 and SecurityGroup status(Dryrun) or Update as ec2List? (d/u)u
MYIP Address:  54.111.61.34/32

Loading EC2 List from:  /Users/myuser/Documents/myProject/ec2List.json
Checking all EC2 security group...
i-66661fooaaaaa1 running cn-north-1 Bastion-BJS
  Port: 22 [{'CidrIp': '0.0.0.0/0'}] 22
    Change SecurityGroup to MYIP: 54.222.61.34/32 ...
  Port: -1 [{'CidrIp': '0.0.0.0/0'}] -1
    Change SecurityGroup to MYIP: 54.222.61.34/32 ...

i-66661fooaaaaa2 running cn-northwest-1 Bastion-ZHY
Stopping EC2 ...
  Port: 22 [{'CidrIp': '0.0.0.0/0'}] 22
  Port: -1 [{'CidrIp': '0.0.0.0/0'}] -1

```
Now it is changing the EC2 i-66661fooaaaaa1 security group rules, and currently i-66661fooaaaaa2 is running, the tool is going to STOP it.   
本例中改变了EC2的安全组规则，并且把一个运行中的EC2 STOP关机

Notes: The tool will get your current public IP address by calling a service endpoint. You can change the code to use public aws endpoint checkip.amazonaws.com or a private setup API backed by Amazon API Gateway proxy integrated with a very simple Lambda function as below Python code:  
注意：本工具会调用一个公共服务端点来获取本机公网IP。普通用户，可以使用aws公开的服务端点 checkip.amazonaws.com 来获得公网IP。但如果你本身是 amazon 员工正在使用VPN连接，则需要访问一个自建的私有API来获取公网IP地址，否则地址是不准确的。本例中使用了 Amazon API Gateway 代理集成了一个非常简单的 Lambda 函数实现获取公网IP，Python 代码如下：  
```
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': event['requestContext']['identity']['sourceIp']
    }
```
* Every time you want to turn on some EC2 or change Security Group to only allow access by your IP, just run the update-ec2-status-securitygroup.py again.  
  每次要改变EC2状态或者安全组规则为只允许本机访问，只需要重新运行 update-ec2-status-securitygroup.py 即可