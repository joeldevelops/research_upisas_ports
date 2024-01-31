class PIDController:
    """
    This class builds a PID controller, based on pseudocode from:
    https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller#Pseudocode
    """
    def __init__(self, set_point: float, kp: float, ki: float, kd: float):
        self.set_point = set_point
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def update_set_point(self, set_point: float):
        self.set_point = set_point

    def get_set_point(self):
        return self.set_point

    def calculate(self, measured_value: float, dt: float) -> float:
        """
        Calculates the resulting output based on the error. dt cannot be 0, but the controller will perform better
            if it is close to 0.
        Special case here is that the error is bound between [-20, 20].
        Similarly, the integral gets limited to a maximum between [-50, 50] to ensure recoverability.
        Since not every iteration of the MAPE-K loop performs an execute, the integral might otherwise run off.
        Args:
            measured_value
            dt: time step in seconds

        Returns:
            A float representing a new polling rate
        """
        error = self.set_point - measured_value
        error = max(min(error, 20.0), -20.0)

        # Reset integral if dt is too large
        if dt > 1.0:
            self.integral = 0.0
        else:
            self.integral += error
            self.integral = max(min(self.integral, 50.0), -50.0)
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0

        output = self.kp * error + self.ki * self.integral * dt + self.kd * derivative

        self.prev_error = error
        # PID Control is used for setting the polling rate of sensors. A polling rate below 0 Hz does not make sense
        return max(output, 0.0)
