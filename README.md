Python Interface to USPS WebTools
=================================

##Description
Perform address validation, city/state, and zipcode lookups using the US Postal
Service's [WebTools API](https://www.usps.com/business/webtools.htm).

##Python Package Dependencies
* [Requests](http://docs.python-requests.org/en/v0.10.7/index.html)
* [ElementTree](http://effbot.org/zone/element-index.htm)

##Usage
Before you can make API calls, you need to
[register](https://secure.shippingapis.com/registration/) with the USPS to get a
your USERID.

Before you can make API calls, you must make API calls to the USPS testing
server, with their testing data. Here is how:

    from webtools_api import WebToolsRequest
    
    w = WebToolsRequest(user_id='YOURUSERIDHERE')
    w.verify_test()
    w.zipcode_lookup_test()
    w.citystate_lookup_test()

Once this step is complete, you must contanct the USPS via the email address
they included in your registration confirmation email. Once they response
affirmatively, you may use the API like this:

    from webtools_api import WebToolsRequest

    w = WebToolsRequest(user_id='YOURUSERIDHERE')

    addresses = [
                  { 'firmname': 'Sweetwater Tavern',
                    'address2': '400 E Congress St',
                    'city': 'Detroit',
                    'state': 'MI',
                    'zip5': '48226'},
                  { 'firmname': "Mudgie's".
                    'address2': '1300 Porter St',
                    'zip5': '48226'
                  }
                ]
    
    verified_addresses = w.verify(addresses)

This will return an array of WebToolsAddress objects which contain the
formatted and verified information, accessible like this:

    print verified_addresses[0].address2
    print verified_addresses[1].zip4

##Notes
* You may submit a maximum of 5 addresses per API call
* Each address must include either the 5 digit zipcode (zip5) field or the city
  and state fields. The verified address will include the complete address,
  with all releveant fields

