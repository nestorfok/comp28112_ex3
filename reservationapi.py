""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

import requests
import simplejson
import warnings
import time

from requests.exceptions import HTTPError
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError)

class ReservationApi:
    def __init__(self, base_url: str, token: str, retries: int, delay: float):
        """ Create a new ReservationApi to communicate with a reservation
        server.

        Args:
            base_url: The URL of the reservation API to communicate with.
            token: The user's API token obtained from the control panel.
            retries: The maximum number of attempts to make for each request.
            delay: A delay to apply to each request to prevent server overload.
        """
        self.base_url = base_url
        self.token    = token
        self.retries  = retries
        self.delay    = delay

    def _reason(self, req: requests.Response) -> str:
        """Obtain the reason associated with a response"""
        reason = ''

        # Try to get the JSON content, if possible, as that may contain a
        # more useful message than the status line reason
        try:
            json = req.json()
            reason = json['message']

        # A problem occurred while parsing the body - possibly no message
        # in the body (which can happen if the API really does 500,
        # rather than generating a "fake" 500), so fall back on the HTTP
        # status line reason
        except simplejson.errors.JSONDecodeError:
            if isinstance(req.reason, bytes):
                try:
                    reason = req.reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = req.reason.decode('iso-8859-1')
            else:
                reason = req.reason

        return reason

    def _headers(self) -> dict:
        """Create the authorization token header needed for API requests"""
        # Your code goes here
        value = "Bearer " + self.token
        header = {"Authorization": value}
        return header

    def _send_request(self, method: str, endpoint: str) -> dict:
        """Send a request to the reservation API and convert errors to
           appropriate exceptions"""
        # Your code goes here

        # Allow for multiple retries if needed
        for i in range(self.retries):
            # Perform the request.
            if method == "DELETE":
                response = requests.delete(endpoint, headers=self._headers())
            elif method == "GET":
                response = requests.get(endpoint, headers=self._headers())
            else:
                response = requests.post(endpoint, headers=self._headers())

            # Delay before processing the response to avoid swamping server.
            time.sleep(self.delay)

            # 200 response indicates all is well - send back the json data.
            if response.status_code == 200:
                return response.json()
            else:
                # 5xx responses indicate a server-side error, show a warning
                # (including the try number).
                if 500 <= response.status_code < 600:
                    reason = self._reason(response)
                    warnings.warn(reason + ': %d trial' % (i + 1))

                # 400 errors are client problems that are meaningful, so convert
                # them to separate exceptions that can be caught and handled by
                # the caller.
                elif 400 <= response.status_code < 500:
                    # 400
                    if response.status_code == 400:
                        error = BadRequestError("A 400 Bad Request error occurred.")
                    # 401
                    elif response.status_code == 401:
                        error = InvalidTokenError('The API token was invalid or missing.')
                    # 403
                    elif response.status_code == 403:
                        error = BadSlotError('The requested slot does not exist.')
                    # 404
                    elif response.status_code == 404:
                        error = NotProcessedError('The request has not been processed.')
                    # 409
                    elif response.status_code == 409:
                        error = SlotUnavailableError('The requested slot is not available.')
                    # 451
                    else:
                        error = ReservationLimitError('The client already holds the maximum number of reservations.')
                # Anything else is unexpected and may need to kill the client.
                else:
                    raise Exception('Something is unexpected and the client is down')

        raise error

    def get_slots_available(self):
        """Obtain the list of slots currently available in the system"""
        # Your code goes here
        return self._send_request("GET", self.base_url + "/reservation/available")

    def get_slots_held(self):
        """Obtain the list of slots currently held by the client"""
        # Your code goes here
        return self._send_request("GET", self.base_url + "/reservation")

    def release_slot(self, slot_id):
        """Release a slot currently held by the client"""
        # Your code goes here
        return self._send_request("DELETE", self.base_url + "/reservation/%d" % slot_id)


    def reserve_slot(self, slot_id):
        """Attempt to reserve a slot for the client"""
        # Your code goes here
        return self._send_request("POST", self.base_url + "/reservation/%d" % slot_id)
