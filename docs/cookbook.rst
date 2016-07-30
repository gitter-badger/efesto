Cookbook
========

Public API
##########
To set up a public API with Efesto:

* Create a 'public' user
* Assign read permissions to the user for the data it needs to access
* Create a 'public' eternal token for this user

Now you can use the eternal token to authenticate public, read-only requests. 

High-performance installations
##############################
If you need an high-performance installation, there are some extra steps that
you should take:

* Install falcon and peewee with cython
* Use pgbouncer
