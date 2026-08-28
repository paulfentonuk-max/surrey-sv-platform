import requests
import pandas as pd
from django.conf import settings
from sv_platform.apps.communities.models import CommunityProfile

class CommunityDataIngester:
    def __init__(self):
        self.data_sources = {
            'census': settings.SURREY_CENSUS_API_URL,
            'imd_deprivation': settings.SURREY_IMD_API_URL,
