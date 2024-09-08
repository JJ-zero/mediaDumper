import datetime


class ProcessBase:
    @classmethod
    def prepare_nametemplate_data(cls):
        return {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "dateRaw": datetime.datetime.now().strftime("%Y%m%d"),
            "time": datetime.datetime.now().strftime("%H-%M-%S"),
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        }

    @classmethod
    def run(cls, config, device_config, device):
        """
        Returns any object or value to be saved as a checkpoint into device config.
        """
        raise NotImplementedError
