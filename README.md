#The SMArt reference EMR documentation is rapidly evolving.  If something in this document looks strange, confusing, or wrong, please ask about it:
###http://groups.google.com/group/smart-app-developers

# Repositories 
These instructions are included in each if three github repositories that you'll need in order to run the SMArt Reference EMR in your own environment:

* https://github.com/chb/smart_server.git

* https://github.com/chb/smart_ui_server.git

* https://github.com/chb/smart_sample_apps.git

# System setup

* Recent Linux installation (Kernel 2.6+).  We recommend an up-to-date version of Ubuntu, and these instructions are written from that perspective.
* Note: We recommend you do this by sudo'ing from a non-root user.  If you would like to do this as root make sure you create at least one non-root user with `useradd -m {USER}` otherwise the default locale will not be set.  This issue is most common on a new OS build.
* PostgreSQL 8.3+
<pre>
     apt-get install postgresql
</pre>

* Python 2.6 with package <tt>psycopg2</tt> and <tt>libxslt1</tt>
<pre>
    apt-get install python-psycopg2 python-libxslt1 python-librdf librdf-storage-postgresql librdf-storage-sqlite python-m2crypto python-simplejson
</pre>

* Django 1.1

    `apt-get install python-django`

# Setup Database 

You'll have the easiest time naming your database <tt>smart</tt>

* There are two ways to authenticate to PostgreSQL: use your Unix credentials, or use a separate username and password. We strongly recommend the latter, and our instructions are tailored appropriately. If you know how to use PostgreSQL and want to use Unix-logins, go for it, just remember that when you use Apache, it will usually try to log in using its username, <tt>www-data</tt>.

* in <tt>/etc/postgresql/8.4/main/pg_hba.conf</tt>, find the line that reads:

  `local     all     all        ident`

This should be the second uncommented line in your default config. Change <tt>ident</tt> to <tt>md5</tt>:

  `local     all     all        md5`

You will need to restart PostgreSQL:
<pre>
   service postgresql-8.4 restart
</pre>

* Create a PostgreSQL user for your SMArt service, e.g. "smart" and setup a password
 <pre>
 su - postgres
 createuser --superuser smart
 psql
 postgres=# \password smart
 </pre>
* Create the Database and make the smart user its owner.

  `createdb -O smart smart`

# Install openrdf-sesame (and tomcat)  
<pre>
 sudo apt-get install tomcat6
 wget http://downloads.sourceforge.net/project/sesame/Sesame%202/2.3.2/openrdf-sesame-2.3.2-sdk.tar.gz
 tar -xzvf openrdf-sesame-2.3.2-sdk.tar.gz
 sudo cp -r openrdf-sesame-2.3.2/war/* /var/lib/tomcat6/webapps/
 sudo mkdir /usr/share/tomcat6/.aduna
 sudo chown tomcat6.tomcat6 /usr/share/tomcat6/.aduna/
 sudo /etc/init.d/tomcat6 restart
</pre>

# Download, Install, and Configure SMArt Backend Server 

* get the code
<pre>
 git clone https://github.com/chb/smart_server.git
 cd smart_server
 git submodule init
 git submodule update
</pre>

* copy <tt>settings.py.default</tt> to <tt>settings.py</tt> and update it:
    * set <tt>DATABASE_USER</tt> to the username you chose, in this documentation <tt>web</tt>, and set <tt>DATABASE_PASSWORD</tt> accordingly.		
    * set <tt>APP_HOME</tt> to the complete path to the location where you've installed <tt>smart_server</tt>, e.g. <tt>/web/smart_server</tt>
    * set <tt>SITE_URL_PREFIX</tt> to the URL where your server is running, including port number  e.g. <tt>http://localhost:7000</tt>

* copy <tt>bootstrap_helpers/application_list.json.default</tt> to <tt>bootstrap_helpers/application_list.json</tt> and customize to include the apps you want.

* set things up (supplying the smart db password when prompted)
   `./reset.sh`

# Download, Install, and Configure SMArt UI Server

* get the code

<pre>
 git clone https://github.com/chb/smart_server.git/smart_ui_server.git
 cd smart_ui_server
 git submodule init
 git submodule update
</pre>

* copy settings.py.default to settings.py and update:
    * set <tt>SMART_UI_BASE</tt> to the complete path to the location where you've installed <tt>smart_ui_server</tt>, e.g. <tt>/web/smart_ui_server</tt>
    * set <tt>SMART_SERVER_LOCATION</tt>, <tt>CONSUMER_KEY</tt>, <tt>CONSUMER_SECRET</tt> appropriately to match the SMArt Server's location and chrome credentials (check your <tt>bootstrap.py</tt> BEFORE you <tt>reset.sh</tt> on the server end).

#Running the Development Servers

The Django development servers are easy to run at the prompt.

The backend server can run on localhost in the configuration given above:
<pre>
 cd /web/smart_server/
 python manage.py runserver 7000
</pre>

The UI server, if you want it accessible from another machine, needs to specify a hostname or IP address. If you want port 80, you need to be root of course:

<pre>
 cd /web/smart_ui_server/
 python manage.py runserver 0.0.0.0:7001
</pre>

#Installation of SMArt Sample Apps

* source code

 `git clone https://github.com/chb/smart_server.git/smart_sample_apps.git`

The sample apps can run on localhost in the configuration given above:

<pre>
 cd /web/smart_sample_apps/
 mkdir session
 python manage.py runserver 0.0.0.0:8001
</pre>