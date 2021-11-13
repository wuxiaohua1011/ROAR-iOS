from collections import deque

import numpy as np

from ROAR.utilities_module.vehicle_models import VehicleControl, Vehicle


class Brake:
    def __init__(self, kp, kd, ki, max_brake=0.15, time_horizon=10):
        self.kp = kp
        self.kd = kd
        self.ki = ki
        self.max_brake = max_brake
        self.error_deque = deque(maxlen=time_horizon)

    def run_step(self, control: VehicleControl, vehicle: Vehicle) -> VehicleControl:
        if control.brake:
            e = 0 - vehicle.get_speed(vehicle)
            if vehicle.transform.rotation.pitch > -80:
                # going up ramp
                control.throttle = 0.15
                return control
            if vehicle.transform.rotation.pitch < -105:
                # going down ramp
                control.throttle = -0.15
                return control

            de = 0 if len(self.error_deque) < 2 else self.error_deque[-2] - self.error_deque[-1]
            ie = 0 if len(self.error_deque) < 2 else np.sum(self.error_deque)
            control.throttle = np.clip(self.kp * e + self.kd * de + self.ki * ie, -abs(self.max_brake),
                                       abs(self.max_brake))
            return control
        else:
            self.error_deque.clear()
            return control
