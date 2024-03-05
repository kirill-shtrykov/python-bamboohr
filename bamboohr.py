#!/usr/bin/env python

""" BambooHR API Client

Make requests to BambooHR API

Usage:
```python
import bamboohr

subdomain = 'example'  # This is top level domain of your BambooHR, ex.: https://example.bamboohr.com
token = 'secret_token'  # BambooHR API Token
client = bamboohr.BambooHR(subdomain, token)

# Fields you want to include to custom report
fields = [
        'id',
        'firstName',
        'lastName',
        'jobTitle',
        ...
    ]

name = 'custom'  # Report name
report = client.get_custom_report(name, fields)
```

URL: https://github.com/kirill-shtrykov/python-bamboohr
Author: Kirill Shtrykov <kirill@shtrykov.com>
Website: https://shtrykov.com
"""

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

DEFAULT_HEADERS = {'Accept': 'application/json'}

PHOTO_ORIGINAL = 'original'
PHOTO_LARGE = 'large'  # 340x340
PHOTO_MEDIUM = 'medium'  # 170x170
PHOTO_SMALL = 'small'  # 150x150
PHOTO_XS = 'xs'  # 50x50
PHOTO_TINY = 'tiny'  # 20x20

BAMBOOHR_API_URL = 'https://api.bamboohr.com/api/gateway.php'


class BambooHR:
    """ BambooHR API Client main class
    Arguments:
        - subdomain: The subdomain used to access BambooHR.
                     If you access BambooHR at https://mycompany.bamboohr.com,
                     then the companyDomain is "mycompany"
        - token: BambooHR API token
    """

    def __init__(self, subdomain: str, token: str):
        self.subdomain = subdomain
        self.auth = HTTPBasicAuth(token, 'x')  # BambooHR uses token as username and 'x' as password in basic auth

    @property
    def employees_url(self) -> str:
        """ returns employess directory API URL """
        return BAMBOOHR_API_URL + f'/{self.subdomain}/v1/employees/directory'

    @property
    def custom_report_url(self) -> str:
        """ returns custom reports API URL"""
        return BAMBOOHR_API_URL + f'/{self.subdomain}/v1/reports/custom'

    def _get_employee_url(self, employee_id: int) -> str:
        """ generates an employee API URL
        :param employee_id: an employee ID
        :return: an employee API URL
        """
        return BAMBOOHR_API_URL + f'/{self.subdomain}/v1/employees/{str(employee_id)}'

    def _get_photo_url(self, employee_id: int, size: str) -> str:
        """ generates employees photo API URL
        :param employee_id: an employee ID
        :param size: photo size
        :return: an employee photo API URL
        """
        return BAMBOOHR_API_URL + f'/{self.subdomain}/v1/employees/{str(employee_id)}/photo/{size}'

    @staticmethod
    def _raise_for_error(response: requests.Response) -> requests.Response:
        """ wrapper on HTTP response statuses """
        if response.status_code != 200:
            raise HTTPError(
                f'HTTP[{response.status_code}]: {response.reason} {response.text} for {response.url}',
                request=response.request,
                response=response
            )
        return response

    def _get(self, url: str, params: dict = None) -> requests.Response:
        """ requests GET method wrapper

        :param url: URL
        :param params: URL parameters
        :return: response
        :rtype: requests.Response
        """
        params = params if params else {}
        response = requests.get(url, params=params, headers=DEFAULT_HEADERS, auth=self.auth)
        return self._raise_for_error(response)

    def _post(self, url: str, data: dict, params: dict) -> requests.Response:
        """ requests POST method wrapper

        :param url: URL
        :param data: JSON data
        :param params: URL parameters
        :return: response
        :rtype: requests.Response
        """
        response = requests.post(url, json=data, params=params, headers=DEFAULT_HEADERS, auth=self.auth)
        return self._raise_for_error(response)

    def get_employees(self) -> dict:
        """ Gets employee directory

        :return: employees information
        :rtype: dict
        """
        url = self.employees_url
        return self._get(url).json()

    def get_employee(self, employee_id: int, fields: list = None) -> dict:
        """ Get an employee from BambooHR by ID

        :param employee_id: is an employee ID. The special employee ID of zero (0)
            means to use the employee ID associated with the API key (if any).
        :param fields: comma separated list of values taken from the official list of field names
        :return: employee information
        :rtype: dict
        """
        url = self._get_employee_url(employee_id=employee_id)
        fields = fields if fields else ['firstName', 'lastName']
        params = {
            'fields': ','.join(fields)
        }
        return self._get(url, params=params).json()

    def get_custom_report(self, title: str, fields: list, report_format: str = 'json',
                          only_current: bool = True) -> dict:
        """ Get custom report from BambooHR

        Use this method to request BambooHR generate a report.
        The custom report will return employees regardless of their status, "Active" or "Inactive".
        This differs from the UI, which by default applies a quick filter to display only "Active" employees.

        :param title: report title
        :param fields: list of fields to include in report
        :param report_format: report format. You must specify a type of either "PDF", "XLS", "CSV", "JSON", or "XML".
        :param only_current: Limits the report to only current employees.
        :return: employees information
        :rtype: dict
        """
        url = self.custom_report_url
        data = {
            'title': title,
            'fields': fields
        }
        params = {
            'format': report_format,
            'onlyCurrent': only_current
        }
        return self._post(url, data, params).json()

    def get_photo(self, employee_id: int, size: str) -> bytes:
        """ Get an employee photo from BambooHR

        :param employee_id: is an employee ID. The special employee ID of zero (0)
            means to use the employee ID associated with the API key (if any).
        :param size: size of photo 'original', 'large' - 340x340px, 'medium' - 170x170px,
            'small' - 150x150px, 'xs' - 50x50px, 'tiny' - 20x20px
        :return: employee photo
        :rtype: bytes
        """
        url = self._get_photo_url(employee_id=employee_id, size=size)
        return self._get(url).content
