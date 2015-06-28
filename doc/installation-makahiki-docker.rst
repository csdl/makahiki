Docker installation of Makahiki
===============================

Install Docker
--------------

Install docker following the instructions in the `Docker installation`_ for your OS.

.. _Docker installation: https://docs.docker.com/installation/#installation

Install Compose
---------------

Install compose following the `Compose installation`_.

.. _Compose installation: https://docs.docker.com/compose/install

Download the Makahiki source
----------------------------

To download the Makahiki system, type the following::

  % git clone git://github.com/csdl/makahiki.git

This will create a directory called "makahiki" containing the source code
for the system.

Setup environment variables
---------------------------

To deploy Makahiki on Docker, you must define several environment variables that will be
used by the Docker instance. The environment variables are defined in the file .env in the
Makahiki source code root directory.

First, define a local environment variable that specifies the Makahiki admin account name and
password::

  MAKAHIKI_ADMIN_INFO=admin:Dog4Days56

Create the docker container
---------------------------

Once the above local environment variables are set, run the following command to build the container::

  % docker-compose build

This command will:
  * pull a python image to create a container
  * install the dependencies defined in requirements-docker.txt

Initialize the web container
----------------------------

Run the following command to initialize the web container::

  % docker-compose up db
  % docker-compose run web python makahiki/scripts/initialize_instance.py -t default -d

 This command will:
  * initialize the database contents and perform any needed database migrations.
  * initialize the system with data.
  * set up static files.

Start the server
----------------

To start up the server on Docker, invoke::

  % docker-compose up

Verify that Makahiki is running
-------------------------------

Open a browser and go to `http://<docker-ip>:8000`. This should retrieve the landing page, which should look like:

.. figure:: figs/guided-tour/guided-tour-landing.png
   :width: 600 px
   :align: center

Configure your Makahiki instance
--------------------------------

Now that you have a running Makahiki instance, it is time to configure it for your
challenge, as documented in :ref:`section-site-configuration`.

Updating your Makahiki instance
-------------------------------

Makahiki is designed to support post-installation updating of your configured system when bug fixes or
system enhancements become available.   Updating an installed Makahiki instance is quite
simple, and consists of the following steps.

#. Get the updated source code::

   % git pull origin master

#. Run the update_instance script to update your Heroku configuration (make sure the AWS environment variables are set)::

   % docker-compose build

#. Finally, restart your server::

   % docker-compose up
