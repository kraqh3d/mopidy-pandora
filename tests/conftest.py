from __future__ import unicode_literals

import json

from mock import Mock

from pandora.models.pandora import AdItem, Playlist, PlaylistItem, Station, StationList

import pytest

import requests

from mopidy_pandora import backend

MOCK_STATION_TYPE = 'station'
MOCK_STATION_NAME = 'Mock Station'
MOCK_STATION_ID = '0000000000000000001'
MOCK_STATION_TOKEN = '0000000000000000010'
MOCK_STATION_DETAIL_URL = 'http://mockup.com/station/detail_url?...'
MOCK_STATION_ART_URL = 'http://mockup.com/station/art_url?...'

MOCK_STATION_LIST_CHECKSUM = 'aa00aa00aa00aa00aa00aa00aa00aa00'

MOCK_TRACK_TYPE = 'track'
MOCK_TRACK_NAME = 'Mock Track'
MOCK_TRACK_TOKEN = '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001'
MOCK_TRACK_AD_TOKEN = '000000000000000000-none'
MOCK_TRACK_AUDIO_HIGH = 'http://mockup.com/high_quality_audiofile.mp4?...'
MOCK_TRACK_AUDIO_MED = 'http://mockup.com/medium_quality_audiofile.mp4?...'
MOCK_TRACK_AUDIO_LOW = 'http://mockup.com/low_quality_audiofile.mp4?...'
MOCK_TRACK_DETAIL_URL = 'http://mockup.com/track/detail_url?...'
MOCK_TRACK_ART_URL = 'http://mockup.com/track/art_url?...'
MOCK_TRACK_INDEX = '1'

MOCK_DEFAULT_AUDIO_QUALITY = 'highQuality'

MOCK_AD_TYPE = 'ad'


@pytest.fixture(scope='session')
def config():
    return {
        'http': {
            'hostname': '127.0.0.1',
            'port': '6680'
        },
        'proxy': {
            'hostname': 'mock_host',
            'port': 'mock_port'
        },
        'pandora': {
            'enabled': True,
            'api_host': 'test_host',
            'partner_encryption_key': 'test_encryption_key',
            'partner_decryption_key': 'test_decryption_key',
            'partner_username': 'partner_name',
            'partner_password': 'partner_password',
            'partner_device': 'test_device',
            'username': 'john',
            'password': 'smith',
            'preferred_audio_quality': MOCK_DEFAULT_AUDIO_QUALITY,
            'sort_order': 'date',
            'auto_setup': True,
            'cache_time_to_live': 1800,

            'event_support_enabled': True,
            'double_click_interval': '0.1',
            'on_pause_resume_click': 'thumbs_up',
            'on_pause_next_click': 'thumbs_down',
            'on_pause_previous_click': 'sleep',
        }
    }


def get_backend(config, simulate_request_exceptions=False):
    obj = backend.PandoraBackend(config=config, audio=Mock())

    if simulate_request_exceptions:
        type(obj.api.transport).__call__ = request_exception_mock
    else:
        # Ensure that we never do an actual call to the Pandora server while
        # running tests
        type(obj.api.transport).__call__ = transport_call_not_implemented_mock

    obj._event_loop = Mock()
    return obj


@pytest.fixture(scope='session')
def station_result_mock():
    mock_result = {'stat': 'ok',
                   'result':
                       {'stationId': MOCK_STATION_ID,
                        'stationDetailUrl': MOCK_STATION_DETAIL_URL,
                        'artUrl': MOCK_STATION_ART_URL,
                        'stationToken': MOCK_STATION_TOKEN,
                        'stationName': MOCK_STATION_NAME},
                   }

    return mock_result


@pytest.fixture(scope='session')
def station_mock(simulate_request_exceptions=False):
    return Station.from_json(get_backend(config(), simulate_request_exceptions).api,
                             station_result_mock()['result'])


@pytest.fixture(scope='session')
def get_station_mock(self, station_token):
    return station_mock()


