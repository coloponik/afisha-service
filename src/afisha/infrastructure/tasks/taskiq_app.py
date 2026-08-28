from taskiq import SimpleRetryMiddleware
from taskiq.middlewares import TaskiqAdminMiddleware
from taskiq_redis import RedisStreamBroker

from afisha.infrastructure.tasks.config import settings

broker_cpu = RedisStreamBroker(
    url=settings.redis.url,
    queue_name="cpu",
    socket_timeout=None,
    xread_count=1
).with_middlewares(
    SimpleRetryMiddleware(types_of_exceptions=(Exception,)),
    TaskiqAdminMiddleware(
        url=settings.taskiq.admin_url,
        api_token="supersecret",
        taskiq_broker_name="afisha-cpu"
    )
)
