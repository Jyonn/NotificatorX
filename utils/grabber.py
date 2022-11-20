import json
import random
import time
import zlib
from urllib import request, parse
from urllib.parse import quote


class ResponseDict:
    def __init__(self, content, headers):
        self.content = content
        self.headers = headers


class Grabber:
    @staticmethod
    def get_normal_header(phone_agent=False):
        normal_header = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }
        if phone_agent:
            normal_header['User-Agent'] = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit" \
                                          "/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
        else:
            normal_header['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like " \
                                          "Gecko) Chrome/56.0.2924.87 Safari/537.36"
        return normal_header

    @staticmethod
    def get_form_data(data: dict):
        return parse.urlencode(data)

    @staticmethod
    def get_json_data(data: dict):
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def get_cookie_from_response(headers: list, dtype=dict):
        cookies = dict()
        for k in headers:
            if k[0].lower() == 'Set-Cookie'.lower():
                cookie = k[1]
                if ';' in cookie:
                    cookie = cookie[:cookie.index(';')]
                    key_value_splitter = cookie.index('=')
                    cookies[cookie[:key_value_splitter]] = cookie[key_value_splitter + 1:]
        if dtype == dict:
            return cookies
        if dtype == str:
            return '; '.join(['{}={}'.format(k, v) for k, v in cookies.items()])
        raise ValueError

    def __init__(self, headers=None, timeout=2000, return_dict=False, data_type='json', wait_per_request=0):
        self.headers = headers or {}
        self.timeout = timeout
        self.return_dict = return_dict
        self.data_type = data_type
        self.wait_per_request = wait_per_request

    def update_header(self, headers: dict):
        self.headers.update(headers)

    def set_wait_time(self, min_seconds=0, max_seconds=None):
        if max_seconds is None:
            self.wait_per_request = min_seconds
        else:
            self.wait_per_request = [min_seconds, max_seconds]

    def get_wait_seconds(self):
        if isinstance(self.wait_per_request, list):
            min_seconds, max_seconds = self.wait_per_request
        else:
            return self.wait_per_request
        min_milliseconds = int(min_seconds * 1000)
        max_milliseconds = int(max_seconds * 1000)
        wait_milliseconds = random.randint(min_milliseconds, max_milliseconds)
        return wait_milliseconds / 1000

    def _get_response(self, req: request.Request):
        for header in self.headers:
            req.add_header(header, self.headers[header])

        res = request.urlopen(req, timeout=self.timeout)
        headers = res.getheaders()
        gzipped = res.headers.get('Content-Encoding')  # 判断是否压缩
        compressed_data = res.read()
        res.close()

        wait_seconds = self.get_wait_seconds()
        time.sleep(wait_seconds)

        if gzipped:
            content = zlib.decompress(compressed_data, 16 + zlib.MAX_WBITS)  # 解压
        else:
            content = compressed_data

        if self.return_dict:
            return ResponseDict(
                content=content,
                headers=headers,
            )
        return content

    def get_data(self, data):
        if data is None:
            return None

        if isinstance(data, dict):
            if self.data_type == 'form':
                data = self.get_form_data(data)
            elif self.data_type == 'json':
                data = self.get_json_data(data)
            else:
                raise ValueError('default data type')
        if isinstance(data, str):
            data = data.encode()
        assert isinstance(data, bytes)
        return data

    def get(self, url, query: dict = None):
        if query:
            url += '?' + '&'.join(['{}={}'.format(quote(param), quote(query[param])) for param in query])
        req = request.Request(url, method='GET')
        return self._get_response(req)

    def post(self, url, data: dict = None):
        req = request.Request(url, data=self.get_data(data), method='POST')
        return self._get_response(req)

    def __call__(self, url, data: dict = None):
        if data:
            return self.post(url, data)
        return self.get(url)
