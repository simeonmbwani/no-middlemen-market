import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Listing

@receiver(post_delete, sender=Listing)
def auto_delete_files_on_delete(sender, instance, **kwargs):
    """
    Listens for asset deletions and scrubs corresponding physical media 
    images from system storage folders dynamically to preserve disk capacity.
    """
    # Bundle your listing file fields together into an iterable array
    image_fields = [instance.image1, instance.image2, instance.image3]
    
    for image in image_fields:
        if image:
            # Get the exact physical path to the file on your local machine
            if os.path.isfile(image.path):
                try:
                    os.remove(image.path)
                    print(f"🗑️ System Signal: Cleaned up orphaned media file: {image.path}")
                except Exception as e:
                    # Logs any OS permission anomalies quietly without breaking user workflow execution
                    print(f"⚠️ Signal Warning: Could not clear file path {image.path}. Error: {e}")