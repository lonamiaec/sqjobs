import json
from abc import abstractmethod, ABCMeta
from six import add_metaclass
from datetime import datetime

from django.db import IntegrityError

from sqjobs import Job
from sqjobs.contrib.django.djsqjobs.models import JobStatus


@add_metaclass(ABCMeta)
class ResultJob(Job):

    def __init__(self):
        self.properly_setup = False
        self.repeated_task = False

    def execute(self, *args, **kwargs):
        self.set_up(*args, **kwargs)
        if not self.repeated_task:
            self.result = self.run(*args, **kwargs)
            self.tear_down(*args, **kwargs)

    def set_up(self, *args, **kwargs):
        super(ResultJob, self).set_up(*args, **kwargs)
        # Take as id the left part from the hash symbol
        task_id = self.id.split('#')[0]
        try:
            self.job_status = JobStatus(
                job_id=task_id,
                job_name=self.__repr__()
            )
            self.job_status.save(force_insert=True)
            self.properly_setup = True
        except IntegrityError:
            self.job_status = JobStatus.objects.get(job_id=task_id)
            if self.job_status.status == JobStatus.FAILURE:
                self.job_status.status = JobStatus.PENDING
                self.job_status.save()
                self.properly_setup = True
            else:
                self.repeated_task = True

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def tear_down(self, *args, **kwargs):
        self.job_status.date_done = datetime.now()
        self.job_status.result = json.dumps(self.result)
        self.job_status.save(force_update=True)
        super(ResultJob, self).tear_down(*args, **kwargs)

    def on_success(self, *args, **kwargs):
        if not self.repeated_task:
            self.job_status.status = JobStatus.SUCCESS
            self.job_status.save(force_update=True)
            super(ResultJob, self).on_success(*args, **kwargs)

    def on_failure(self, *args, **kwargs):
        if not self.repeated_task:
            if self.properly_setup:
                self.job_status.status = JobStatus.FAILURE
                self.job_status.save(force_update=True)
            super(ResultJob, self).on_failure(*args, **kwargs)
