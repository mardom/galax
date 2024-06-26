"""galax: Galactic Dynamix in Jax."""

__all__ = ["MockStream"]

from dataclasses import replace
from typing import TYPE_CHECKING, Any, final

import equinox as eqx
import jax.numpy as jnp

from coordinax import Abstract3DVector, Abstract3DVectorDifferential
from unxt import Quantity

import galax.typing as gt
from galax.coordinates import AbstractPhaseSpacePosition, ComponentShapeTuple
from galax.coordinates._psp.utils import (
    _p_converter,
    _q_converter,
    getitem_vec1time_index,
)
from galax.utils._shape import batched_shape, vector_batched_shape

if TYPE_CHECKING:
    from typing import Self


@final
class MockStream(AbstractPhaseSpacePosition):
    """Mock stream object.

    Parameters
    ----------
    q : Array[float, (*batch, 3)]
        Positions (x, y, z).
    p : Array[float, (*batch, 3)]
        Conjugate momenta (v_x, v_y, v_z).
    t : Array[float, (*batch,)]
        Array of times corresponding to the positions.
    release_time : Array[float, (*batch,)]
        Release time of the stream particles [Myr].
    """

    q: Abstract3DVector = eqx.field(converter=_q_converter)
    """Positions (x, y, z)."""

    p: Abstract3DVectorDifferential = eqx.field(converter=_p_converter)
    r"""Conjugate momenta (v_x, v_y, v_z)."""

    t: gt.QVecTime = eqx.field(converter=Quantity["time"].constructor)
    """Array of times corresponding to the positions."""

    release_time: gt.QVecTime = eqx.field(converter=Quantity["time"].constructor)
    """Release time of the stream particles [Myr]."""

    # ==========================================================================
    # Array properties

    @property
    def _shape_tuple(self) -> tuple[gt.Shape, ComponentShapeTuple]:
        """Batch ."""
        qbatch, qshape = vector_batched_shape(self.q)
        pbatch, pshape = vector_batched_shape(self.p)
        tbatch, _ = batched_shape(self.t, expect_ndim=0)
        batch_shape = jnp.broadcast_shapes(qbatch, pbatch, tbatch)
        return batch_shape, ComponentShapeTuple(q=qshape, p=pshape, t=1)

    def __getitem__(self, index: Any) -> "Self":
        """Return a new object with the given slice applied."""
        # Compute subindex
        subindex = getitem_vec1time_index(index, self.t)
        # Apply slice
        return replace(
            self,
            q=self.q[index],
            p=self.p[index],
            t=self.t[subindex],
            release_time=self.release_time[subindex],
        )
