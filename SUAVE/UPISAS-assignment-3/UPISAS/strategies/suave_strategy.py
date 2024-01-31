import logging

from UPISAS.strategy import Strategy
from transitions import Machine

WATER_VISIBILITY_THRESHOLD = 3.0
SUAVE_INIT_TIMEOUT = 1000
SUAVE_WV_TIMEOUT = 60


class SuaveStateMachine(object):
    def __init__(self):
        self.states = ['Idle', 'Descending', 'Ascending', 'ExecutingTask', 'DegradedOperation', 'Returning']

        self.transitions = [
            {'trigger': 'visibility_greater_than_N', 'source': '*', 'dest': 'Descending'},
            {'trigger': 'visibility_equals_N', 'source': '*', 'dest': 'ExecutingTask'},
            {'trigger': 'visibility_less_than_N', 'source': '*', 'dest': 'Ascending'},
            {'trigger': 'erroneous_water_visibility_reported', 'source': '*', 'dest': 'DegradedOperation'},
            {'trigger': 'thruster_failure_detected', 'source': '*', 'dest': 'DegradedOperation'},
            {'trigger': 'multiple_thruster_failures', 'source': '*', 'dest': 'Returning'},
            {'trigger': 'sensor_error_detected', 'source': '*', 'dest': 'Returning'},
        ]

        self.machine = Machine(model=self, states=self.states, transitions=self.transitions,
                               initial='Idle')

        self.first_transition = True

    def on_enter_Descending(self):
        if self.first_transition:
            self.first_transition = False
            return None
        logging.info("The AUV enters descending state to reach water visibility threshold.")
        adaptation = {
            "adaptation": "/f_generate_search_path/change_mode",
            "option": "fd_spiral_low"
        }
        return adaptation

    def on_enter_Ascending(self):
        if self.first_transition:
            self.first_transition = False
            return None
        logging.info("The AUV enters ascending state to reach water visibility threshold.")
        adaptation = {
            "adaptation": "/f_generate_search_path/change_mode",
            "option": "fd_spiral_high"
        }
        return adaptation

    def on_enter_ExecutingTask(self):
        logging.info("The AUV enters task execution state. No extra adaptations to send.")

    def on_enter_DegradedOperation(self) -> dict:
        logging.warning("Entering degraded operational mode, current task will be cancelled. "
                        "Maintain motion cmd will be sent.")
        adaptation = {
            "adaptation": "/f_maintain_motion/change_mode",
            "option": "fd_recover_thrusters"
        }
        return adaptation

    def on_enter_Returning(self):
        logging.warning("Critical error detected (water visibility sensor failure/multiple thruster failure). "
                        "Entering AUV returning procedure, all task will be cancelled.")
        adaptation = {
            "adaptation": "/task/cancel",
            "option": "inspect_pipeline"
        }
        return adaptation


class SuaveStrategy(Strategy):

    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.suave_init_timer = 0
        self.suave_initialized = False
        self.suave_wv_sensor_timeout = 0

        self.sm = SuaveStateMachine()

        logging.info("SM Strategy initialized with following settings: "
                     f"\n\tWV_THRES: {WATER_VISIBILITY_THRESHOLD}"
                     f"\n\tSUAVE_INIT_TIMEOUT: {SUAVE_INIT_TIMEOUT}"
                     f"\n\tSUAVE_WV_TIMEOUT: {SUAVE_WV_TIMEOUT}")

    def analyze(self):
        data = self.knowledge.monitored_data
        water_visibility_curr = data['water_visibility'][-1]

        if water_visibility_curr == -1:
            self.suave_init_timer += 1
            if self.suave_init_timer > SUAVE_INIT_TIMEOUT:
                logging.error("Unable to check the health status of SUAVE, please check manually.")
            return False

        thruster_status = data['thrusters'][-1]
        thruster_failure_count = 0

        logging.info(f"Current state: {self.sm.state}")
        logging.info(f"Current WV: {water_visibility_curr}")

        self.knowledge.plan_data = None

        for thruster_id, status in thruster_status.items():
            if not status:
                thruster_failure_count += 1
        try:
            # handle water visibility events
            if water_visibility_curr == 0:
                self.knowledge.plan_data = self.sm.erroneous_water_visibility_reported()
                self.suave_wv_sensor_timeout += 1
                if self.suave_wv_sensor_timeout > SUAVE_WV_TIMEOUT:
                    self.knowledge.plan_data = self.sm.sensor_error_detected()
                return True
            elif water_visibility_curr > WATER_VISIBILITY_THRESHOLD:
                self.knowledge.plan_data = self.sm.visibility_greater_than_N()
            elif water_visibility_curr < WATER_VISIBILITY_THRESHOLD:
                self.knowledge.plan_data = self.sm.visibility_less_than_N()
            elif water_visibility_curr == WATER_VISIBILITY_THRESHOLD:
                self.knowledge.plan_data = self.sm.visibility_equals_N()

            # handle thruster failure events
            if thruster_failure_count == 1:
                self.knowledge.plan_data = self.sm.thruster_failure_detected()
            elif thruster_failure_count >= 1:
                self.knowledge.plan_data = self.sm.multiple_thruster_failures()

            # nothing to analyze
            if not self.knowledge.plan_data:
                logging.warning("Unable to analyze with given knowledge, will retry in the next analysis.")
                return False

            return True
        except Exception as e:
            pass

    def plan(self):
        # Since state machine is a rather simple mechanism for SAS
        # the plan phase is built into the analysis phase.
        # See anaylze() for more info
        pass
