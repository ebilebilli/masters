from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from core.models.city_model import City, District
from core.models.language_model import Language



@receiver(post_save, sender=City)
@receiver(post_delete, sender=City)
def clear_city_caches(sender, **kwargs):
    cache.delete('city_list')


@receiver(post_save, sender=District)
@receiver(post_delete, sender=District)
def clear_district_caches(sender, **kwargs):
    cache.delete('district_list')

@receiver(post_save, sender=District)
@receiver(post_delete, sender=District)
def clear_district_caches_for_city(sender, instance, **kwargs, ):
    city_id = instance.city_id
    cache.delete(f'district_list_for_city_{city_id}')


@receiver(post_save, sender=Language)
@receiver(post_delete, sender=Language)
def clear_language_caches(sender, **kwargs):
    cache.delete('language_list')

