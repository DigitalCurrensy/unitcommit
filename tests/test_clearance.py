"""A mismatch is refused."""
from dataclasses import dataclass

from platforms.unitcommit.src.application.apply_derate import apply_derates, from_flexible
from platforms.unitcommit.src.application.build_ising import Cluster, OpfSolution, ZoneSnapshot
from platforms.unitcommit.src.application.clearance import build_and_clear


@dataclass(frozen=True)
class _Group:
    cluster_id: str
    pmin_mw: float
    pmax_mw: float
    c_nl: float
    c_su: float
    mut_steps: int
    initial_on: int


def test_derate_shrinks_pmax_before_clearance():
    flex = _Group("a", 10, 50, 10, 40, 2, 1)
    cluster = from_flexible(flex)

    class _D:
        cluster_id = "a"
        factor = 0.4

    shrunk = apply_derates(cluster, [_D()])
    assert shrunk.pmax_mw == 20.0

    snap = ZoneSnapshot(
        clusters=(shrunk, Cluster("b", 8, 30, 15, 25, 1, 1)),
        demand_mw=(20.0, 22.0),
        reserve_mw=(8.0, 8.0),
        interval_s=900,
    )
    refused = build_and_clear(
        run_id="r1",
        snapshot=snap,
        opf=OpfSolution(residual_mw=9.0, spin_count=8),
        assignment_count=8,
        tolerance_mw=1.0,
        time_source="csac",
        wrapped=True,
    )
    assert refused.status == "refused"
    cleared = build_and_clear(
        run_id="r2",
        snapshot=snap,
        opf=OpfSolution(residual_mw=0.2, spin_count=8),
        assignment_count=8,
        tolerance_mw=1.0,
        time_source="csac",
        wrapped=True,
    )
    assert cleared.status == "cleared"
