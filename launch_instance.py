#!/usr/bin/env python

"""Launch AWS instance with Anaconda & jupyter notebook"""

from __future__ import (absolute_import, division,print_function, unicode_literals)

try:
    import pytz
    import time
    import sys
    import boto3
    from botocore.exceptions import NoRegionError, NoCredentialsError
    import subprocess
    import readline
    import os.path
    from colorama import Fore, Back, Style
except ImportError as e:
    print("\nPlease install the following Python package(s) to run the code: ",e.args[0].split()[-1])
    sys.exit(1)

def main():
    # Function to set time zone to display times according to local time
    local_tz = pytz.timezone('Europe/Berlin')
    tmax = 30 # maximum waiting time for instance launch, each unit = 10s
    def utc_to_local(utc_dt):
        local_dt = utc_dt.astimezone(local_tz)
        return local_tz.normalize(local_dt) # .normalize might be unnecessary

    # Function for pre-filled data entry
    def rlinput(prompt, prefill=''):
       readline.set_startup_hook(lambda: readline.insert_text(prefill))
       try:
          return raw_input(prompt)
       finally:
          readline.set_startup_hook()

    # Get input on instance to be launched
    print(Fore.GREEN + Style.BRIGHT + "\nInstance characteristics: \n",Style.RESET_ALL)
    in_type = rlinput(Style.BRIGHT + "Instance type: " + Style.NORMAL, "t2.micro")
    in_image = rlinput(Style.BRIGHT +"Ami ID: " + Style.NORMAL,"ami-db1688a2")
    in_security = rlinput(Style.BRIGHT + "Security group name [from those in your AWS account]: " + Style.NORMAL,"launch-wizard-2")
    in_device = rlinput(Style.BRIGHT + "Storage device mount name [e.g. xvda,sda1]: " + Style.NORMAL,"xvda")
    in_storage = rlinput(Style.BRIGHT + "Storage space: " + Style.NORMAL,"8")

    try:
        # Initialize ec2 session
        ec2 = boto3.resource('ec2')
        session = boto3.Session()
        client = boto3.client('ec2')

        # Launch instance
        print(Fore.GREEN + Style.BRIGHT + "\nLaunching instance \n" + Style.RESET_ALL)
        new_reservation = ec2.create_instances(ImageId=in_image, SecurityGroups=[in_security],InstanceType=in_type,KeyName='KeyBrushup',MinCount=1, MaxCount=1, BlockDeviceMappings=[{"DeviceName": "/dev/"+in_device, "Ebs" : { "VolumeSize" : int(in_storage) }}])

    # Catch some of the most usual errors & provide guidance
    except NoRegionError:
        print(Fore.RED + Style.BRIGHT + "\nYou must specify a region in your config files", Style.RESET_ALL + "usually at ~/.aws/config \n\nFor more information see http://boto3.readthedocs.io/en/latest/guide/configuration.html \n")
        sys.exit(1)
    except NoCredentialsError:
        print(Fore.RED + Style.BRIGHT + "\nYou must specify your AWS id and key",Style.RESET_ALL + "(e.g. obtained from an IAM role), usually specified at ~/.aws/config \n\nFor more information see http://boto3.readthedocs.io/en/latest/guide/configuration.html \n")
        sys.exit(1)

    # Wait until it has been created
    status = None
    timer=0
    while (status != u'ok'):
        try:
            if timer > tmax:
                sys.exit(Fore.RED + Style.BRIGHT + "\nToo long too start instance. Check AWS console as there may be some network issue." + Style.RESET_ALL)
            time.sleep(10)
            timer += 1
            response = client.describe_instance_status(InstanceIds=[new_reservation[0].instance_id])
            status = response["InstanceStatuses"][0]["SystemStatus"]["Status"]
            print("Instance state: %s" % status)
        except IndexError:
            pass

    print(Fore.GREEN + Style.BRIGHT + "\nInstance created \n" + Style.RESET_ALL)

    # Print list of instances in your account
    print(Fore.GREEN + Style.BRIGHT + "List of instances: \n" + Style.RESET_ALL)
    instances = client.describe_instances()
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            print("Launch Time:", utc_to_local(instance["LaunchTime"])," ID:",instance["InstanceId"]," Type:", instance["InstanceType"], " State:", instance["State"]["Name"], "\n")

    # Get IP address of the new instance
    instances = None
    timer=0
    while (instances is None):
        try:
            if timer > tmax:
                sys.exit(Fore.RED + Style.BRIGHT + "\nToo long too get IP address. Check AWS console as there may be some network issue." + Style.RESET_ALL)
            time.sleep(2)
            timer += 1
            instances = ec2.instances.filter(InstanceIds=[new_reservation[0].instance_id])
        except IndexError:
            pass

    for instance in instances:
        ip = instance.public_ip_address

    print(Fore.GREEN + "IP address newly created instance: ", ip)

    # Set up Anconda and emacs in instance
    print(Fore.GREEN + Style.BRIGHT + "\nConnecting to instance and installing data science toolkit via Anaconda" + Style.RESET_ALL)
    # AWS key pair required to connect to instance
    keypair = rlinput(Style.BRIGHT + "\nAWS key pair file (.pem)?" + Style.NORMAL,"~/Keys/")
    keypair = os.path.expanduser(keypair)

    while (not os.path.exists(keypair)) or (not keypair.lower().endswith('.pem')):
        keypair = rlinput(Fore.RED + "\nInvalid path to .pem file.\nEnter new path or \'quit\' to abort: " + Style.RESET_ALL,"")
        keypair = os.path.expanduser(keypair)
        if keypair == "quit":
            sys.exit(Fore.RED + Style.BRIGHT + "\nNo AWS key pair provided." + Style.RESET_ALL)
    # Run setup using keypair entered
    print("\n")
    subprocess.check_call(['./setup_python.sh',ip,keypair])

    # Ask user if Jupyter notebook is to be started remotely
    jnote = rlinput(Style.BRIGHT + "\nStart remote jupyter notebook? (y/n) " + Style.NORMAL,"")
    while (jnote.lower() != 'y') and (jnote.lower() != 'n'):
        jnote = rlinput(Fore.RED + "\nPlease enter \"y\" or \"n\" " + Style.RESET_ALL,"")
    # If user entered yes, launch jupyer notebook on preferred browser
    if jnote.lower() == 'y':
        browser = rlinput(Style.BRIGHT + "\nAccess remote jupyter notebook on:\n(1) Firefox\n(2) Chrome\n ? " + Style.NORMAL,"1")
        while (browser != '1') and (browser != '2'):
            jnote = rlinput(Fore.RED + "\nPlease enter \"1\" or \"2\" " + Style.RESET_ALL,"")
        if browser == '1':
            cmd = "firefox localhost:8000"
        else:
            cmd = "google-chrome http://localhost:8000"
        subprocess.check_call(['./tunnel_localhost.sh',ip,keypair,cmd])
        print(Fore.GREEN + "\n Screen created at instance (port 8888) and on this machine (port 8000).", Style.RESET_ALL)

    print(Fore.GREEN + Style.BRIGHT + "\nComplete.", Style.RESET_ALL)

if __name__ == "__main__":
    main()
