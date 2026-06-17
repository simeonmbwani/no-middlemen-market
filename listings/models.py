from django.db import models
from django.conf import settings
import io
from PIL import Image
from django.core.files.base import ContentFile


class Listing(models.Model):
    # Core Metadata Fields
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rental rate per day in USD")
    district = models.CharField(max_length=50) 
    province = models.CharField(max_length=50)
    
    is_active = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🗂️ COMPREHENSIVE Southern Africa Asset Grouping Choice Matrix
    CATEGORY_CHOICES = [
        ('Property', (
            ('house', 'House'),
            ('flat', 'Apartment / Flat'),
            ('room', 'Room'),
            ('cottage', 'Cottage'),
            ('office', 'Office Room'),
            ('shop_prop', 'Retail Shop Space'),
            ('warehouse', 'Warehouse'),
            ('conf_hall', 'Conference Hall'),
            ('event_venue', 'Event Venue'),
            ('ind_building', 'Industrial Building'),
            ('comm_stand', 'Commercial Stand'),
            ('res_stand', 'Residential Stand'),
            ('land_plot', 'Land / Agricultural Plot'),
            ('student_accom', 'Student Accommodation'),
        )),
        ('Vehicle', (
            ('car', 'Car'),
            ('truck', 'Truck'),
            ('bus', 'Bus'),
            ('minibus', 'Minibus'),
            ('motorcycle', 'Motorcycle'),
            ('bicycle', 'Bicycle'),
            ('tractor_veh', 'Tractor (Transport)'),
            ('tipper', 'Tipper Truck'),
            ('fuel_tanker', 'Fuel Tanker'),
            ('van', 'Van'),
            ('ambulance', 'Ambulance'),
            ('luxury_veh', 'Luxury Vehicle'),
            ('caravan', 'Caravan'),
            ('const_veh', 'Construction Vehicle'),
        )),
        ('Mining Equipment', (
            ('excavator', 'Excavator'),
            ('bulldozer', 'Bulldozer'),
            ('compressor', 'Air Compressor'),
            ('generator_min', 'Heavy Generator'),
            ('jack_hammer', 'Jack Hammer'),
            ('drill_rig', 'Drill Rig'),
            ('water_pump_min', 'High-Volume Water Pump'),
            ('crusher', 'Mill Crusher / Concentrator'),
            ('loader', 'Front Loader'),
            ('dump_truck', 'Mining Dump Truck'),
            ('conveyor', 'Conveyor System'),
            ('detector', 'Metal Detector'),
            ('safety_gear', 'Mining Safety Equipment'),
            ('survey_equip', 'Surveying Equipment'),
        )),
        ('Farming Equipment', (
            ('tractor_farm', 'Farm Tractor'),
            ('plough', 'Plough'),
            ('harrow', 'Disc Harrow'),
            ('planter', 'Planter / Seed Drill'),
            ('boom_sprayer', 'Boom Sprayer'),
            ('irrigation', 'Irrigation System Layout'),
            ('water_pump_farm', 'Farm Water Pump'),
            ('cultivator', 'Cultivator'),
            ('harvester', 'Harvester Machine'),
            ('baler', 'Hay Baler'),
            ('feed_mixer', 'Feed Mixer'),
            ('livestock_trail', 'Livestock Trailer'),
            ('poultry_equip', 'Poultry Equipment'),
            ('greenhouse', 'Greenhouse Structure'),
        )),
        ('Commerce & Business', (
            ('pos_machine', 'Point of Sale (POS) Machine'),
            ('cash_register', 'Cash Register'),
            ('comm_fridge', 'Commercial Refrigerator'),
            ('display_shelf', 'Display Shelves'),
            ('office_furn', 'Office Furniture'),
            ('comm_computer', 'Business Computer Set'),
            ('comm_printer', 'Enterprise Printer/Copier'),
            ('projector_biz', 'Business Projector'),
            ('internet_equip', 'Network Routers / Starlink'),
        )),
        ('Fishing', (
            ('fish_boat', 'Fishing Boat'),
            ('canoe', 'Canoe'),
            ('fish_net', 'Fishing Net'),
            ('fish_rod', 'Fishing Rod / Gear'),
            ('fish_trap', 'Fish Trap'),
            ('outboard_engine', 'Outboard Engine'),
            ('fish_tank', 'Fish Tank'),
            ('ice_box', 'Commercial Ice Box'),
            ('feed_equip', 'Fish Feed Equipment'),
            ('life_jacket', 'Safety Jacket'),
        )),
        ('Tourism & Hospitality', (
            ('lodge_prop', 'Safari Lodge Room'),
            ('holiday_home', 'Holiday Home'),
            ('campsite', 'Campsite Plot'),
            ('safari_veh', 'Safari Open Vehicle'),
            ('tour_camping_gear', 'Camping / Tour Equipment'),
        )),
        ('General Equipment', (
            ('welding_machine', 'Welding Machine'),
            ('concrete_mixer', 'Concrete Mixer'),
            ('ladder', 'Industrial Ladder'),
            ('power_tools', 'Power Tools (Drills, Saws)'),
            ('solar_system', 'Solar Power System / Batteries'),
            ('cleaning_equip', 'Industrial Cleaning Equipment'),
        )),
        ('Information Technology', (
            ('laptop', 'Laptop Computer'),
            ('desktop', 'Desktop Computer Set'),
            ('server', 'Server Rack Unit'),
            ('starlink_kit', 'Starlink Terminal Kit'),
            ('cctv_system', 'CCTV Security System'),
            ('drone', 'Drone / Quadcopter'),
            ('smart_phone', 'Smart Phone / Tablet'),
        )),
        ('Events & Entertainment', (
            ('pa_system', 'Public Address (PA) System'),
            ('speakers', 'Audio Speakers'),
            ('microphones', 'Microphones / Wireless Gear'),
            ('dj_equipment', 'DJ Decks & Mixers'),
            ('stage_equip', 'Stage Rigging & Lighting'),
            ('event_furniture', 'Tents, Chairs & Tables'),
            ('led_screens', 'LED Display Screens'),
            ('camera_gear', 'Video / Live Streaming Camera'),
        )),
        ('Other', (
            ('other_asset', 'Other (Unlisted Asset - Describe fully below)'),
        ))
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other_asset')

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    PROVINCE_CHOICES = [
        ('harare', 'Harare'), 
        ('bulawayo', 'Bulawayo'), 
        ('manicaland', 'Manicaland'),
        ('mash_central', 'Mashonaland Central'), 
        ('mash_east', 'Mashonaland East'),
        ('mash_west', 'Mashonaland West'), 
        ('masvingo', 'Masvingo'),
        ('mat_north', 'Matabeleland North'), 
        ('mat_south', 'Matabeleland South'), 
        ('midlands', 'Midlands'),
    ]

    # Relationships & Ownership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='listings'
    )
    
    # Text Details
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in USD")
    
    # Location fields tailored for Zimbabwe
    province = models.CharField(max_length=20, choices=PROVINCE_CHOICES)
    district = models.CharField(max_length=50, help_text="e.g., Kadoma, Shurugwi, Gwanda, Bindura")
    
    # Data Optimization Strategy: Strict maximum of 3 images
    image1 = models.ImageField(upload_to='listings/%Y/%m/%d/')
    image2 = models.ImageField(upload_to='listings/%Y/%m/%d/', blank=True, null=True)
    image3 = models.ImageField(upload_to='listings/%Y/%m/%d/', blank=True, null=True)
    
    # Anti-Middleman Business Logic Flags
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False) # Only True after payment and admin review
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (${self.price}) - {self.district}"
    def save(self, *args, **kwargs):
        """Override save method to automatically compress uploaded images."""
        for image_attr in ['image1', 'image2', 'image3']:
            image_field = getattr(self, image_attr)
            
            # If the image field contains a new file upload
            if image_field and hasattr(image_field, 'file') and not getattr(image_field, '_processed', False):
                opened_image = Image.open(image_field)
                
                # Convert colorspace if image is transparent PNG to avoid errors saving as JPEG
                if opened_image.mode in ("RGBA", "P"):
                    opened_image = opened_image.convert("RGB")
                
                # Enforce size ceiling while maintaining aspect ratio
                opened_image.thumbnail((1200, 800))
                
                # Compress into byte stream
                output_stream = io.BytesIO()
                opened_image.save(output_stream, format='JPEG', quality=75) # 75 is ideal for clarity vs data size
                output_stream.seek(0)
                
                # Replace the original uploaded file with our tiny compressed version
                compressed_file = ContentFile(output_stream.read(), name=f"{image_field.name.split('.')[0]}.jpg")
                setattr(self, image_attr, compressed_file)
                
                # Mark as processed to avoid an infinite loop on subsequent saves
                getattr(self, image_attr)._processed = True
                
        super().save(*args, **kwargs)