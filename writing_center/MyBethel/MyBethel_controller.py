import os
import sys

from flask import abort
from functools import wraps

from writing_center.db_repository.db_connection_bw import conn_bw
from writing_center import app


class MyBethelController:

    def get_results(self, result, label="", type=None):
        ret = {}
        for i, row in enumerate(result):
            row_dict = {}
            for item in row:
                if isinstance(item, bytes) or isinstance(item, str):
                    item = item.split(":", 1)
                else:
                    # blob
                    item = item.read()
                if len(item) > 1:
                    row_dict[item[0]] = item[1]
                else:
                    # if the result set doens't have key / value pairs
                    # use a custom label
                    row_dict[label] = item[0]

            ret[int(i)] = row_dict

        return ret

    # @try_db_method_twice
    def portal_common_profile(self, username):
        try:
            call_cursor_bw = conn_bw.cursor()
            result_cursor_bw = conn_bw.cursor()
            call_cursor_bw.callproc('bth_portal_channel_api.bu_profile_name_photo', (username, result_cursor_bw,))
            r = result_cursor_bw.fetchall()
            return self.get_results(r)
        except:
            return abort(503)