from sequence import Sequence
import pandas as pd
class Degree:

    
    def __init__(self, seq, credit):
        self.degreeFrame = pd.DataFrame({"Sequence": [], "Credits": []})
        self.degreeFrame.loc[len(self.degreeFrame.index)] = [seq, credit]

    def getCredit(self, seq):
        self.degreeFrame[self.degreeFrame[Sequence]==[seq].index]

        return self.credit

    def getSeq(self, seq):
        return self.degreeFrame[self.degreeFrame[Sequence]==[seq]]

    def getDegree(self):
        return self.degreeFrame