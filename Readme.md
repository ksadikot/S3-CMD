To run shell require S5-S3.conf where aws credentials are under [default]
To run shell - 'python shellScript.py'

Welcome to S3 File Manager!
This project is a shell script that can manage AWS S3 files.
The objectives of this project was to replicate file management system such as powershell and cmd.

**Following list of commands:**
Upload file: locs3cp '/file/path/'
Download file: s3loccp '/s3/file/path/'
Create folder: create_folder '/folder/path/'
Display current directory: cwlocn
Create S3 bucket: create_bucket 'bucketName'
Delete S3 Bucket: delete_bucket 'bucketName'
Change directory: chlocn '/new/directory/path/'
Copy object In S3: s3copy 'objectName'
Delete object in S3: s3delete 'objectName'
List S3 directory: list


Normal behaviour: 
When running script only 'ls' command is accepted to display local files  
When entering a bucket name '/' must be placed first for example: chlocn /cis4010
Use of pathlib module to handle virtual directory management of s3 location

Limitations:
Changing directories only allow you go as far as folder length. Meaning if in s3 I have path = /cis4010/folder/obj
you cannot enter into obj as it is not considered a folder by aws s3 making the farthest chlocn can take is folder/
