API
===
Efesto will generate REST endpoints for all the custom types that have been
specified and of course for the default endpoints.

GET
###
Use get request to fetch data! In GET requests you can use query strings to
specify what exactly you want, how it should be ordered and such.

Querying
--------
To fetch items with specific attribute, you can pass the attribute,
the needed value and a comparison operator.

Querying supports *=*, *<*, *>* and *!* operators.

::

    /endpoint?my_attribute=1   # items with my_attribute equal to 1
    /endpoint?my_attribute=!1  # items with my_attribute different from 1
    /endpoint?my_attribute=>1  # items with my_attribute greater than 1
    /endpoint?my_attribute=<1  # items with my_attribute smaller than 1

You can query against string and date values exactly in the same way.

You can query against more than one parameter while combining multiple
operators::

    /endpoint?my_attribute=1&category=!flowers
    # items with my_attribute equal to 1 but with category different from 'flowers'


Ordering
--------
To order items based on the values of an attribute, use the order_by parameter.

The order_by parameter supports ascending (>) and descending (<) orderings::

    /endpoint?order_by=my_attribute  # orders items by my_attribute ascending
    /endpoint?order_by=>my_attribute # orders items by my_attribute ascending
    /endpoint?order_by=<my_attribute # orders items by my_attribute descending


.. note::

    The default order is by id, ascending


Pagination
-----------
Pagination is used to specify the subset of items that you wish to receive,
from a larger set.

With the *items* argument you specify how many items you wish::

    /endpoint?items=20 # provides up to 20 items

With the *page* argument you specify the page, or in other words, the offset::

    /endpoint?items=20&page=2 # provides up to 20 items, skips the first 20


POST
####

PATCH
#####

DELETE
######
