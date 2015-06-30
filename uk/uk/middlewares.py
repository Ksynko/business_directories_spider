from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy import log
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.xlib.tx import ResponseFailed


class UpdatedRetryMiddleware(RetryMiddleware):
    """This middleware will remove 'proxy' from meta, so for
    next request another one may be used."""

    def __init__(self, settings):
        if not settings.getbool('UPDATED_RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    def process_response(self, request, response, spider):
        if 'dont_retry' in request.meta:
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            try:
                request.headers.pop('Proxy-Authorization')
            except:
                pass
            return self._retry(request, reason, spider) or response
        return response

    def _retry(self, request, reason, spider):
        try:
            proxy = request.meta.pop('proxy', None)
        except:
            proxy = 'Without proxy'
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            log.msg(format="Retrying %(request)s (failed %(retries)d times):"\
                    " %(reason)s. Proxy address: %(proxy)s",
                    level=log.DEBUG, spider=spider, request=request,
                    retries=retries, reason=reason, proxy=proxy)
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            log.msg(format="Gave up retrying %(request)s "\
                    "(failed %(retries)d times): %(reason)s."\
                    " Proxy address: %(proxy)s",
                    level=log.DEBUG, spider=spider, request=request,
                    retries=retries, reason=reason, proxy=proxy)