# -*- coding: utf-8 -*-

VALUE = re.compile(r'\w+\=(\S+)')
PRODUCTS = re.compile(r'spConfig.+Product\.Config\((\{.+?\})\);\s+VOLCOM_')

RE_ENCODED_FUNCTION = re.compile('var b="(.*?)"', re.DOTALL)
RE_INCAPSULA = re.compile('(_Incapsula_Resource\?SWHANEDL=.*?)"')
INCAPSULA_URL = 'http://www.volcom.com/%s'

##################################### incapsula block #####################################

def _check_and_trick_incapsula(url):

    ###---------------------------- block of helping functions ----------------------------

    def parse_cookies(jar_value):
        cookie_li = []
        for cook in jar_value:
            cookie_li.append(str(cook).split(' ')[1])
        return cookie_li

    def simpleDigest(val_str):
        res, pos = 0, 0
        while pos < len(val_str):
            res += ord(val_str[0])
            pos += 1
        return res

    def getSessionCookies(jar_value):
        cookieArray = []
        cookies = parse_cookies(jar_value)
        cName = 'incap_ses_'
        for elem in cookies:
            key = KEY.search(elem).group(1)
            value = VALUE.search(elem).group(1)
            if cName in key:
                cookieArray.append(value)
        return cookieArray

    def createCookie(value, seconds):
        expires = ''
        if seconds:
            date = datetime.utcnow() + timedelta(seconds=seconds) # days, seconds, then other fieldsself.
            expires = "; expires=" + date.ctime()  # seems "expires" value in python cookie_jar has another format
        return str(value) + expires + ';'

    def setIncapCookie(jar_value):
        res = ''
        stat_info = 'navigator=true,navigator.vendor=Google Inc.,navigator.appName=Netscape,navigator.plugins.'\
                    'length==0=false,navigator.platform=Linux x86_64,navigator.webdriver=undefined,plugin_ext=no extention,'\
                    'plugin_ext=so,ActiveXObject=false,webkitURL=true,_phantom=false,callPhantom=false,chrome=true,yandex=false,'\
                    'opera=false,opr=false,safari=false,awesomium=false,puffinDevice=false,navigator.cpuClass=false,navigator.'\
                    'oscpu=false,navigator.connection=false,window.outerWidth==0=false,window.outerHeight==0=false,window.'\
                    'WebGLRenderingContext=true,document.documentMode=undefined,eval.toString().length=33'
        try:
            cookies = getSessionCookies(jar_value)
            digests, it = [], 0
            while it < len(cookies):
                digests.append(simpleDigest(stat_info + cookies[it]))
                it += 1
            res = stat_info + ",digest=" + ','.join(map(str, digests))
        except Exception as e:
            res = stat_info + ",digest=" + urllib2.unquote(str(e).encode('utf-8'))
        cookie = createCookie(res, 20)
        return cookie

    ###---------------------------- end block of helping functions ----------------------------

    result_content = self.open_url(url)
    if 'String.fromCharCode' in result_content:
        cookie_data = self.cookie_jar
        incap_cookies = setIncapCookie(cookie_data)
        c = {'name': '___utmvc', 'value': incap_cookies, 'domain': '.volcom.com'}
        self._set_cookie(name=c['name'], value=c['value'], domain=c['domain'])  # , expires=c['expires_val'])
        img = '{0}/_Incapsula_Resource?SWKMTFSR=1&e={1}'.format('http://www.volcom.com', random())
        # need to open rhis url
        self.open_url(img)

        encoded_func = RE_ENCODED_FUNCTION.search(result_content).group(1)
        if 'nostojs' in encoded_func:
            _content = result_content
        else:
            try:
                decoded_func = ''.join([chr(int(encoded_func[i:i+2], 16)) for i in xrange(0, len(encoded_func), 2)])
            except Exception as e:
                raise e

            incapsula_params = RE_INCAPSULA.search(decoded_func).group(1)
            incap_url = INCAPSULA_URL % incapsula_params
            self.open_url(incap_url)
            _content = self.open_url(url)
    else:
        raise CaptchaException

    return _content

###########################################################################################
