import redis
from django.conf import settings
from django.db import transaction
import json

from django.forms import model_to_dict


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
    def load(cls, instance_id):
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
        conn.set(cache_key, json.dumps(model_to_dict(instance)), ex=cls.cache_timeout)

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
    def cache_delete_multiple(cls, instance_ids):
        conn = cls.get_redis_connection()
        cache_keys = [cls.get_cache_key(instance_id) for instance_id in instance_ids]
        conn.delete(*cache_keys)

    @classmethod
    def load_multiple(cls, instance_ids):
        conn = cls.get_redis_connection()
        cache_keys = [cls.get_cache_key(instance_id) for instance_id in instance_ids]
        pipe = conn.pipeline()
        for key in cache_keys:
            pipe.get(key)
        values = pipe.execute()
        result = list()
        ids_need_cache = list()
        for key, value in zip(cache_keys, values):
            instance_id = key.split(":")[-1]
            if value:
                result.append(json.loads(value))
            else:
                ids_need_cache.append(instance_id)

        if ids_need_cache:
            instances = cls.objects.filter(id__in=ids_need_cache)
            if instances:
                cls.set_cache_multiple(instances)

                for instance in instances:
                    result.append(model_to_dict(instance))
        return result

    @classmethod
    def set_cache_multiple(cls, instances):
        conn = cls.get_redis_connection()
        pipe = conn.pipeline()
        for instance in instances:
            pipe.set(cls.get_cache_key(instance.id), json.dumps(model_to_dict(instance)))
        pipe.execute()