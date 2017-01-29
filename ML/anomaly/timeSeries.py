import numpy as np
import pyflux as pf
import pandas as pd


class TimeSeriesPrediction:
    'Common base for time series prediction'

    iterations=500
    updateFlag=False
    initFlag=False

    def __init__(self, data, p=1, q=1):
        '''
            Constructor
        '''
        self.initFlag=True
        self.model = pf.EGARCHM(data,p,q)
        x = self.model.fit('BBVI', record_elbo=True, iterations=self.iterations, map_start=False)
        self.updatedmodel = None

   
    def update(self, data, p=1, q=1):
        '''
            update the model
        '''
        if not self.initFlag:
            self.updatedmodel = pf.EGARCHM(data,p,q)
            self.updatedmodel.latent_variables = self.model.latent_variables
            x = self.updatedmodel.fit('BBVI', record_elbo=True, iterations=self.iterations, map_start=False)
            self.updateFlag=True


    def predict (self, h):
        '''
            predict the data
        '''
        if self.updateFlag:
            print self.updateFlag
            self.updateFlag=False
            return self.updatedmodel.predict(h)
        return self.model.predict(h)



if __name__ == "__main__":

    data = pd.read_csv('https://vincentarelbundock.github.io/Rdatasets/csv/datasets/sunspot.year.csv')
    h = 2
    data.index = data['time'].values
    tsData = TimeSeriesPrediction(data)

    print tsData.predict (h)

    tsData.update(data)

    print tsData.predict (h)

    tsData.update(data)

    print tsData.predict (h)

    tsData.update(data)

    print tsData.predict (h)
    print type(tsData.predict (h))
    print tsData.predict (h).columns
    vdata = tsData.predict (h)
    print "Timestamp"
    print vdata.index.tolist()
    print "Values"
    print vdata.values.T[0]

