# Dropzone Action Info
# Name: OSS
# Description: Upload images to aliyun OSS
# Handles: Files
# Creator: zousandian
# URL: https://github.com/zousandian
# OptionsNIB: ExtendedLogin
# Events: Clicked, Dragged
# KeyModifiers: Command, Option, Control, Shift
# SkipConfig: No
# RunsSandboxed: No
# Version: 1.0
# MinDropzoneVersion: 3.5

import os
import sys
import commands
import shutil
import uuid
import imghdr
import webbrowser
import oss2

reload(sys)
sys.setdefaultencoding('utf8')

bucket_name = os.environ['server'].split('.')[0]
endpoint = os.environ['server'].split(bucket_name + '.')[1]
try:
  remote_path = os.environ['remote_path']
  remote_path = remote_path[1:] if remote_path[0] == '/' else remote_path
except Exception,e:
  remote_path = ''
auth = None

def getAuth():
    global auth
    if auth != None:
        return query
    access_key = os.environ['username']
    secret_key = os.environ['password']
    auth = oss2.Auth(access_key, secret_key)
    return auth

#def isFileExist(file_name):
#    q = getAuth()
#    # check if file already exist
#    endpoint = os.environ['server']
#    bucket_name = os.environ['remote_path']
#    bucket = oss2.Bucket(getAuth(), endpoint, bucket_name)
#    ret, info = bucket.stat(bucket_name, file_name)
#    if ret != None:
#        return True
#    else:
#        return False

def uploadFile(file_path, file_name):
    auth = getAuth()

#    if isFileExist(file_name):
#        dz.fail("Filename already exist")

    print remote_path, endpoint, bucket_name, remote_path + file_name
    
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    ret = bucket.put_object_from_file(remote_path + file_name, file_path)
    
    if ret.status == 200:
        root_url = os.environ.get('root_url', '')
        bucket_domain = root_url.split(',')[0]
        style = ''
        try:
          style = root_url.split(',')[1]
        except Exception,e:
          print e
          pass
        
        print style
        base_url = 'http://%s/%s' % (bucket_domain, remote_path + file_name)
        if style:
          base_url += '?x-oss-process=style/' + style.strip()

        # copy file to local path as backup
#        if 'remote_path' in os.environ:
#            dest_path = '%s/%s' % (os.environ['remote_path'], file_name)
#            shutil.copyfile(file_path, dest_path)

        return base_url
    else:
        return False

def dragged():
    dz.begin("Starting uploading...")
    dz.determinate(True)
    dz.percent(10)
    
    # keep origin name
    file_path = items[0]
    file_name = os.path.basename(file_path)
    base_url  = uploadFile(file_path, file_name)

    if base_url:
        dz.finish("Upload Completed")
        dz.percent(100)
        dz.url(base_url)
    else:
        dz.fail("Upload Failed")
        dz.percent(100)
        dz.url(False)
 
def clicked():
    dz.percent(10)

    file_path = dz.temp_folder() + '/oss_img_cache'
    current_path = os.path.dirname(os.path.realpath(__file__))
    command = '"%s/pngpaste" "%s"' % (current_path, file_path)
    status, output = commands.getstatusoutput(command)
    if (status != 0):
        webbrowser.open("https://oss.console.aliyun.com")
        dz.fail(output)

#    inputs = dz.cocoa_dialog('standard-inputbox --title "Filename Required" --e --informative-text "Enter filename without suffix:"')
#    inputs = inputs.split("\n")
#    if not inputs[1]:
#        file_name = str(uuid.uuid4())
#    else:
#        file_name = inputs[1]

    file_name = str(uuid.uuid4())
    file_name = file_name + '.' + imghdr.what(file_path)

#    while True:
#        if isFileExist(file_name):
#            file_name = dz.inputbox("Filename already exist", "Enter filename without suffix:")
#            file_name = file_name + '.' + imghdr.what(file_path)
#        else:
#            break

    dest_path = '%s/%s' % (os.path.dirname(file_path), file_name)
    shutil.move(file_path, dest_path)

    dz.begin("Starting uploading...")
    dz.determinate(True)

    base_url = uploadFile(dest_path, file_name)
    if (base_url):
        dz.finish("Upload Completed")
        dz.percent(100)
        dz.url(base_url)
    else:
        dz.fail("Upload Failed")
        dz.percent(100)
        dz.url(False)
