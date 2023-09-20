import re
import requests

# read sign list from github

response = requests.get('https://raw.githubusercontent.com/tosaja/Nuolenna/master/sign_list.txt')
data = response.text
data_lines = data.split('\n')
# we start by making a list without transliterations that begin with '...', a slash '/' or a pip '|' and it is called unicode_lines
unicode_lines = ''
for sign in range(len(data_lines)-1):
    if data_lines[sign][0:3] == '...' or data_lines[sign][0] == '/' or data_lines[sign][0] == '|':
        continue
    else:
        unicode_lines += data_lines[sign] + '\n'

# correct mistake for ka
unicode_lines = unicode_lines.replace('ka\t𒅟','ka\t𒅗')

# change text file to unicode cunefirom
# locate first the file you want to change, the assumption here is that it contains lines seperated by newlines and each line has a tab-separated label, if you don't have labels or newlines as separaters you can remove those parts
txt_file_2_change = ''
with open(txt_file_2_change,'r') as f:
    text_data = f.readlines()

# define the list of possible labels
labels = []

unicode_text = ''
failed = []
for line in text_data:
    if line == '\n':
       
        unicode_text += '\n'
    else:
        signs = re.finditer('[a-zA-Z0-9₁-₉ḫḪṣṢṭṬšŠ()\/]*[^\s\{\}\[\]\-\.|$]',line)
        for sign in signs:
            if sign.group() in labels:
                
                unicode_text += '\t{pos}\n'.format(pos=sign.group())
                
            elif sign.group() == 'x':
                
                unicode_text += 'x'
                
            else:
                if len(unicode_lines.loc[unicode_lines[0]==sign.group().lower(),1]) >= 1:
                    unicode_text += unicode_lines.loc[unicode_lines[0]==sign.group().lower(),1].values[0]
                else:
                    unicode_text += 'CHECK({sign_miss})'.format(sign_miss=sign.group())
                    failed.append('CHECK({sign_miss})'.format(sign_miss=sign.group()))

failed = list(set(failed))

unicode_txt_file_directory = ''
with open(unicode_txt_file_directory,'w') as f:
    f.writelines(unicode_text)