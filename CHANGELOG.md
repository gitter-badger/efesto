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
