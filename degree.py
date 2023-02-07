from sequence import Sequence
import pandas as pd
class Degree:

    degreeFrame = pd.DataFrame({"Sequence": [], "Credits": []})
    def __init__(self, seq, credit):
        Degree.degreeFrame.loc[len(Degree.degreeFrame.index)] = [seq, credit]

    def getCredit(self, seq):
        self.degreeFrame[self.degreeFrame[Sequence]==[seq].index]

        return self.credit

    def getSeq(self, seq):
        return self.degreeFrame[self.degreeFrame[Sequence]==[seq]]

    def getDegree(self):
        return Degree.degreeFrame