#!/usr/bin/env python3
#
#  Libraries and Modules
#
import configparser
import os 
import sys 
import pathlib
import boto3
import re

#Introduction message
print( "Welcome to the AWS S3 Storage Shell (S5)" )

# Get aws credentials and set s3 virtual location
config = configparser.ConfigParser()
config.read("S5-S3.conf")
aws_access_key_id = config['default']['aws_access_key_id']
aws_secret_access_key = config['default']['aws_secret_access_key']
s3_path = pathlib.PurePosixPath("/")

# Replicates ls command by listing current files and directories in current location
def ls_command():
    # Get current directory
    current_dir = os.getcwd()
    print(current_dir)

    files = os.listdir(current_dir)
    for file in files:
        print(file)

# Uploads file from local directory to specified cloud path
def upload_file(user_input, s3):
    try:
        cmdName, localPath, cloudPath = user_input.split(' ')

        localPath = localPath.replace('/', '\\')
        
        match = re.search(r'/([^/]+)/(.*)', cloudPath)
        bucket_name = match.group(1)
        path = match.group(2)

        s3.upload_file(localPath, bucket_name, path)

        print("Successfully uploaded file: " + localPath + " to s3 path: " + cloudPath)

    except:
        print("ERROR: Unable to copy local file, check local path or bucket name")

# Downloads file from a specific s3 location into a specific local directory 
def download_file(user_input, s3):
    try:
        cmdName, cloudPath, localPath = user_input.split(' ')

        if len(s3_path.parts) > 1 :
            
            bucket_name = s3_path.parts[1]
            dir = pathlib.PurePosixPath("")
            dir = dir.joinpath(*s3_path.parts[2:])

            for path in cloudPath.split("/"):
                dir = dir.joinpath(path)
            
            cloudPath = str(dir)
            
        else:
            match = re.search(r'/([^/]+)/(.*)', cloudPath)
            bucket_name = match.group(1)
            cloudPath = match.group(2)            

        localPath = localPath.replace('/', '\\')
        print("Bucket: " + bucket_name + " full cloud path: " + cloudPath + " local path: " + localPath)

        s3.download_file(bucket_name, cloudPath, localPath)


    except:
        print("ERROR: Unable to copy cloud file, check local path or bucket name")
    
# Creates s3 bucket 
def create_bucket(user_input, s3):

    try:
        cmdName, bucketName = user_input.split(' ')
        bucketName = bucketName.lstrip('/')
        
        s3.create_bucket(Bucket=bucketName, CreateBucketConfiguration={'LocationConstraint': 'ca-central-1'})

        print("Successfully created s3 bucket: ", bucketName)
        
    except:
        print("ERROR: Could not create s3 bucket " + bucketName +", check bucket name")

# Creates object within s3 environment
def create_folder(user_input, s3):
    try:
        cmdName, directory = user_input.split(' ')
        global s3_path

        if len(s3_path.parts) > 1 :

            bucket_name = s3_path.parts[1]
            dir = pathlib.PurePosixPath()
            dir = dir.joinpath(*s3_path.parts[2:])

            for path in directory.split("/"):
                dir = dir.joinpath(path)

            directory = str(dir)  
        else:
            match = re.search(r'/([^/]+)/(.*)', directory)
            bucket_name = match.group(1)
            directory = match.group(2)            

        print("Bucket: " + bucket_name + " directory path: " + directory)

        s3.put_object(Bucket=bucket_name, Key=directory)
        print("successfully created directory " + directory + " in bucket " + bucket_name)

    except:
        print("ERROR: Unable to create directory, check bucket name")

# change current s3 space
def change_directory(user_input, s3):
    try:
        cmdName, directoryChange = user_input.split(' ')
        global s3_path

        if directoryChange == "/" or directoryChange == "~":
            s3_path = pathlib.PurePosixPath("/")
        elif directoryChange.startswith(".."):
            
            for x in range(directoryChange.count("..")): 
                s3_path = s3_path.parent
                
        else: 
            for path in directoryChange.split("/"):
                s3_path = s3_path.joinpath(path)
            
            bucket_name = s3_path.parts[1]
            dir = pathlib.PurePosixPath()
            dir = dir.joinpath(*s3_path.parts[2:])
            str_dir = str(dir) + "/"

            try:
                s3.head_bucket(Bucket=bucket_name)
            except:
                print(f"Bucket {bucket_name} does not exist")
                s3_path = pathlib.PurePosixPath("/")
            
            if (len(s3_path.parts) > 2):
                try:
                    response = s3.list_objects(Bucket=bucket_name, Prefix=str_dir)

                    if 'Contents' not in response:
                        raise e
                    
                except Exception as e:
                    print(f"Object {dir} does not exist in bucket {bucket_name} (message: {str(e)}")
                    s3_path = pathlib.PurePosixPath("/")
            
                    
    except Exception as e:
        print("ERROR: could not change directory {Message: " + str(e) + "}")
    
