================
The War: Latency
================

This is a **draft** implementation of simple game written in Twisted.
In order to try it, install requirements and run ``warserver.py``.

.. code-block:: console

    $ pip install -r requirements.txt
    $ twistd --nodaemon --python warserver.py

Now you can connect to server by telnet.

.. code-block:: console

    $ telnet
    telnet> open localhost 6666
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    Hi! I'm trying to find an opponent for you.

Tests
-----

You can run tests by invoking ``trial``:

.. code-block:: console

    $ trial tests
