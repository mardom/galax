"""galax: Galactic Dynamix in Jax."""

__all__ = ["BovyMWPotential2014", "MilkyWayPotential"]


from collections.abc import Mapping
from dataclasses import KW_ONLY
from types import MappingProxyType
from typing import Any, ClassVar, TypeVar, final

import equinox as eqx

from unxt import Quantity
from unxt.unitsystems import AbstractUnitSystem, dimensionless, galactic, unitsystem

from .base import AbstractPotentialBase, default_constants
from .builtin.builtin import (
    HernquistPotential,
    MiyamotoNagaiPotential,
    PowerLawCutoffPotential,
)
from .builtin.nfw import NFWPotential
from .composite import AbstractCompositePotential
from galax.utils import ImmutableDict

T = TypeVar("T", bound=AbstractPotentialBase)


def _parse_input_comp(
    cls: type[T],
    instance: T | Mapping[str, Any] | None,
    default: Mapping[str, Any],
    units: AbstractUnitSystem,
) -> T:
    if isinstance(instance, cls):
        return instance

    if units == dimensionless:
        default = {k: v.value for k, v in default.items()}

    return cls(units=units, **dict(default) | (dict(instance or {})))


@final
class BovyMWPotential2014(AbstractCompositePotential):
    """``MWPotential2014`` from Bovy (2015).

    An implementation of the ``MWPotential2014``
    `from galpy <https://galpy.readthedocs.io/en/latest/potential.html>`_
    and described in `Bovy (2015)
    <https://ui.adsabs.harvard.edu/#abs/2015ApJS..216...29B/abstract>`_.

    This potential consists of a spherical bulge and dark matter halo, and a
    Miyamoto-Nagai disk component.

    Parameters
    ----------
    units : `~gala.units.UnitSystem` (optional)
        Set of non-reducable units that specify (at minimum) the
        length, mass, time, and angle units.
    disk : dict (optional)
        Parameters to be passed to the :class:`~gala.potential.MiyamotoNagaiPotential`.
    bulge : dict (optional)
        Parameters to be passed to the :class:`~gala.potential.PowerLawCutoffPotential`.
    halo : dict (optional)
        Parameters to be passed to the :class:`~gala.potential.NFWPotential`.

    Note: in subclassing, order of arguments must match order of potential
    components added at bottom of init.
    """

    _data: dict[str, AbstractPotentialBase] = eqx.field(init=False)
    _: KW_ONLY
    units: AbstractUnitSystem = eqx.field(
        default=galactic, static=True, converter=unitsystem
    )
    constants: ImmutableDict[Quantity] = eqx.field(
        default=default_constants, converter=ImmutableDict
    )

    # TODO: as an actual `MiyamotoNagaiPotential`, then use `replace`?
    _default_disk: ClassVar[MappingProxyType[str, Quantity]] = MappingProxyType(
        {
            "m_tot": Quantity(68_193_902_782.346756, "Msun"),
            "a": Quantity(3.0, "kpc"),
            "b": Quantity(280, "pc"),
        }
    )
    # TODO: as an actual `PowerLawCutoffPotential`, then use `replace`?
    _default_bulge: ClassVar[MappingProxyType[str, Any]] = MappingProxyType(
        {
            "m_tot": Quantity(4501365375.06545, "Msun"),
            "alpha": 1.8,
            "r_c": Quantity(1.9, "kpc"),
        }
    )
    # TODO: as an actual `NFWPotential`, then use `replace`?
    _default_halo: ClassVar[MappingProxyType[str, Quantity]] = MappingProxyType(
        {"m": Quantity(4.3683325e11, "Msun"), "r_s": Quantity(16, "kpc")}
    )

    def __init__(
        self,
        *,
        disk: MiyamotoNagaiPotential | Mapping[str, Any] | None = None,
        bulge: PowerLawCutoffPotential | Mapping[str, Any] | None = None,
        halo: NFWPotential | Mapping[str, Any] | None = None,
        units: Any = galactic,
        constants: Any = default_constants,
    ) -> None:
        units_ = unitsystem(units) if units is not None else galactic

        super().__init__(
            disk=_parse_input_comp(
                MiyamotoNagaiPotential, disk, self._default_disk, units_
            ),
            bulge=_parse_input_comp(
                PowerLawCutoffPotential, bulge, self._default_bulge, units_
            ),
            halo=_parse_input_comp(NFWPotential, halo, self._default_halo, units_),
            units=units_,
            constants=constants,
        )


