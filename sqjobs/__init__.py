from .job import Job
from .metadata import __version__, __license__


def create_eager_broker():
    from .brokers.eager import Eager

    broker = Eager()
    return broker


def create_sqs_broker(access_key, secret_key, region='us-west-1', is_secure=True, port=443):
    from .connectors.sqs import SQS
    from .brokers.broker import Standard

    sqs = SQS(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        is_secure=is_secure,
        port=port
    )

    broker = Standard(sqs)
    return broker


def create_sqs_worker(queue_name, access_key, secret_key, region='us-west-1', is_secure=True, port=443):
    from .worker import Worker

    broker = create_sqs_broker(access_key, secret_key, region, is_secure, port)
    worker = Worker(broker, queue_name)

    return worker
