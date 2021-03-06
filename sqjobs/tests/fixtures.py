from ..job import Job


class Adder(Job):
    name = 'adder'
    queue = 'default'
    # We set this time so it's re-queued in Dummy connector
    retry_time = 10

    def run(self, num1, num2):
        return num1 + num2


class Divider(Job):
    name = 'divider'
    queue = 'default'
    retry_time = 10

    def run(self, num1, num2):
        return self.num1 // num2

    def set_up(self, num1, *args, **kwargs):
        self.num1 = num1 + 1

    def tear_down(self, *args, **kwargs):
        self.result = str(self.result)

    def on_failure(self, *args, **kwargs):
        self.err = 'ZeroDivisionError'


class RetryJob(Job):
    name = 'retry'
    retried_callback_called = False

    @classmethod
    def has_retried(cls):
        return cls.retried_callback_called

    @classmethod
    def retried(cls):
        cls.retried_callback_called = True

    @classmethod
    def reset_retried(cls):
        cls.retried_callback_called = True

    def __init__(self):
        super(RetryJob, self).__init__()
        RetryJob.reset_retried()

    def run(self):
        self.retry()

    def on_retry(self):
        RetryJob.retried()


class ExceptionJob(Job):
    name = 'exception'
    failed_callback_called = False
    # We set this time so it's re-queued in Dummy connector
    retry_time = 10

    @classmethod
    def has_failed(cls):
        return cls.failed_callback_called

    @classmethod
    def failed(cls):
        cls.failed_callback_called = True

    @classmethod
    def reset_failed(cls):
        cls.failed_callback_called = True

    def __init__(self):
        super(ExceptionJob, self).__init__()
        ExceptionJob.reset_failed()

    def run(self):
        raise Exception("Test")

    def on_fail(self):
        ExceptionJob.retried()


class FakeAdder(Adder):
    retry_time = None


class AbstractAdder(Adder):
    abstract = True


class ComplexRetryJob(Adder):
    name = 'complex'
    retry_time = 10

    def next_retry(self):
        return (self.retries + 1) * self.retry_time
