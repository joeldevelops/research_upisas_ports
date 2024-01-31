from dataclasses import dataclass


@dataclass
class Knowledge:
    """
    A container class representing the knowledge base of the MAPE-K reference model.

    Attributes
    -----------
    monitored_data : dict
        The data monitored in the Monitor step of the MAPE-K reference model.
    analysis_data : dict
        The resulting data of the Analysis step of the MAPE-K reference model.
    plan_data : dict
        The resulting data of the Plan step of the MAPE-K reference model.
    adaptation_options : dict
        A dictionary describing the adaptations options.
    monitor_schema : dict
        A JSON schema to validate the response of the monitor endpoint.
    execute_schema : dict
        A JSON schema to validate the response of the execute endpoint.
    adaptation_options_schema : dict
        A JSON schema to validate the response of the adaptation_options endpoint.
    """
    monitored_data: dict
    analysis_data: dict
    plan_data: dict

    adaptation_options: dict

    monitor_schema: dict
    execute_schema: dict
    adaptation_options_schema: dict
