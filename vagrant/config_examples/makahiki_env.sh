# Makahiki environment variables
# Syntax: postgres://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>
export MAKAHIKI_DATABASE_URL=postgres://makahiki:makahiki@localhost:5432/makahiki

# Syntax: <admin_name>:<admin_password>
export MAKAHIKI_ADMIN_INFO=admin:admin

# Used by settings.py to recognize that Makahiki is running in a Vagrant virtual machine
export MACHINE_IS_VAGRANT=True