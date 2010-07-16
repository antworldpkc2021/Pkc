import datetime
import logging

from tron.utils import timeutils

log = logging.getLogger('tron.scheduler')

class ConstantScheduler(object):
    """The constant scheduler only schedules the first one but sets itself as a dependant so always runs"""
    def next_run(self, flow):
        if flow.runs:
            return None
        flow_run = flow.build_run()
        flow_run.set_run_time(timeutils.current_time())
        return flow_run

    def __str__(self):
        return "CONSTANT"

    def set_flow_queueing(self, flow):
        flow.constant = True

class DailyScheduler(object):
    """The daily scheduler schedules one run per day"""
    def next_run(self, flow):
        # For a daily scheduler, always assume the next job run is tomorrow
        run_time = (timeutils.current_time() + datetime.timedelta(days=1)).replace(hour=0, minute=1, second=1)

        last = flow.runs[-1] if flow.runs else None
        flow_run = flow.build_run(last)
        flow_run.set_run_time(run_time)
        return flow_run

    def __str__(self):
        return "DAILY"

    def set_flow_queueing(self, flow):
        flow.queueing = True

class IntervalScheduler(object):
    """The interval scheduler runs a flow (to success) based on a configured interval
    """
    def __init__(self, interval=None):
        self.interval = interval
    
    def next_run(self, flow):
        # Find the last success to pick the next time to run
        if flow.runs:
            last = flow.runs[-1]
            run_time = last.run_time + self.interval
        else:
            log.debug("Found no past runs for flow %s, next run is now", flow.name)
            last = None
            run_time = timeutils.current_time()
        
        flow_run = flow.build_run(last)
        flow_run.set_run_time(run_time)
        return flow_run

    def __str__(self):
        return "INTERVAL:%s" % self.interval
        
    def set_flow_queueing(self, flow):
        flow.queueing = False

