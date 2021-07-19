import wget
import sys
import os
from bs4 import BeautifulSoup
import re
import threading

if(len(sys.argv) <= 1):
    print("usage : run.py http_address")
    exit()
elif (len(sys.argv) > 2):
    multi_thread_check = sys.argv[2]
    if(multi_thread_check.find("-m") == 0):
        multi_thread_check = multi_thread_check[2:]
        multi_thread_count = eval(multi_thread_check)
    else:
        multi_thread_count = 1
else:
    multi_thread_count = 1
print("thread count :" , multi_thread_count)
filename = os.path.basename(sys.argv[1])
if(os.path.isfile(os.path.basename(sys.argv[1]))):
    print("\nThe file existed , not downloading the file")
else:
    filename = wget.download(sys.argv[1],out=os.path.basename(sys.argv[1])[:100])
    

print()
imagelink = sys.argv[1].replace('/'+os.path.basename(sys.argv[1]),'',-1)

filereadstr = open(filename, encoding='UTF-8').read()
#print(filereadstr)

soup = BeautifulSoup(filereadstr, 'html.parser')
content = soup.find_all('article')

extract_name = str(list(content)[0])
soup2 = BeautifulSoup(extract_name, 'html.parser')
hname = str(soup2.find('h1').get_text())

extract_circle_artist = re.search('\[[^\]]*\]', hname )
if (extract_circle_artist == None):
    extract_circle_artist = hname
else:
    extract_circle_artist = extract_circle_artist.group(0)

hname_remove_artist = hname.replace(extract_circle_artist,'',-1)
hname_rmA_remove_blank = hname_remove_artist.replace(" ","",-1)

extract_circle_artist+="_"
extract_circle_artist = re.sub('[\[\]]','', extract_circle_artist )
extract_circle_artist = re.sub('[ \t]+','', extract_circle_artist )
#print(extract_circle_artist)
cleanString = re.sub('\W+.*','', hname_rmA_remove_blank )
cleanString = str(cleanString)[:50]
#print(cleanString)

final_dir_name = extract_circle_artist+cleanString
print("")
user_input = ''
if(os.path.exists(final_dir_name)):
    print("the directory {} is exist , make sure there is no file inside , exceed?(y/n)".format(final_dir_name))
    user_input = input()
else:
    print("creating a new directory {} , exceed?(y/n)".format(final_dir_name))
    user_input = input()

if user_input != 'y':
    print("leaving {}".format(sys.argv[1]))
    exit()

try:
    os.mkdir(final_dir_name)
except FileExistsError:
    pass
os.chdir(final_dir_name)
actual_name_write = open('actual_name','w', encoding='UTF-8')
actual_name_write.write(hname)
actual_name_write.close()
actual_name_write = open('actual_link','w', encoding='UTF-8')
actual_name_write.write(sys.argv[1])
actual_name_write.close()


counter = 1
downloading_list = []
for link in soup.find_all('img'):
    downloading_filename = link.get('src')
    _, file_extension = os.path.splitext(downloading_filename)
    if("http" in downloading_filename):
        downloading_list.append((downloading_filename,str(counter)+file_extension))
    else:
        downloading_list.append((imagelink + downloading_filename,str(counter)+file_extension))
    #print(str(counter)+file_extension)
    #wget.download(imagelink + downloading_filename,out=str(counter)+file_extension)
    counter+=1

#print(downloading_list)

def downloading_job(thread_download_list,total_thread,num):
    #print("hi {} {} {}".format(len(thread_download_list),total_thread,num))
    try_python_wget_or_system_wget = 0 #0 for python wget 1 for system wget
    for i in range(num,len(thread_download_list),total_thread):
        #print(num,i)
        try:
            if(try_python_wget_or_system_wget == 0):
                wget.download(thread_download_list[i][0],out=thread_download_list[i][1])
            else:
                os.system("wget -O {0} {1}".format(thread_download_list[i][1], thread_download_list[i][0]))
        except:
            try_python_wget_or_system_wget = 1
            os.system("wget -O {0} {1}".format(thread_download_list[i][1], thread_download_list[i][0]))


thread_id = []
for i in range(multi_thread_count):
    thread_id.append(threading.Thread(target=downloading_job , args= (downloading_list , multi_thread_count , i)))

for i in range(multi_thread_count):
    thread_id[i].start()

for i in range(multi_thread_count):
    thread_id[i].join()

print("\ndone ;)")
os.chdir("../")
os.remove(filename)