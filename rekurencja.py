


class Rodzic:
    def __init__(self):
        self.atrybut = 0

class Dziecko(Rodzic):
    def zmien(self,x):
        self.atrybut = x
        
        
        
o = Rodzic()
obiekt = Dziecko()

print(obiekt.atrybut)

obiekt.zmien(5)

print(obiekt.atrybut)