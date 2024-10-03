from celery import shared_task
from .models import Cruise

@shared_task
def process_cruise_data():
    cruises = Cruise.objects.prefetch_related('legs', 'positions', 'scientists').all()
    # Perform any necessary data processing here
    for cruise in cruises:
        # Example processing logic
        pass
    return "Cruise data processed successfully."
