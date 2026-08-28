import requests
import pandas as pd
from django.conf import settings
from .models import GeographicArea
from sv_platform.apps.communities.models import CommunityProfile

class CommunityDataIngester:
    def __init__(self):
        self.data_sources = {
            'census': settings.SURREY_CENSUS_API_URL,
            'imd_deprivation': settings.SURREY_IMD_API_URL,
            'health_outcomes': settings.SURREY_HEALTH_API_URL,
        }
        self.processed_areas = []
    
    def ingest_all(self):
        census_data = self.fetch_census_data()
        imd_data = self.fetch_imd_data()
        health_data = self.fetch_health_data()
        
        for area_code in census_data.keys():
            self.process_area(
                area_code,
                census_data.get(area_code, {}),
                imd_data.get(area_code, {}),
                health_data.get(area_code, {})
            )
        
        return len(self.processed_areas)
    
    def fetch_census_data(self):
        try:
            response = requests.get(f"{self.data_sources['census']}/latest")
            return response.json()
        except:
            return self._mock_census_data()
    
    def fetch_imd_data(self):
        try:
            response = requests.get(f"{self.data_sources['imd_deprivation']}/latest")
            return response.json()
        except:
            return self._mock_imd_data()
    
    def fetch_health_data(self):
        try:
            response = requests.get(f"{self.data_sources['health_outcomes']}/latest")
            return response.json()
        except:
            return self._mock_health_data()
    
    def process_area(self, area_code, census, imd, health):
        area, created = GeographicArea.objects.update_or_create(
            code=area_code,
            defaults={
                'name': census.get('name', f'Area {area_code}'),
                'area_type': 'LSOA',
            }
        )
        
        profile, created = CommunityProfile.objects.update_or_create(
            geographic_area=area,
            defaults={
                'census_data': census,
                'deprivation_index': imd,
                'health_outcomes': health,
            }
        )
        
        profile.calculate_disadvantage_index()
        profile.save()
        self._generate_embedding(profile)
        self.processed_areas.append(area_code)
        return profile
    
    def _generate_embedding(self, profile):
        try:
            from sentence_transformers import SentenceTransformer
            profile_text = f"Community: {profile.geographic_area.name} Deprivation: {profile.composite_disadvantage_score}"
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(profile_text).tolist()
            profile.profile_embedding = embedding
            profile.save()
            profile.geographic_area.embedding = embedding
            profile.geographic_area.save()
        except:
            pass
    
    def _mock_census_data(self):
        return {
            'E01000001': {'name': 'Surrey Area 1', 'population': 1500},
            'E01000002': {'name': 'Surrey Area 2', 'population': 2000},
        }
    
    def _mock_imd_data(self):
        return {
            'E01000001': {'income': 0.3, 'employment': 0.4, 'education': 0.2, 'health': 0.5, 'crime': 0.1, 'housing': 0.3},
            'E01000002': {'income': 0.5, 'employment': 0.6, 'education': 0.4, 'health': 0.7, 'crime': 0.3, 'housing': 0.5},
        }
    
    def _mock_health_data(self):
        return {
            'E01000001': {'life_expectancy': 78, 'long_term_conditions': 0.25},
            'E01000002': {'life_expectancy': 75, 'long_term_conditions': 0.35},
        }
