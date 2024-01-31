""" Helper functions """


def addToAverage(totalCount, totalValue, newValue):
    """ simple sliding average calculation """
    return ((1.0 * totalCount * totalValue) + newValue) / (totalCount + 1)

# def addToVariance(totalCount, oldVariance, oldAverage, newAverage, newValue):
#     """ sliding variance calculation """
#     return (((oldVariance + oldAverage**2) * totalCount + newValue**2) / float(totalCount+1)) - newAverage**2

 

