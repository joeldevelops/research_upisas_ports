import json

class SimulationData(object):
    _instance = None
    file_path = '../monitor_data.json'
    
    # Initializing the fields of the simulation data
    
    def __new__(self):
        if self._instance is None:
            self._instance = super(SimulationData, self).__new__(self)
            self._instance.tick_duration = None
            self._instance.tick_number = None
            self._instance.trip_overhead = None
            self._instance.routing_duration = None
            self._instance.route_random_sigma = None
            self._instance.exploration_percentage = None
            self._instance.max_speed_and_length_factor = None
            self._instance.average_edge_duration_factor = None
            self._instance.freshness_update_factor = None
            self._instance.freshness_cutoff_value = None
            self._instance.reroute_every_ticks = None
            self._instance.average_trip_overhead = None
            self._instance.average_trip_duration = None
            self._instance.number_of_cars = None
            # self._instance.variance_trip_overhead = None
        return self._instance
    
# Setters and getters of the simulation data

    def get_tick_duration(self):
        """Getter for tick duration"""
        return self._instance.tick_duration

    def set_tick_duration(self, value):
        """Setter for tick duration"""
        self._instance.tick_duration = value
        self.writeToFile()

    def get_tick_number(self):
        """Getter for tick number"""
        return self._instance.tick_number

    def set_tick_number(self, value):
        """Setter for tick number"""
        self._instance.tick_number = value
        self.writeToFile()

    def get_trip_overhead(self):
        """Getter for trip overhead"""
        return self._instance.trip_overhead

    def set_trip_overhead(self, value):
        """Setter for trip overhead"""
        self._instance.trip_overhead = value
        self.writeToFile()
    
    def set_number_of_cars(self, value):
        """Setter for number of cars"""
        self._instance.number_of_cars = value
        self.writeToFile()
        
        
    def get_number_of_cars(self):
        """Getter for number of cars"""
        return self._instance.number_of_cars
    

        
    def get_routing_duration(self):
        """Getter for routing duration"""
        return self._instance.routing_duration

    def set_routing_duration(self, value):
        """Setter for routing duration"""
        self._instance.routing_duration = value
        self.writeToFile()

    def set_route_random_sigma(self, value):
        """Setter for route random sigma"""
        self._instance.route_random_sigma = value
        self.writeToFile()

    def get_route_random_sigma(self):
        """Getter for route random sigma"""
        return self._instance.route_random_sigma

    def set_exploration_percentage(self, value):
        """Setter for exploration percentage"""
        self._instance.exploration_percentage = value
        self.writeToFile()

    def get_exploration_percentage(self):
        """Getter for exploration percentage"""
        return self._instance.exploration_percentage

    def set_max_speed_and_length_factor(self, value):
        """Setter for max speed and length factor"""
        self._instance.max_speed_and_length_factor = value
        self.writeToFile()

    def get_max_speed_and_length_factor(self):
        """Getter for max speed and length factor"""
        return self._instance.max_speed_and_length_factor

    def set_average_edge_duration_factor(self, value):
        """Setter for average edge duration factor"""
        self._instance.average_edge_duration_factor = value
        self.writeToFile()

    def get_average_edge_duration_factor(self):
        """Getter for average edge duration factor"""
        return self._instance.average_edge_duration_factor

    def set_freshness_update_factor(self, value):
        """Setter for freshness update factor"""
        self._instance.freshness_update_factor = value
        self.writeToFile()

    def get_freshness_update_factor(self):
        """Getter for freshness update factor"""
        return self._instance.freshness_update_factor

    def set_freshness_cutoff_value(self, value):
        """Setter for freshness cutoff value"""
        self._instance.freshness_cutoff_value = value
        self.writeToFile()

    def get_freshness_cutoff_value(self):
        """Getter for freshness cutoff value"""
        return self._instance.freshness_cutoff_value

    def set_reroute_every_ticks(self, value):
        """Setter for reroute every ticks"""
        self._instance.reroute_every_ticks = value
        self.writeToFile()

    def get_reroute_every_ticks(self):
        """Getter for reroute every ticks"""
        return self._instance.reroute_every_ticks  
    
    def get_average_trip_overhead(self):
        """Getter for average trip overhead"""
        return self._instance.average_trip_overhead

    def set_average_trip_overhead(self, value):
        """Setter for average trip overhead"""
        self._instance.average_trip_overhead = value
        self.writeToFile()

    def get_average_trip_duration(self):
        """Getter for average trip duration"""
        return self._instance.average_trip_duration

    def set_average_trip_duration(self, value):
        """Setter for average trip duration"""
        self._instance.average_trip_duration = value
        self.writeToFile()

    # def get_variance_trip_overhead(self):
    #     """Getter for variance trip overhead"""
    #     return self._instance.variance_trip_overhead

    # def set_variance_trip_overhead(self, value):
    #     """Setter for variance trip overhead"""
    #     self._instance.variance_trip_overhead = value
    #     self.writeToFile()
    
# Display the values of the simulation data  

    def display(self):
        print "Tick Duration: {}".format(self._instance.tick_duration)
        print "Tick Number: {}".format(self._instance.tick_number)
        print "Trip Overhead: {}".format(self._instance.trip_overhead)
        print "Routing Duration: {}".format(self._instance.routing_duration)
        print "Route Random Sigma: {}".format(self._instance.route_random_sigma)
        print "Exploration Percentage: {}".format(self._instance.exploration_percentage)
        print "Max Speed And Length Factor: {}".format(self._instance.max_speed_and_length_factor)
        print "Average Edge Duration Factor: {}".format(self._instance.average_edge_duration_factor)
        print "Freshness Update Factor: {}".format(self._instance.freshness_update_factor)
        print "Freshness Cut Off Value: {}".format(self._instance.freshness_cutoff_value)
        print "ReRoute Every Ticks: {}".format(self._instance.reroute_every_ticks)
        print "Average trip duration: {}".format(self._instance.average_trip_duration)
        print "Average trip overhead: {}".format(self._instance.average_trip_overhead)
        print "Number of cars: {}".format(self._instance.number_of_cars)
        # print "Variance trip overhead: {}".format(self._instance.variance_trip_overhead)



# write values of the data to file after every time a new value is set

    def writeToFile(self):
        data = {
                'tripOverhead':self._instance.trip_overhead,
                'tickNumber': self._instance.tick_number,
                'tickDuration': self._instance.tick_duration,
                'routingDuration': self._instance.routing_duration,
                'routeRandomSigma': self._instance.route_random_sigma,
                'explorationPercentage': self._instance.exploration_percentage,
                'maxSpeedAndLengthFactor': self._instance.max_speed_and_length_factor,
                'averageEdgeDurationFactor': self._instance.average_edge_duration_factor,
                'freshnessUpdateFactor': self._instance.freshness_update_factor,
                'freshnessCutOffValue': self._instance.freshness_cutoff_value,
                'reRouteEveryTicks': self._instance.reroute_every_ticks,
                'averageTripOverhead': self._instance.average_trip_overhead,
                'averageTripDuration': self._instance.average_trip_duration,
                'numberOfCars': self._instance.number_of_cars
                # 'varianceTripOverhead': self._instance.variance_trip_overhead
            }
        with open(self.file_path, 'w') as json_file:
            json.dump(data, json_file) 

