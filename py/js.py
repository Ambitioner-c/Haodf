import requests
import execjs
import re

url = 'https://zhaizhenguo.haodf.com/'
Headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36'}


def get_Jslid(response):
    cookie = response.cookies
    cookie = '; '.join(['='.join(item) for item in cookie.items()])
    print(cookie)
    return cookie


def get_Clearance(response):
    func_return = ''.join(re.findall('<script>(.*?)</script>', response.text))
    print(func_return)
    func_return = func_return.replace('eval', 'return')

    content = execjs.compile(func_return)
    eval_func = content.call('x')
    print(eval_func)

    name = re.findall(r'var (.*?)=function.*', eval_func)[0]

    mode_func = eval_func.replace('while(window._phantom||window.__phantomas){};', ''). \
        replace('document.cookie=', 'return').replace('if((function(){try{return !!window.addEventListener;}', ''). \
        replace("catch(e){return false;}})()){document.addEventListener('DOMContentLoaded',%s,false)}" % name, ''). \
        replace("else{document.attachEvent('onreadystatechange',%s)}" % name, '').replace(
        r"setTimeout('location.href=location.pathname+location.search.replace(/[\?|&]captcha-challenge/,\'\')',1500);",
        '')  

    content = execjs.compile(mode_func)
    cookies = content.call(name)
    # print(cookies)
    clearance = cookies.split(';')[0]

    return clearance


def structureHeaders(cookie, clearance):
    """
    构造新的headers
    :return:
    """

    cookie = {
        'cookie': cookie + ';' + clearance
    }
    return dict(Headers, **cookie)


if __name__ == '__main__':
    my_response = requests.get(url, headers=Headers)
    print(my_response.headers)
    print(my_response.text)

    my_Jslid = get_Jslid(my_response)
    my_Clearance = get_Clearance(my_response)
    # a = structureHeaders(my_Jslid, my_Clearance)
    # print(a)
