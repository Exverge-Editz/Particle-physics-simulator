class Particles:

    def __init__(self, charge: object, mass: object, name: object, x: object, y: object) -> None:
        """

        :type name: object
        """
        self.charge = charge
        self.mass = mass
        self.name = name
        self.x = x
        self.vx = 0
        self.y = y
        self.vy = 0

#class for baryons (protons, neutrons) these are the heavier elements
class Baryon(Particles):

    @staticmethod
    def proton(x, y):
        return Baryon(charge=1, mass=1, name='proton', x=x, y=y)

    @staticmethod
    def neutron(x, y):
        return Baryon(charge=0, mass=1, name='neutron', x=x, y=y)

#class for leptons (electrons, neutrinos) these are the lighter elements
class Lepton(Particles):

    @staticmethod
    def electron(x, y):
        return Lepton(charge=(-1), mass=0.05, name="electron", x=x, y=y)