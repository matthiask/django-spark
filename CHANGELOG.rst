Change log
==========

`Next version`_
~~~~~~~~~~~~~~~

- Added a ``spark.api.event`` helper for creating events.
- Moved all imports in the ``spark.api`` module into the functions using
  them so that the module can always be imported early during startup.
- Decoupled the generators API from ``Generator`` model instances.
  Documentation will be written after some additional `real world
  testing <https://406.ch/writing/writing-documentation/>`__.
  ``events_from_generators`` now accepts a list of generator
  descriptions instead of a generator queryset. The ``.as_generators()``
  queryset method easily allows creating a suitable generator
  description.
- Separated ``EmailMessage`` generation from sending in the
  ``spark_mails`` API and made mail sending not fail silently by
  default.
- Fixed a bug where an empty template would crash the mail rendering.
- Rewrote the Travis CI configuration to make jobs explicit, added newer
  Django and Python versions to the matrix.


`0.3`_ (2018-10-29)
~~~~~~~~~~~~~~~~~~~

- Changed API events to be dictionaries instead of
  ``types.SimpleNamespace`` objects. The top level of the dictionary
  normally contains ``key`` and ``group`` keys used by django-spark and
  an additional ``context`` dictionary with arbitrary data.
- Added a new ``Event.objects.create_if_new`` queryset method which
  understands event dictionaries.
- Added a new ``spark.spark_generators`` app for configuring spark
  generators using Django's administration interface.
- Changed the API contract for sources and sinks: Sources and sinks are
  both **NOT** responsible for only letting new events through. A new
  ``spark.api.only_new_events`` filtering iterator has been added which
  only yields events that haven't been seen yet.
- Added a new ``spark.spark_mails`` app for transactional mails.


`0.2`_ (2018-10-16)
~~~~~~~~~~~~~~~~~~~

- Reformatted the code using black.
- Added a testsuite and some documentation.


`0.1`_ (2017-12-19)
~~~~~~~~~~~~~~~~~~~

- Initial public version.

.. _0.1: https://github.com/matthiask/django-spark/commit/4b8747afd
.. _0.2: https://github.com/matthiask/django-spark/compare/0.1...0.2
.. _0.3: https://github.com/matthiask/django-spark/compare/0.2...0.3
.. _Next version: https://github.com/matthiask/django-spark/compare/0.3...master
