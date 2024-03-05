# python-bamboohr
BambooHR API for Python 

## Install
`pip install git+https://github.com/kirill-shtrykov/python-bamboohr#egg=bamboohr`

## Usage
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
