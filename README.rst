pimp_myGPT
======



Install
-------

Create a virtualenv and activate it::

    $ python3 -m venv .venv
    $ . .venv/bin/activate

Or on Windows cmd::

    $ py -3 -m venv .venv
    $ .venv\Scripts\activate.bat

Install pimpmygpt::

    $ pip install -e .

Or if you are using the main branch, install Flask from source before
installing pimpmygpt::

    $ pip install -e ../..
    $ pip install -e .


Run
---

.. code-block:: text

    $ flask --app pimpmygpt init-db
    $ flask --app pimpmygpt run --debug

Open http://127.0.0.1:5000 in a browser.


Test
----

::

    $ pip install '.[test]'
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
