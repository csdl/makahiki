Heroku installation of Makahiki
===============================

Install Heroku
--------------

Sign up for an account and install the Heroku toolbelt following
the instructions in the `Heroku Cheat Sheet`_

.. _Heroku Cheat Sheet: http://devcenter.heroku.com/articles/quickstart

This involves:
  * Signing up with the Heroku service
  * Install the Heroku Toolbelt (provides the "git" and "heroku" commands).
  * Logging in to Heroku.

Add your SSH keys to Heroku
---------------------------

You must tell Heroku about your SSH keys. Follow
https://devcenter.heroku.com/articles/keys to upload your keys to Heroku.

Verifying your Heroku account
-----------------------------
Heroku provides many `addons <https://addons.heroku.com/>`_ to enhance and manage the apps deployed in Heroku.
Makahiki use the free `Memcache <https://addons.heroku.com/memcache>`_ addon on Heroku for performance enhancement.
In order to use any addons, even the free ones, Heroku requires to verify your account by providing your credit card
info. The verification process is free and no charge will be made as long as you don't use the paid addons or exceed
your app's free resource usage allowance. See more about Heroku billing at: https://devcenter.heroku.com/categories/billing

Follow `Account Verification <https://devcenter.heroku.com/articles/account-verification>`_ page to verify your account.

If you don't verify your Heroku account, Makahiki will not be able to use Memcache and the "initialize_instance"
step later will fail to add the "Memcache" addon to your heroku instance.

Setup Amazon S3
---------------
Makahiki on Heroku use Amazon S3 to store static files and support file/image upload due to the limitation of Heroku's `Ephemeral filesystem`_ in hosting static assets. You will need to set up the Amazon S3 for serving the static files in Makahiki heroku instance.

Follow `Using AWS S3 to store static assets <https://devcenter.heroku.com/articles/s3>`_ for details to setup the Amazon S3.

Create a S3 bucket to be used for storing the static files for Makahiki, and record the bucket name you created, the AWW access key id, and the AWS secret access key for use in setting up the environment variables for Heroku.

.. note:: You will need to sign up for an AWS S3 account with Amazon if you don't have one. AWS S3 is not a free service and requires a credit card. But if you are a new AWS customer, you can sign up for the `AWS Free Usage Tier <http://aws.amazon.com/free/>`_ which will be free for one year. And in general, the charge to S3 after the free period is very inexpensive.

.. _Ephemeral filesystem: https://devcenter.heroku.com/articles/dynos#ephemeral-filesystem

Setup environment variables
---------------------------

To deploy Makahiki on Heroku, you must define several local environment variables that will be
used by the initialize_instance script when it configures the Heroku instance.

First, define a local environment variable that specifies the Heroku Makahiki admin account name and
password::


  % export MAKAHIKI_ADMIN_INFO=admin:Dog4Days56

You will also need to define Amazon S3 information::

  % export MAKAHIKI_AWS_ACCESS_KEY_ID=<AWS access key id>
  % export MAKAHIKI_AWS_SECRET_ACCESS_KEY=<AWS secret access key>
  % export MAKAHIKI_AWS_STORAGE_BUCKET_NAME=<AWS S3 bucket name>

You should have obtained these values in the previous "Setup S3" section.

Download the Makahiki source
----------------------------

To download the Makahiki system, type the following::

  % git clone git://github.com/csdl/makahiki.git

This will create a directory called "makahiki" containing the source code
for the system.


Initialize Makahiki
-------------------

Once the above local environment variables are set, you can use the initialize_instance
script to create a Heroku application
and initialize the application with the default Makahiki data set. All Heroku application
names must be unique, so if your organization is "hpu", then you might call your
application "makahiki-hpu". Use an application name appropriate for your organization.

To initialize your heroku application (for example, "makahiki-hpu") with the default Makahiki data set, you need to first activate the Makahiki virtual environment and invoke the initialize_instance.py script, similar to the following::

  % workon makahiki
  % cd makahiki
  % scripts/initialize_instance.py --type default --heroku makahiki-hpu

This command will:
  * create the application in Heroku
  * install Heroku Memcache addons
  * set up the Makahiki environments you defined for the application
  * upload the Makahiki source code to Heroku
  * install and/or update all Python packages required by Makahiki
  * initialize the database contents and perform any needed database migrations.
  * initialize the system with data.
  * set up static files.

This command will produce lots of output and may take more than 20 minutes to upload Makahiki to
Heroku, depending on your network.  After uploading Makahiki you will have to answer 'Y' to the question
"Do you wish to continue (Y/n)?" during the process.

.. warning:: initialize_instance will delete any Makahiki challenge configuration actions!

   The initialize_instance script should be run only a single time in production
   scenarios, because any subsequent challenge configuration will be lost if initialize_instance is
   invoked again. Instead, use update_instance (discussed below) after performing configuration in the
   production environment.

.. note:: In an development environment, it is ok to run the initialize_instance multiple times provided that you
   understand the process will delete your pre-existing instance. In the case that you did not verify the Heroku account
   or did not setup S3 correctly, the script will fail. You could run the "initialize_instance" script again after
   you verify the account and/or fix the S3 setup.

   If you run the script a second time with the same heroku app name, you may see an error message saying that the
   heroku application had already been created and the Memcache addon already installed. You can ignore this error
   message.

Start the server
----------------

To start up the server on Heroku, invoke::

  % heroku ps:restart --app makahiki-hpu

Verify that Makahiki is running
-------------------------------

Open a browser and go to `http://<heroku-appname>.herokuapp.com/` (where <heroku-appname> is
replaced by your app's name, for example, makahiki-hpu).  This should retrieve the landing page, which should look like:

.. figure:: figs/guided-tour/guided-tour-landing.png
   :width: 600 px
   :align: center


(Optional) Enable SSL
---------------------
To enable SSL for the Heroku app, run::

  % heroku addons:add ssl

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

   % cd makahiki
   % scripts/update_instance.py --heroku makahiki-hpu

#. Finally, restart your server::

     % heroku ps:restart --app makahiki-hpu
