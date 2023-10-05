import re
import requests

response = requests.get('https://raw.githubusercontent.com/tosaja/Nuolenna/master/sign_list.txt')
data = response.text
data.replace('ka\t𒅟','ka\t𒅗')
#location of the where you want to save the downloaded sign list
with open('','w') as f:
    f.write(data)
#location where you saved the sign list
sign_list = pd.read_csv('', sep='\t', header=None,keep_default_na=False,index_col=0)
dropped_lines = list(filter(lambda x: (x[0:3] == '...' or x[0] == '/' or x[0] == '|'),sign_list.index))
sign_list.drop(dropped_lines)

#pre-defined labels based on typical ORACC data as pos-tags
labels = ['O', 'V', 'MOD', 'AV', 'PN', 'SBJ', 'PRP', 'N', 'nan', 'CNJ', 'NU', 'IP', 'AJ', 'DET', 'DP', 'SN', 'DN', 'REL', 'RN', 'J', 'XP', 'MN', 'QP', 'WN', 'RP', 'GN', 'EN', 'PP', 'TN']
#location for file that is going to be changed, which is currently set  to be a tab-separated list with transliteration and label
txt_file_2_change = ''
with open(txt_file_2_change,'r') as f:
    text_data = f.readlines()

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
                
                if len(sign_list.loc[sign_list.index==sign.group().lower(),1]) >= 1:
                    unicode_text += sign_list.loc[sign_list.index==sign.group().lower(),1].values[0]
                else:
                    unicode_text += 'CHECK({sign_miss})'.format(sign_miss=sign.group())
                    failed.append('CHECK({sign_miss})'.format(sign_miss=sign.group()))

failed = list(set(failed))

#location of results
unicode_txt_file_directory = ''
with open(unicode_txt_file_directory,'w') as f:
    f.writelines(unicode_text)
