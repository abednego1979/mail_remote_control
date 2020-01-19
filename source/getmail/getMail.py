# -*- coding: UTF-8 -*-
#python 3.5

import traceback
import codecs
import os, sys, string
import poplib
import email
import platform
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def guess_charset(msg):
    # 先从msg对象获取编码:
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

# indent用于缩进显示:
def print_info(msg, indent=0):
    res_list={}
    part_index=0
    if indent == 0:
        # 邮件的From, To, Subject存在于根对象上:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    # 需要解码Subject字符串:
                    value = decode_str(value)
                else:
                    # 需要解码Email地址:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
                print('%s%s: %s' % (' ' * indent, header, value))
                res_list[header]=value
    if (msg.is_multipart()):
        # 如果邮件对象是一个MIMEMultipart,
        # get_payload()返回list，包含所有的子对象:
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % (' ' * indent, n))
            print('%s--------------------' % (' ' * indent))
            # 递归打印每一个子对象:
            sub_info = print_info(part, indent + 1)
            if sub_info:
                for sub_key in sub_info.keys():
                    res_list['sub_'+sub_key] = sub_info[sub_key]
    else:
        # 邮件对象不是一个MIMEMultipart,
        # 就根据content_type判断:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            # 纯文本或HTML内容:
            content = msg.get_payload(decode=True)
            # 要检测文本编码:
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % (' ' * indent, content + '...'))
            res_list['part'+str(part_index)]=content
            part_index+=1
        else:
            # 不是文本,作为附件处理:
            print('%sAttachment: %s' % (' ' * indent, content_type))

    return res_list


host = "pop3.163.com"
username = "xxxxxxxx@163.com"

pp = poplib.POP3(host)
pp.set_debuglevel(1)
pp.user(username)
password=input('mail box password('+username+'):')
pp.pass_(password)

ret = pp.stat()
print (ret)

ret = pp.list()
#print (ret)

#'+OK 1204 261324250'
temp=ret[0]
try:
    temp=temp.decode()
except:
    pass
assert temp.split(' ')[0]=='+OK'

last_index=int(temp.split(' ')[1])

temp=ret[1][last_index-1]
try:
    temp=temp.decode()
except:
    pass
down = pp.retr(int(temp.split(' ')[0]))

enterChar=''
if platform.system() == "Windows":
    enterChar='\r\n'
elif platform.system() == "Linux":
    enterChar='\n'
else:#for mac os
    enterChar='\r'

temp=[]
for item in down[1]:
    try:
        temp.append(item.decode())
    except:
        pass
msg_content = enterChar.join(temp)

msg = Parser().parsestr(msg_content)
#print (msg)

print ('--------')
ret=print_info(msg)

print ('--------')
print (ret)

while True:
    a=input('which to get?'+'('+'/'.join(ret.keys())+')')
    if a in ret.keys():
        break

print ('get '+a)
print (ret[a])

try:
    #with open('info_file.txt', 'wb') as pf:
    with codecs.open('info_file.txt', 'w', 'utf-8') as pf:
        pf.write(ret[a])
except Exception as err:
    print ('write file fail')
    print (err)
    print(traceback.format_exc())    

print ('write file ok')


pp.quit()
