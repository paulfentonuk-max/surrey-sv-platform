from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize vector database for community similarity matching'

    def handle(self, *args, **options):
        if settings.VECTOR_DB == 'pinecone':
            self._setup_pinecone()
        else:
            self._setup_weaviate()
    
    def _setup_pinecone(self):
        try:
            import pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            
            if settings.PINECONE_INDEX not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.PINECONE_INDEX,
                    dimension=384,
                    metric='cosine'
                )
                self.stdout.write(self.style.SUCCESS(f'Created Pinecone index: {settings.PINECONE_INDEX}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Pinecone index exists: {settings.PINECONE_INDEX}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Pinecone setup failed: {e}'))
    
    def _setup_weaviate(self):
        try:
            import weaviate
            client = weaviate.Client(settings.WEAVIATE_URL)
            
            schema = {
                "class": "Community",
                "vectorizer": "none",
                "properties": [
                    {"name": "area_code", "dataType": ["text"]},
                    {"name": "name", "dataType": ["text"]},
                    {"name": "disadvantage_score", "dataType": ["number"]},
                ]
            }
            
            try:
                client.schema.create_class(schema)
                self.stdout.write(self.style.SUCCESS('Created Weaviate schema'))
            except:
                self.stdout.write(self.style.SUCCESS('Weaviate schema exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Weaviate setup failed: {e}'))
