# coding=utf-8
import asyncio
import logging
import hashlib

logger = logging.getLogger('sanic')


def batch_jsonrpc_cache_key(batch_jussi_attrs):
    return tuple(r['jussi']['key'] for r in batch_jussi_attrs)


def batch_jsonrpc_cache_ttl(batch_jussi_attrs):
    return min(b.ttl for b in batch_jussi_attrs)


def jsonrpc_cache_key(single_jsonrpc_request):
    if isinstance(single_jsonrpc_request.get('params'), dict):
        params = tuple(single_jsonrpc_request['params'].items())
    else:
        params = tuple(single_jsonrpc_request.get('params', []))

    return hashlib.sha1(
        ('%s%s' % (params,
                   single_jsonrpc_request['method'])).encode()).digest()


async def cache_get(app, jussi_attrs):
    cache = app.config.cache
    response = cache.get(jussi_attrs.key)
    if response:
        logger.debug(logger.debug('cache --> %s', response))
    return response


async def cache_set(app, value, jussi_attrs=None, expire=None, key=None):
    expire = expire or jussi_attrs.ttl
    if expire < 0:
        return
    key = key or jussi_attrs.key
    cache = app.config.cache
    cache.set(key, value, expire=expire)