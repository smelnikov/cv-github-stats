import json

import urllib.error
import urllib.parse
import urllib.request

from ghstats.api.exceptions import RateLimitExceededException, GithubException


class Requester(object):

    def __init__(self, base_url, token=None):
        self.__base_url = base_url
        o = urllib.parse.urlparse(base_url)
        self.__hostname = o.hostname
        self.__prefix = o.path
        self.__scheme = o.scheme
        self.__authorization_header = None
        if token:
            self.__authorization_header = f"token {token}"

    def request_and_check(self, verb, url):
        try:
            status, response_headers, output = self.__request_raw(verb, url)
            output = self.__structured_from_json(output)

            return response_headers, output

        except urllib.error.HTTPError as err:
            output = self.__structured_from_json(err.fp.read())

            if err.code == 403 and (
                    output.get("message").lower().startswith("api rate limit exceeded")
                    or output.get("message").lower().endswith("please wait a few minutes before you try again.")
            ):
                raise RateLimitExceededException(err.code, output)

            raise GithubException(err.code, output)

    def __request_raw(self, verb, url):
        request_headers = dict()
        self._authenticate(request_headers)

        url = self.__make_absolute_url(url)
        url = "%s://%s%s" % (self.__scheme, self.__hostname, url)

        rq = urllib.request.Request(url, method=verb.upper(), headers=request_headers)
        r = urllib.request.urlopen(rq)

        status = r.code
        response_headers = r.headers
        output = r.read()

        return status, response_headers, output

    def _authenticate(self, request_headers):
        if self.__authorization_header is not None:
            request_headers["Authorization"] = self.__authorization_header

    def __make_absolute_url(self, url):
        if url.startswith("/"):
            url = self.__prefix + url
        else:
            o = urllib.parse.urlparse(url)
            url = o.path
            if o.query != "":
                url += "?" + o.query
        return url

    def __structured_from_json(self, data):
        if len(data) == 0:
            return None
        else:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            try:
                return json.loads(data)
            except ValueError:
                return {"data": data}


class PaginatedList(object):
    def __init__(self, requester, first_url):
        self.__elements = list()
        self.__requester = requester
        self.__first_url = first_url
        self.__next_url = first_url

    def __iter__(self):
        for element in self.__elements:
            yield element
        while self._could_grow():
            new_elements = self._grow()
            for element in new_elements:
                yield element

    def _grow(self):
        new_elements = self._fetch_next_page()
        self.__elements += new_elements
        return new_elements

    def _could_grow(self):
        return self.__next_url is not None

    def _fetch_next_page(self):
        headers, data = self.__requester.request_and_check("GET", self.__next_url)
        data = data if data else []

        self.__next_url = None
        if len(data) > 0:
            links = self.__parse_link_header(headers)
            if "next" in links:
                self.__next_url = links["next"]

        content = [
            element
            for element in data
            if element is not None
        ]
        return content

    def __parse_link_header(self, headers):
        links = {}
        if "link" in headers:
            link_headers = headers["link"].split(", ")
            for linkHeader in link_headers:
                (url, rel) = linkHeader.split("; ")
                url = url[1:-1]
                rel = rel[5:-1]
                links[rel] = url
        return links
