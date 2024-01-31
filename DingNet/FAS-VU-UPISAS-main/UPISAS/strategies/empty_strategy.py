from UPISAS.strategy import Strategy


class EmptyStrategy(Strategy):
    """
    A class which implements an empty adaption strategy.

    The strategy follows the MAPE-K reference model.

    Methods
    -------
    analyze()
        Analyzes the possible adaptation options. Always returns True.
    plan()
        Plans the adaptation. Always returns True.
    """

    def analyze(self):
        """
        Analyzes the possible adaptation options. Always returns True.

        This method represents the Analyze step of the MAPE-K reference model.

        Returns
        -------
        bool
            True
        """
        return True

    def plan(self):
        """
        Plans the adaptation. Always returns True.

        This method represents the Plan step of the MAPE-K reference model.

        Returns
        -------
        bool
            True
        """
        return True
