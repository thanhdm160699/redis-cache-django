import redis
from django.conf import settings
from django.db import transaction
import json


class BaseCacheMixin:
    cache_timeout = settings.CACHE_TTL
    conn = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )

    @classmethod
    def get_redis_connection(cls):
        return cls.conn

    @classmethod
    def get_cache_key(cls, instance_id):
        return f"{cls.__name__}:{instance_id}"

    @classmethod
    def get_instance_from_cache(cls, instance_id):
        conn = cls.get_redis_connection()
        cache_key = cls.get_cache_key(instance_id)
        cached_instance = conn.get(cache_key)
        if cached_instance:
            return json.loads(cached_instance)

        # If cache miss, retrieve from database and set cache
        instance = cls.objects.get(id=instance_id)
        cls.set_cache(instance)
        return instance

    @classmethod
    def set_cache(cls, instance):
        cache_key = cls.get_cache_key(instance.id)
        conn = cls.get_redis_connection()
        conn.set(cache_key, json.dumps(instance), ex=cls.cache_timeout)

    @classmethod
    def invalidate_cache(cls, instance_id):
        cache_key = cls.get_cache_key(instance_id)
        conn = cls.get_redis_connection()
        conn.delete(cache_key)

    @classmethod
    def update_instance(cls, instance_id, data):
        with transaction.atomic():
            instance = cls.objects.get(id=instance_id)
            for key, value in data.items():
                setattr(instance, key, value)
            instance.save()

            cls.invalidate_cache(instance_id)
            cls.set_cache(instance)

        return instance

    @classmethod
    def delete_instance(cls, instance_id):
        with transaction.atomic():
            instance = cls.objects.get(id=instance_id)
            instance.delete()

            cls.invalidate_cache(instance_id)

    @classmethod
    def cache_get_multiple(cls, instance_ids):
        conn = cls.get_redis_connection()
        cache_keys = [cls.get_cache_key(instance_id) for instance_id in instance_ids]
        values = conn.mget(cache_keys)
        result = {}
        for key, value in zip(cache_keys, values):
            instance_id = key.split(":")[-1]
            result[instance_id] = json.loads(value) if value else None
        return result

    @classmethod
    def cache_delete_multiple(cls, instance_ids):
        conn = cls.get_redis_connection()
        cache_keys = [cls.get_cache_key(instance_id) for instance_id in instance_ids]
        conn.delete(*cache_keys)
