#
#  Copyright 2012 John Gerlock
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from elementtree.ElementTree import Element, SubElement
from elementtree.ElementTree import dump, tostring, fromstring
import requests


class WebToolsRequest():
    def __init__(self, user_id):
        self.user_id = user_id
        self.api_url = 'https://secure.shippingapis.com/ShippingAPI.dll'
        self.test_api_url = 'https://secure.shippingapis.com/ShippingAPITest.dll'
        self.address_fields = ('FirmName', 'Address1', 'Address2',
                               'City', 'State', 'Zip5', 'Zip4')
        self.verify_root_tag = 'AddressValidateRequest'
        self.zipcode_lookup_root_tag = 'ZipCodeLookupRequest'
        self.citystate_lookup_root_tag = 'CityStateLookupRequest'
        self.test_data = [
            {
                'address2':'6406 Ivy Lane',
                'city':'Greenbelt',
                'state':'MD'
            },
            {
                'address2':'8 Wildwood Drive',
                'city':'Old Lyme',
                'state':'CT',
                'zip5':'06371'
            }]

    def build_request_xml(self, data, root_tag):
        root = Element(root_tag, USERID=self.user_id)
        for i, address in enumerate(data):
            address_element = SubElement(root, 'Address', ID=str(i))
            for field in self.address_fields:
                SubElement(
                    address_element, field).text = address.get(field.lower())
        return tostring(root)

    def request(self, api_name, xml, test=False):
        if test:
            response = requests.get(
                self.test_api_url, params={'API': api_name, 'XML': xml})
        else:
            response = requests.get(
                self.api_url, params={'API': api_name, 'XML': xml})
        return response

    def verify(self, data):
        api_name = 'Verify'
        xml = self.build_request_xml(data, self.verify_root_tag)
        response = self.request(api_name, xml)
        return Response(response)

    def zipcode_lookup(self, data):
        api_name = 'ZipCodeLookup'
        xml = self.build_request_xml(data, self.zipcode_lookup_root_tag)
        response = self.request(api_name, xml)
        return Response(response)

    def citystate_lookup(self, data):
        api_name = 'CityStateLookup'
        xml = self.build_request_xml(data, 'CityStateLookupRequest')
        response = self.request(api_name, xml)
        return Response(response)

    def verify_test(self):
        api_name = 'Verify'
        xml = self.build_request_xml(self.test_data, self.verify_root_tag)
        response = self.request(api_name, xml)
        print response.content

    def zipcode_lookup_test(self):
        api_name = 'ZipCodeLookup'
        xml = self.build_request_xml(
            self.test_data, self.zipcode_lookup_root_tag)
        response = self.request(api_name, xml)
        print response.content

    def citystate_lookup_test(self):
        api_name = 'CityStateLookup'
        xml = self.build_request_xml(
            self.test_data, self.citystate_lookup_root_tag)
        response = self.request(api_name, xml)
        print response.content

    def make_all_test_requests(self):
        self.verify_test()
        self.zipcode_lookup_test()
        self.citystate_lookup_test()


class Response():
    def __init__(self, response):
        self.address_fields = (
            'FirmName',
            'Address1',
            'Address2',
            'City',
            'State',
            'Zip5',
            'Zip4')
        self.response = response
        self.et = self.response_to_et(self.response)
        self.check_et_errors(self.et)
        self.dict = self.build_address_dict(self.et)
        self.index = self.address_count

    def __iter__(self):
        return self

    def __getitem__(self, key):
        if self.dict.get(str(key)):
            return self.dict[str(key)]
        else:
            raise IndexError

    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]

    def dump(self):
        print self.response.status_code
        print self.response.content
        if self.et:
            dump(self.et)

    def check_respone_errors(self, response):
        if response.status_code is not 200:
            self.dump()
            raise Exception

    def response_to_et(self, response):
        return fromstring(response.content)

    def check_et_errors(self, et):
        if et.tag == 'Error':
            self.dump()
            raise Exception
        else:
            return et

    def build_address_dict(self, et):
        addresses = {}
        for address_element in et.getiterator('Address'):
            address = {}
            id = address_element.get('ID')
            address['id'] = id
            for key in self.address_fields:
                address[str(key).lower()] = address_element.findtext(key)
            addresses[id] = WebToolsAddress(address)
        return addresses

    @property
    def address_count(self):
        return len(self.et.getiterator('Address'))


class WebToolsAddress():
    def __init__(self, address):
        self.address = address

    def __str__(self):
        fields = ('firmname', 'address1', 'address2')
        add_string = ''
        for field in fields:
            if self.address[field]:
                add_string += '%s\n' % self.address[field]
        add_string += self.last_line
        return add_string

    @property
    def address(self):
        return self.address

    @property
    def address1(self):
        return self.address['address1']

    @property
    def address2(self):
        return self.address['address2']

    @property
    def city(self):
        return self.address['city']

    @property
    def state(self):
        return self.address['state']

    @property
    def zip4(self):
        return self.address['zip4']

    @property
    def zip5(self):
        return self.address['zip5']

    @property
    def address_lines(self):
        if self.address1:
            return '%s\n%s' % (self.address1, self.address2)
        else:
            return '%s' % self.address2

    @property
    def zipcode(self):
        return '%s-%s' % (self.zip5, self.zip4)

    @property
    def citystate(self):
        return '%s, %s' % (self.city, self.state)

    @property
    def last_line(self):
        return '%s %s' % (self.citystate, self.zipcode)
