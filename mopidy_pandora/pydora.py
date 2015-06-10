import requests
from pandora import APIClient, PandoraException

class AlwaysOnAPIClient(APIClient):
    """Pydora API Client for Mopidy-Pandora

    This API client automatically re-authenticates itself if the Pandora authorization token
    has expired. This ensures that the Mopidy-Pandora extension will always be available,
    irrespective of how long Mopidy has been running for.

    Detects 'Invalid Auth Token' messages from the Pandora server, and repeats the last
    request after logging in to the Pandora server again.
    """

    def login(self, username, password):

        # Store username and password so that client can re-authenticate itself if required.
        self.username = username
        self.password = password

        return super(AlwaysOnAPIClient, self).login(username, password)


    def re_authenticate(self):

        # Invalidate old tokens to ensure that the pydora transport layer creates new ones
        self.transport.user_auth_token = None
        self.transport.partner_auth_token = None

        # Reset sync times for new Pandora session
        self.transport.start_time = None
        self.transport.server_sync_time = None

        self.login(self.username, self.password)


    def playable(self, track):

        # Retrieve header information of the track's audio_url. Status code 200 implies that
        # the URL is valid and that the track is accessible
        url = track.audio_url
        r = requests.head(url)
        if r.status_code == 200:
            return True

        return False


    def get_station_list(self):

        try:
            return super(AlwaysOnAPIClient, self).get_station_list()
        except PandoraException as e:

            if e.message == "Invalid Auth Token":
                self.re_authenticate()
                return super(AlwaysOnAPIClient, self).get_station_list()
            else:
                # Exception is not token related, re-throw to be handled elsewhere
                raise e


    def get_playlist(self, station_token):

        try:
            return super(AlwaysOnAPIClient, self).get_playlist(station_token)
        except PandoraException as e:

            if e.message == "Invalid Auth Token":
                self.re_authenticate()
                return super(AlwaysOnAPIClient, self).get_playlist(station_token)
            else:
                # Exception is not token related, re-throw to be handled elsewhere
                raise e
