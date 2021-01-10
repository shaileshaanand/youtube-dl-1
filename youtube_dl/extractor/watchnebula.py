# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from .zype import ZypeIE
from ..compat import re
from ..compat import compat_urllib_parse_unquote


class WatchNebulaIE(InfoExtractor):
    IE_NAME = 'watchnebula'
    _VALID_URL = r'https?://(?:www\.)?watchnebula\.com\/videos\/(?P<id>[^\\]+)\/?'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        jsdata = ""
        token = re.search(r'"apiToken" *: *"(?P<token>[^"]+)"', compat_urllib_parse_unquote(
            str(self._get_cookies(url)))).group("token")
        for url in re.findall(r'src="([^"]+js)"', str(webpage)):
            jsdata += self._download_webpage(
                'https://watchnebula.com' + url, video_id)

        api_key = re.findall(r'REACT_APP_ZYPE_API_KEY:"([^"]+)"', jsdata)[0]
        api_url = "https://api.zype.com/videos?friendly_title={}&per_page=1&api_key={}".format(
            video_id, api_key)
        uid = self._download_json(api_url, video_id)["response"][0]["_id"]
        access_token = self._download_json(
            "https://api.watchnebula.com/api/v1/auth/user/", video_id, headers={
                'Authorization': 'Token {}'.format(token),
            })["zype_auth_info"]["access_token"]

        return {
            'id': video_id,
            '_type': 'url_transparent',
            'ie_key': ZypeIE.ie_key(),
            'url': "https://player.zype.com/embed/{}.html?autoplay=undefined&access_token={}".format(uid, access_token)
        }
