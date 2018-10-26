Change log
==========

`Next version`_
~~~~~~~~~~~~~~~

- Changed API events to be dictionaries instead of
  ``types.SimpleNamespace`` objects. The top level of the dictionary
  normally contains ``key`` and ``group`` keys used by django-spark and
  an additional ``context`` dictionary with arbitrary data.
- Added a new ``Event.objects.create_if_new`` queryset method which
  understands event dictionaries.
- Added a new ``spark.spark_generators`` app for configuring spark
  generators using Django's administration interface.


`0.2`_ (2018-10-16)
~~~~~~~~~~~~~~~~~~~

- Reformatted the code using black.
- Added a testsuite and some documentation.


`0.1`_ (2017-12-19)
~~~~~~~~~~~~~~~~~~~

- Initial public version.

.. _0.1: https://github.com/matthiask/django-spark/commit/4b8747afd
.. _0.2: https://github.com/matthiask/django-spark/compare/0.1...0.2
.. _Next version: https://github.com/matthiask/django-spark/compare/0.2...master
