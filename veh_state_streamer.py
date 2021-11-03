import numpy as np

from ROAR_iOS.udp_receiver import UDPStreamer
from ROAR.utilities_module.data_structures_models import Transform, Vector3D


class VehicleStateStreamer(UDPStreamer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transform = Transform()
        self.velocity = Vector3D()

    def run_in_series(self, **kwargs):
        try:
            data = self.recv()
            d = np.frombuffer(data, dtype=np.float32)
            self.transform.location.x = d[0]
            self.transform.location.y = d[1]
            self.transform.location.z = d[2]
            self.transform.rotation.roll = d[3]
            self.transform.rotation.pitch = d[4]
            self.transform.rotation.yaw = d[5]
            self.velocity.x = d[6]
            self.velocity.y = d[7]
            self.velocity.z = d[8]
        except Exception as e:
            self.logger.error(e)
