import time
import hmac
import hashlib
import requests
import json
import urllib.parse

from writing_center import app


class WSAPIController:

    # This method helps us get WSAPI info that's behind HMAC Auth
    def get_hmac_request(self, path):
        path_and_query = path + '?TIMESTAMP=' + str(int(time.time())) + '&ACCOUNT_ID=labs'
        host = app.config['WSAPI_URL']
        sig = hmac.new(bytes(app.config['WSAPI_SECRET'], 'utf-8'), digestmod=hashlib.sha1,
                       msg=bytes(path_and_query, 'utf-8')).hexdigest()
        req = requests.get(host + path_and_query, headers={'X-Auth-Signature': sig})
        req_info = json.loads(req.content)
        return req_info

    def get_roles_for_username(self, username):
        path = '/username/{0}/roles'.format(username)
        return self.get_hmac_request(path)

    def get_student_courses(self, username):
        path = '/username/{0}/courses'.format(username)
        return self.get_hmac_request(path)

    def get_username_from_name(self, first_name, last_name):
        # First and last name are encoded with a % on each side so that we can search for any users that match
        first_name = urllib.parse.quote('%' + first_name + '%')
        last_name = urllib.parse.quote('%' + last_name + '%')
        path = '/username/find/{0}/{1}'.format(first_name, last_name)
        return self.get_hmac_request(path)

    def get_names_from_username(self, username):
        path = '/username/{0}/names'.format(username)
        return self.get_hmac_request(path)

    def get_pseo_status(self, username):
        path = '/username/{0}/pseo'.format(username)
        response = self.get_hmac_request(path)
        result = response.get('0')
        if result:
            if result["pseo"] == 'Y':
                return True

        return False
