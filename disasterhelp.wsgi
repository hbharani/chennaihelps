import sys
activate_this = '/var/www/disasterhelp/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
sys.path.insert(0,'/var/www/disasterhelp')
from helpchennai import app as application