# list current s3 space
def list_directory(user_input, s3):
    try:

        global s3_path
        paths = ""
        long = False 

        for length in user_input.split(" "):
            if length == "-l":
                long = True
            elif length.startswith("/"):
                paths = length



        if len(s3_path.parts) == 1 and paths == "" or paths =="/":

            response = s3.list_buckets()

            if 'Buckets' in response:
                for bucket in response['Buckets']:
                    if long:
                        print(bucket["Name"] + ", " + str(bucket["CreationDate"]))
                    else:
                        print(bucket["Name"])
            else:
                print("No buckets in root, create bucket using create_bucket command")

        elif len(s3_path.parts) > 1 and paths != "":

            for path in paths.split("/"):
                new_s3_path = s3_path.joinpath(path)

            bucket_name = new_s3_path.parts[1]
            dir = pathlib.PurePosixPath()
            dir = dir.joinpath(*new_s3_path.parts[2:])
            str_dir = str(dir) + "/"

            response = s3.list_objects(Bucket=bucket_name, Prefix=str_dir)

            if "Contents" in response:
                for object in response["Contents"]:
                    if long:
                        print(object["Key"] + ", " + str(object["LastModified"]) + ", " + str(object["Size"]))
                    else:
                        print(object["Key"])
            else:
                print("no objects in directory")

        elif len(s3_path.parts) > 1 and paths == "":

            bucket_name = s3_path.parts[1]
            str_dir = ""

            if len(s3_path.parts) > 2:
                dir = pathlib.PurePosixPath()
                dir = dir.joinpath(*s3_path.parts[2:])
                str_dir = str(dir) + "/"

            response = s3.list_objects(Bucket=bucket_name, Prefix=str_dir)

            if "Contents" in response:
                for object in response["Contents"]:
                    if long:
                        print(object["Key"] + ", " + str(object["LastModified"]) + ", " + str(object["Size"]))
                    else:
                        print(object["Key"])
            else:
                print("no objects in directory")

        elif len(s3_path.parts) == 1 and paths != "":
            
            curr_path = pathlib.PurePosixPath(paths)
            key_dir = pathlib.PurePosixPath()
            bucket_name = curr_path.parts[1]
            key_dir = key_dir.joinpath(*curr_path.parts[2:])
            str_dir = str(key_dir) + "/"

            if str_dir == "./":
                response = s3.list_objects(Bucket=bucket_name)
            else:
                response = s3.list_objects(Bucket=bucket_name, Prefix=str_dir)
            

            if "Contents" in response:
                for object in response["Contents"]:
                    if long:
                        print(object["Key"] + ", " + str(object["LastModified"]) + ", " + str(object["Size"]))
                    else:
                        print(object["Key"])
            else:
                print("no objects in directory")
        
    except Exception as e:
        print(f"Could not list directory (message: {e}")


# copy s3 object from one cloud location to another 
def copy_object(user_input, s3):
    try: 
        cmd, fromSource, toSource = user_input.split(" ")
        global s3_path
        full_dir = pathlib.PurePosixPath()
        full_dir = full_dir.joinpath(*s3_path.parts[1:])
        sourceKey = pathlib.PurePosixPath()

        for source in toSource.split("/"):
            full_dir = full_dir.joinpath(source)  

        bucket_name = full_dir.parts[0]
        sourceKey = sourceKey.joinpath(*full_dir.parts[1:])

        s3.copy_object(Bucket=bucket_name, CopySource=fromSource, Key=str(sourceKey) )

        print("successfully copied files")
    except Exception as e:
        print(f"could not copy object (message: {str(e)})")


# delete s3 object
def delete_object(user_input, s3):
    try:
        cmd, deletePath = user_input.split(" ")
        global s3_path
        full_dir = pathlib.PurePosixPath()
        full_dir = full_dir.joinpath(*s3_path.parts[1:])
        deleteKey = pathlib.PurePosixPath()

        for source in deletePath.split("/"):
            full_dir = full_dir.joinpath(source)  

        bucket_name = full_dir.parts[0]
        deleteKey = deleteKey.joinpath(*full_dir.parts[1:])

        s3.delete_object(Bucket=bucket_name, Key=str(deleteKey))

        print("deletion successful")
    except Exception as e:
        print(f"Could not delete object (message: {str(e)}")

# delete s3 bucket
def delete_bucket(user_input, s3):
    try:
        cmd, bucket = user_input.split(" ")
        global s3_path

        temp, bucket_name = bucket.split("/")

        if str(s3_path).__contains__(bucket_name):
            s3_path = pathlib.PurePosixPath("/")

        s3.delete_bucket(Bucket=bucket_name)

        print("successfully delete bucket")
    except Exception as e:
        print(f"Could not delete bucket (message: {str(e)}")


try:
#
#  Establish an AWS session
#
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
#
#  Set up client and resources
#
    s3 = session.client('s3')
    s3_res = session.resource('s3')

    print ( "You are now connected to your S3 storage" )

    while True:
        user_input = input("S5> ")
        
        if user_input.startswith("locs3cp"): upload_file(user_input, s3)

        if user_input.startswith("s3loccp"): download_file(user_input, s3)

        if user_input.startswith("create_folder"): create_folder(user_input, s3)

        if user_input == "cwlocn": print(s3_path)

        if user_input.startswith("create_bucket"): create_bucket(user_input, s3)

        if user_input.startswith("chlocn"): change_directory(user_input, s3)

        if user_input.startswith("s3copy"): copy_object(user_input, s3)

        if user_input.startswith("s3delete"): delete_object(user_input, s3)

        if user_input.startswith("delete_bucket"): delete_bucket(user_input, s3)

        if user_input.startswith("list"): list_directory(user_input, s3)

        if user_input == "ls": ls_command()
        
        if user_input == "exit" or user_input == 'quit':
            break

except:
    print ( "You could not be connected to your S3 storage" )
    print( "Please review procedures for authenticating your account on AWS S3" )


