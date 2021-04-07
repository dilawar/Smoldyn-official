__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

from pathlib import Path

import smoldyn
import smoldyn._smoldyn as S

sdir = Path(__file__).parent


def test_simptr_simobj():
    s1 = smoldyn.Simulation([0, 0], [10, 10])
    assert s1
    assert s1.getSimPtr()
    assert s1.simptr == s1.getSimPtr()
    assert s1.simptr.dt > 0.0

    modelfile = sdir / ".." / "examples" / "S99_more" / "Min" / "Min1.txt"
    #  s2 = S.Simulation(str(modelfile), "")  # type: _smoldyn.Simulation
    # or, recommended.
    s2 = smoldyn.Simulation.fromFile(modelfile, "")  # type: Simulation

    assert s2
    assert s2.getSimPtr() and s2.getSimPtr() == s2.simptr

    print(s2.start, s2.stop, s2.dt)
    assert s2.start == 0.0
    assert s2.stop == 500
    assert s2.dt == 0.002
    s2.addOutputData('moments')
    s2.addCommand(cmd="molmoments MinD_ATP(front) moments", cmd_type="N", step=10)



if __name__ == "__main__":
    test_simptr_simobj()
