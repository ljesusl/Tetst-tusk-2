import filecmp
import os , sys
import threading
from time import sleep
import shutil
from stat import *
import subprocess
import keyboard
from datetime import datetime


# file attribute extraction function
def scan_Atrib(src):
    com = f'attrib "{src}"'
    proc = subprocess.Popen(com, shell=True, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    out = str(out)
    return out[2],out[5],out[6],out[7] 

# file attribute setting function
def load_Atrib(src,dst):
    dst_atrib = scan_Atrib(src)
    atr = ''
    for i in dst_atrib:
        if i != ' ': atr += ' +' + i
    if atr == '': atr = ' -a -s -h -r'
    com = f'attrib "{dst}"{atr}'
    os.system(com)

# log recording function
def log(text,file,dir):
    d = datetime.now().date()
    d1 = datetime.now().time().isoformat(timespec='seconds')
    dir = dir.rsplit("/",1)[0]
    message = f'{d} {d1} : {text} {file} in {dir}'
    print(message)
    f = open(log_file, 'a')
    f.write(message + '\n')
    f.close()
    

# item copy function
def copy(dir1,dir2,list):
    for i in list:
        src = dir1 + '/' + i
        dst = dir2 + '/' + i

        if os.path.isfile(dst): os.remove(dst)

        if os.path.isfile(src): 
            shutil.copy2(src, dst) 
            log("Create file",i,dir2)
        else: 
            shutil.copytree(dir1 + '/' + i, dir2 +'/'+ i)
            log("Create directory",i,dir2)
        load_Atrib(src, dst)
    

# function for checking the identity of files in a directory
def compare(dir1,dir2):

    dc = filecmp.dircmp(dir1, dir2)

    for i in dc.right_only:               # deletete trash -----------------------------------
        if os.path.isfile(dir2 +"/"+ i): 
            os.remove(dir2 +"/"+ i)
            log("Dellete file",i,dir2)
        else: 
            shutil.rmtree(dir2 +"/"+ i)
            log("Dellete directory",i,dir2)
        
    match, mismatch, errors = filecmp.cmpfiles(dir1, dir2, dc.common_files)

    for i in match:                      # checking the attributes of identical files --------------------------------
        src = dir1 + '/' + i
        dst = dir2 + '/' + i
        load_Atrib(src, dst)

    copy(dir1,dir2,mismatch)             # replacing mismatched files -------------------------------------

    copy(dir1,dir2,dc.left_only)         # copy unique files from source directory ---------------------------------------------

    if dc.common_dirs:                   # scanning files in subdirectories ----------------------------------
        for i in dc.common_dirs:
            src = dir1 + '/' + i
            dst = dir2 + '/' + i
            load_Atrib(src, dst)
            compare(src,dst)
    else: return
        
    # -------------- this not work for hidden and system files
            # shutil.copymode(dir1 + '/' + i, dir2 +"/"+ i)
            # shutil.copystat(dir1 + '/' + i, dir2 +"/"+ i)
    # --------------
            # src = dir1 + '/' + i
            # dst = dir2 + '/' + i
            # com = 'echo F|xcopy /h /y "' + src + '" "' + dst + '"'
            # os.system(com)
    #---------------

def main():

    global log_file, time
    
    print('Enter the location of the first directory: ')
    while True:
        dir1 = input()
        dir1 =os.path.abspath(dir1).replace('\\','/')
        if os.path.isdir(dir1): break
        else: print('Directory not found. Enter the location again: ')

    print('Enter the location of the second directory: ')
    while True:
        dir2 = input()
        dir2 = os.path.abspath(dir2).replace('\\','/')
        if os.path.isdir(dir2): break
        else: print('Directory not found. Enter the location again: ')

    print( 'Enter sync interval(on hour): ')
    while True:
        try:
            time = float(input())
            break
        except ValueError:
            print('This value does not fit. Enter the correct interval: ')

    print('Enter the location of the log file: ')
    while True:
        log_file = input()
        log_file = os.path.abspath(log_file).replace('\\','/')
        if os.path.exists(log_file): break
        else: 
            try:
                f = open(log_file, 'a')
                f.close()
                break
            except ValueError:
                print('This path is not suitable. Enter the location again: ')

    # if os.path.isfile(log_file): os.remove(log_file) # clear log file ---------------------------

    f = open(log_file, 'a')
    f.write(f'\n------------------------ log {datetime.now().date()} {dir1} --> {dir2} ------------------------\n')
    f.close()
    
    while True:
        print( f'Directory {dir1} and directory {dir2} synchronization started')

        if os.path.exists(dir1) == False:
            print('Host directory not found! ')
            break 
        if os.path.exists(dir2): compare(dir1,dir2)
        else: 
            shutil.copytree(dir1, dir2)            
            file = dir2.replace(dir2.rsplit("/",1)[0],"").replace("/","")
            log("Create directory",file,dir2)
        sleep(time*3600)
        

if __name__ == "__main__":
    main()