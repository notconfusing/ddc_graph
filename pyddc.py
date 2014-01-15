import re

class classification:
    #constructor is a single number or a range
    def __init__(self, id):
            self.id = id
            #self.id = self.id.replace('O','0')
    def is_sane(self):
        sane = True
        if not reduce(lambda a, b: a and b,
                 map(lambda c: c in '0123456789.', self.id)):
            sane = False
        elif len(self.id.split('.')) == 1 and len(self.id) > 3:
            sane = False
        return sane
    def len(self):
        return len(self.id.replace('.',''))

class classification_range():
    def __init__(self, classification_a, classification_b):
        if not classification_a.len() == classification_b.len():
            raise AssertionError('Classification length mismatch')
        if not classification_a.id[:-1] == classification_b.id[:-1]:
            raise AssertionError('Range ends must share all digits but last')
        elif classification_a.id[-1] <= classification_b.id[-1]:
            self.start_classification = classification_a
            self.end_classification = classification_b
        else:
            self.start_classification = classification_b
            self.end_classification = classification_a
    def iterrange(self):
        classification_range = []
        pre = self.start_classification.id[:-1]
        s = int(self.start_classification.id[-1])
        e = int(self.end_classification.id[-1])
        for i in range(s,e+1):
            classification_range.append(classification(pre+str(i)))
        return classification_range
    def ids(self):
        return map(lambda x: x.id, self.iterrange())
        
        


def test():
    tests = {'35291': False, 
                '35299': False, 
                '805': True, 
                '809': True, 
                '81': True, 
                '89': True, 
                '033.1': True, 
                '033.8': True}
    testresults = list()
    for test, validity in tests.iteritems():
        t = classification(test)
        testresults.append(t.is_sane() == validity)
    if all(testresults):
        print 'classifications passed'
    else:
        print 'classifications not passed'
    trange_a, trange_b = '033.1',  '033.8'
    crange = classification_range(classification(trange_b), classification(trange_a))
    trange =['033.1', '033.2', '033.3', '033.4', '033.5', '033.6', '033.7', '033.8']
    if trange == map(lambda a: a.id, crange.iterrange()):
        print 'classfication_range passed'    
        