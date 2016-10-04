# Version 0.7 (2016-10-04)

* Added an *embeds* parameter
* The _fields parameter supports comma-separated values
* Custom types support self-referencing fields
* Blueprints assume columns to be nullable by default

# Version 0.6

## Version 0.6.2 (2016-09-28)

* Various updates to documentation and setup

## Version 0.6.1 (2016-09-27)

* Improved error messages
* Fix a bug concerning attributes referencing foreign resources not being displayed
* Fix tokens generated with the default expiration regardless of configuration
* Fix on_post required the owner of an item as parameter

## Version 0.6.0 (2016-09-14)

* Add HATEOAS support using [siren](https://github.com/kevinswiber/siren) as hypermedia type
* Users have an enabled column that can be used to enable/disable them
* Authentication with tokens expects the token in the password field

# Version 0.5 (2016-08-15)

* Add blueprints to import and export custom data structures
* Custom types support float fields
* Performing a GET on a collection returns only the items' ids
* Add a _fields parameter to GET requests on collections


# Version 0.4 (2016-07-24)

* Added efesto-quickstart
* The root endpoint returns a response
* Improvements to the installation process
* Added contribution guide
* Updated falcon version in use to 1.0
* The version number is kept as internal value

# Version 0.3 (2016-04-26)

## Version 0.3.1 (2016-06-01)
Adds essential files for the distribution and configuration of Efesto.
* Add setup.py
* Add LICENSE and copyright notices

## Version 0.3.0 (2016-04-26)
* make_model supports unique columns
* Users.can allows 'create' argument

# Version 0.2

## Version 0.2.2 (2016-04-20)

* Fixed a bug in datetime serialization
* Improved installation output

## Version 0.2.1 (2016-04-19)

* Improved TokensResource
* Auth.generate_token always returns decoded tokens
* Auth.read_token reads timed and non-timed tokens

## Version 0.2.0 (2016-04-18)

* Added order by queries to collections
* Added foreign keys support to make_model
* Deleting a type raise an error if there are still items of that types
* Deleting a type drops the table

# Version 0.1 (2016-04-15)

* First release!
