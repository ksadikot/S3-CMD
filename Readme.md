To run shell require S5-S3.conf where aws credentials are under [default]
To run shell - 'python shellScript.py'



Normal behaviour: 
When running script only 'ls' command is accepted to display local files 
All commands listed in assignment description are followed. 
When entering a bucket name '/' must be placed first for example: chlocn /cis4010
Use of pathlib module to handle virtual directory management of s3 location

Limitations:
Changing directories only allow you go as far as folder length. Meaning if in s3 I have path = /cis4010/folder/obj
you cannot enter into obj as it is not considered a folder by aws s3 making the farthest chlocn can take is folder/