@final
class MilkyWayPotential(AbstractCompositePotential):
    """Milky Way mass model.

    A simple mass-model for the Milky Way consisting of a spherical nucleus and
    bulge, a Miyamoto-Nagai disk, and a spherical NFW dark matter halo.

    The disk model is taken from `Bovy (2015)
    <https://ui.adsabs.harvard.edu/#abs/2015ApJS..216...29B/abstract>`_ - if you
    use this potential, please also cite that work.

    Default parameters are fixed by fitting to a compilation of recent mass
    measurements of the Milky Way, from 10 pc to ~150 kpc.

    Parameters
    ----------
    units : `~unxt.AbstractUnitSystem` (optional)
        Set of non-reducable units.
    disk : dict (optional)
        Parameters to be passed to the :class:`~galax.potential.MiyamotoNagaiPotential`.
    bulge : dict (optional)
        Parameters to be passed to the :class:`~galax.potential.HernquistPotential`.
    halo : dict (optional)
        Parameters to be passed to the :class:`~galax.potential.NFWPotential`.
    nucleus : dict (optional)
        Parameters to be passed to the :class:`~galax.potential.HernquistPotential`.

    Note: in subclassing, order of arguments must match order of potential
    components added at bottom of init.
    """

    _data: dict[str, AbstractPotentialBase] = eqx.field(init=False)
    _: KW_ONLY
    units: AbstractUnitSystem = eqx.field(init=True, static=True, converter=unitsystem)
    constants: ImmutableDict[Quantity] = eqx.field(
        default=default_constants, converter=ImmutableDict
    )

    # TODO: as an actual `MiyamotoNagaiPotential`, then use `replace`?
    _default_disk: ClassVar[MappingProxyType[str, Quantity]] = MappingProxyType(
        {
            "m_tot": Quantity(6.8e10, "Msun"),
            "a": Quantity(3.0, "kpc"),
            "b": Quantity(0.28, "kpc"),
        }
    )
    # TODO: as an actual `NFWPotential`, then use `replace`?
    _default_halo: ClassVar[MappingProxyType[str, Quantity]] = MappingProxyType(
        {"m": Quantity(5.4e11, "Msun"), "r_s": Quantity(15.62, "kpc")}
    )
    # TODO: as an actual `HernquistPotential`, then use `replace`?
    _default_bulge: ClassVar[MappingProxyType[str, Quantity]] = MappingProxyType(
        {"m_tot": Quantity(5e9, "Msun"), "c": Quantity(1.0, "kpc")}
    )
    # TODO: as an actual `HernquistPotential`, then use `replace`?
    _default_nucleus: ClassVar[MappingProxyType[str, Quantity]] = MappingProxyType(
        {"m_tot": Quantity(1.71e9, "Msun"), "c": Quantity(0.07, "kpc")}
    )

    def __init__(
        self,
        *,
        disk: MiyamotoNagaiPotential | Mapping[str, Any] | None = None,
        halo: NFWPotential | Mapping[str, Any] | None = None,
        bulge: HernquistPotential | Mapping[str, Any] | None = None,
        nucleus: HernquistPotential | Mapping[str, Any] | None = None,
        units: Any = galactic,
        constants: Any = default_constants,
    ) -> None:
        units_ = unitsystem(units) if units is not None else galactic

        super().__init__(
            disk=_parse_input_comp(
                MiyamotoNagaiPotential, disk, self._default_disk, units_
            ),
            halo=_parse_input_comp(NFWPotential, halo, self._default_halo, units_),
            bulge=_parse_input_comp(
                HernquistPotential, bulge, self._default_bulge, units_
            ),
            nucleus=_parse_input_comp(
                HernquistPotential, nucleus, self._default_nucleus, units_
            ),
            units=units_,
            constants=constants,
        )
