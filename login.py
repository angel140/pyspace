# -*- coding: utf-8 -*-
 
import re;
import sys;
import http.cookiejar;
import urllib;
import optparse;
import json;


reload(sys)
sys.setdefaultencoding('utf8');

def Login():
 
    cj = cookielib.CookieJar();
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj));
    urllib2.install_opener(opener);
 
    print ("--------------[step1] to get cookie");
    Url = "https://kyfw.12306.cn/otn/login/init";
    resp = urllib2.urlopen(Url);
    for index, cookie in enumerate(cj):
        print ('[',index, ']',cookie);

     
    print ("--------------[step2] to get code");
    Url2 = "https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand";
    resp2 = urllib2.urlopen(Url2);

    #respInfo2 = resp2.info();
    #print "respInfo=",respInfo2;

    with open("code.png", "wb") as image:
        image.write(resp2.read())
        
    codeStr = sys.stdin.readline();
    codeStr = codeStr[:-1]
    
    print ("--------------[step3] to check code");
    ajax_url = "https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn";
    dc = {
        'randCode'      :  codeStr,
        'rand'      : "sjrand"
    };
    request = urllib2.Request(ajax_url, urllib.urlencode(dc))
    request.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
    request.add_header('X-Requested-With','XMLHttpRequest')
    request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    request.add_header('Referer','https://kyfw.12306.cn/otn/login/init')
    request.add_header('Accept','*/*')
    request.add_header('Accept-Encoding','gzip, deflate')

    f = urllib2.urlopen(request) 
    print(f.read())


    print ("--------------[step4] to login");
    LoginUrl = "https://kyfw.12306.cn/otn/login/loginAysnSuggest";
    dc = {
         'randCode'      :  codeStr,
         'userDTO.password'     : "140_226",
        'loginUserDTO.user_name': "angel140"
    };
    req = urllib2.Request(LoginUrl, urllib.urlencode(dc));
    req.add_header('Content-Type', "application/x-www-form-urlencoded");
    req.add_header('X-Requested-With','XMLHttpRequest');
    req.add_header('Origin','https://kyfw.12306.cn');
    req.add_header('Referer','https://kyfw.12306.cn/otn/login/init');
    req.add_header('Accept','*/*');
    req.add_header('Accept-Encoding','gzip, deflate');
    req.add_header('Connection','keep-live');
    request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    resp = urllib2.urlopen(req);
    print(resp.read().encode('gb18030'));


    LoginingUrl = "https://kyfw.12306.cn/otn/login/userLogin";
    req = urllib2.Request(LoginingUrl, "");

    print ("--------------[step5] to QueryUserInfo");
    LoginingUrl = "https://kyfw.12306.cn/otn/modifyUser/initQueryUserInfo";
    req = urllib2.Request(LoginingUrl, "");
    resp = urllib2.urlopen(req);
    info = resp.read();
    print(resp.read().encode('gb18030'));

 
if __name__=="__main__":
    Login();