@pytest.fixture(scope='session')
def playlist_result_mock():
    mock_result = {'stat': 'ok',
                   'result': dict(items=[{
                       'trackToken': MOCK_TRACK_TOKEN,
                       'artistName': 'Mock Artist Name',
                       'albumName': 'Mock Album Name',
                       'albumArtUrl': MOCK_TRACK_ART_URL,
                       'audioUrlMap': {
                           'highQuality': {
                               'bitrate': '64',
                               'encoding': 'aacplus',
                               'audioUrl': MOCK_TRACK_AUDIO_HIGH,
                               'protocol': 'http'
                           },
                           'mediumQuality': {
                               'bitrate': '64',
                               'encoding': 'aacplus',
                               'audioUrl': MOCK_TRACK_AUDIO_MED,
                               'protocol': 'http'
                           },
                           'lowQuality': {
                               'bitrate': '32',
                               'encoding': 'aacplus',
                               'audioUrl': MOCK_TRACK_AUDIO_LOW,
                               'protocol': 'http'
                           }
                       },
                       'trackLength': 0,
                       'songName': MOCK_TRACK_NAME,
                       'songDetailUrl': MOCK_TRACK_DETAIL_URL,
                       'stationId': MOCK_STATION_ID,
                       'songRating': 0,
                       'adToken': None, },

                       # Also add an advertisement to the playlist.
                       {
                           'trackToken': None,
                           'artistName': None,
                           'albumName': None,
                           'albumArtUrl': None,
                           'audioUrlMap': {
                               'highQuality': {
                                   'bitrate': '64',
                                   'encoding': 'aacplus',
                                   'audioUrl': MOCK_TRACK_AUDIO_HIGH,
                                   'protocol': 'http'
                               },
                               'mediumQuality': {
                                   'bitrate': '64',
                                   'encoding': 'aacplus',
                                   'audioUrl': MOCK_TRACK_AUDIO_MED,
                                   'protocol': 'http'
                               },
                               'lowQuality': {
                                   'bitrate': '32',
                                   'encoding': 'aacplus',
                                   'audioUrl': MOCK_TRACK_AUDIO_LOW,
                                   'protocol': 'http'
                               }
                           },
                           'trackLength': 0,
                           'songName': None,
                           'songDetailUrl': None,
                           'stationId': None,
                           'songRating': None,
                           'adToken': MOCK_TRACK_AD_TOKEN}
                   ])}

    return mock_result


@pytest.fixture(scope='session')
def ad_metadata_result_mock():
    mock_result = {'stat': 'ok',
                   'result': dict(title=MOCK_TRACK_NAME, companyName='Mock Company Name', audioUrlMap={
                       'highQuality': {
                           'bitrate': '64',
                           'encoding': 'aacplus',
                           'audioUrl': MOCK_TRACK_AUDIO_HIGH,
                           'protocol': 'http'
                       },
                       'mediumQuality': {
                           'bitrate': '64',
                           'encoding': 'aacplus',
                           'audioUrl': MOCK_TRACK_AUDIO_MED,
                           'protocol': 'http'
                       },
                       'lowQuality': {
                           'bitrate': '32',
                           'encoding': 'aacplus',
                           'audioUrl': MOCK_TRACK_AUDIO_LOW,
                           'protocol': 'http'
                       }
                   }, adTrackingTokens={
                       MOCK_TRACK_AD_TOKEN,
                       MOCK_TRACK_AD_TOKEN,
                       MOCK_TRACK_AD_TOKEN
                   })}

    return mock_result


@pytest.fixture(scope='session')
def playlist_mock(simulate_request_exceptions=False):
    return Playlist.from_json(get_backend(config(), simulate_request_exceptions).api, playlist_result_mock()['result'])


@pytest.fixture(scope='session')
def get_playlist_mock(self, station_token):
    return playlist_mock()


@pytest.fixture(scope='session')
def get_station_playlist_mock(self):
    return iter(get_playlist_mock(self, MOCK_STATION_TOKEN))


@pytest.fixture
def playlist_item_mock():
    return PlaylistItem.from_json(get_backend(
        config()).api, playlist_result_mock()['result']['items'][0])


@pytest.fixture(scope='session')
def ad_item_mock():
    return AdItem.from_json(get_backend(
        config()).api, ad_metadata_result_mock()['result'])


@pytest.fixture
def get_ad_item_mock(self, token):
    return ad_item_mock()


@pytest.fixture(scope='session')
def station_list_result_mock():
    mock_result = {'stat': 'ok',
                   'result': {'stations': [
                       {'stationId': MOCK_STATION_ID.replace('1', '2'),
                        'stationToken': MOCK_STATION_TOKEN.replace('010', '100'),
                        'stationName': MOCK_STATION_NAME + ' 2'},
                       {'stationId': MOCK_STATION_ID,
                        'stationToken': MOCK_STATION_TOKEN,
                        'stationName': MOCK_STATION_NAME + ' 1'},
                       {'stationId': MOCK_STATION_ID.replace('1', '3'),
                        'stationToken': MOCK_STATION_TOKEN.replace('0010', '1000'),
                        'stationName': 'QuickMix', 'isQuickMix': True},
                   ], 'checksum': MOCK_STATION_LIST_CHECKSUM},
                   }

    return mock_result['result']


@pytest.fixture
def get_station_list_mock(self):
    return StationList.from_json(get_backend(config()).api, station_list_result_mock())


@pytest.fixture(scope='session')
def request_exception_mock(self, *args, **kwargs):
    raise requests.exceptions.RequestException


@pytest.fixture
def transport_call_not_implemented_mock(self, method, **data):
    raise TransportCallTestNotImplemented(method + '(' + json.dumps(self.remove_empty_values(data)) + ')')


class TransportCallTestNotImplemented(Exception):
    pass
