"""Interoperability."""

__all__ = ["gala_to_galax"]

from functools import singledispatch
from typing import TypeVar

try:  # TODO: less hacky way of supporting optional dependencies
    import pytest
except ImportError:  # pragma: no cover
    pass
else:
    _ = pytest.importorskip("gala")

import gala.potential as gp
from gala.units import DimensionlessUnitSystem as GalaDimensionlessUnitSystem

import coordinax.operators as cxo
from coordinax.operators import IdentityOperator
from unxt import Quantity
from unxt.unitsystems import DimensionlessUnitSystem

import galax.potential as gpx

##############################################################################
# GALA -> GALAX


@singledispatch
def gala_to_galax(pot: gp.PotentialBase, /) -> gpx.AbstractPotentialBase:
    """Convert a :mod:`gala` potential to a :mod:`galax` potential.

    Parameters
    ----------
    pot :  :class:`~gala.potential.PotentialBase`
        :mod:`gala` potential.

    Returns
    -------
    gala_pot : :class:`~galax.potential.AbstractPotentialBase`
        :mod:`galax` potential.

    Examples
    --------
    The required imports for the examples below are:

    >>> import astropy.units as u
    >>> import gala.potential as gp
    >>> import gala.units as gu
    >>> import galax.potential as gpx

    Going in alphabetical order...

    Composite Potential:

    >>> gpot = gp.CompositePotential(
    ...     disk=gp.MiyamotoNagaiPotential(m=1e11, a=6.5, b=0.26, units=gu.galactic),
    ...     halo=gp.NFWPotential(m=1e12, r_s=20, units=gu.galactic),
    ... )
    >>> gpx.io.gala_to_galax(gpot)
    CompositePotential({'disk': MiyamotoNagaiPotential( ... ),
                        'halo': NFWPotential( ... )})

    Hernquist potential:

    >>> gpot = gp.HernquistPotential(m=1e11 * u.Msun, c=10 * u.kpc, units=gu.galactic)
    >>> gpx.io.gala_to_galax(gpot)
    HernquistPotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m_tot=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ),
      c=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) ) )

    Isochrone potential:

    >>> gpot = gp.IsochronePotential(m=1e11 * u.Msun, b=10 * u.kpc, units=gu.galactic)
    >>> gpx.io.gala_to_galax(gpot)
    IsochronePotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m_tot=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ),
      b=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) ) )

    Kepler potential:

    >>> gpot = gp.KeplerPotential(m=1e11 * u.Msun, units=gu.galactic)
    >>> gpx.io.gala_to_galax(gpot)
    KeplerPotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m_tot=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ) )

    >>> gpot = gp.LeeSutoTriaxialNFWPotential(
    ...     v_c=220, r_s=20, a=1, b=0.9, c=0.8, units=gu.galactic )
    >>> gpx.io.gala_to_galax(gpot)
    LeeSutoTriaxialNFWPotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ),
      r_s=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) ),
      a1=ConstantParameter( unit=Unit(dimensionless), value=Quantity[...]( value=f64[], unit=Unit(dimensionless) ) ),
      a2=ConstantParameter( unit=Unit(dimensionless), value=Quantity[...]( value=f64[], unit=Unit(dimensionless) ) ),
      a3=ConstantParameter( unit=Unit(dimensionless), value=Quantity[...]( value=f64[], unit=Unit(dimensionless) ) )
    )

    Milky Way potential:

    >>> gpot = gp.MilkyWayPotential()
    >>> gpx.io.gala_to_galax(gpot)
    MilkyWayPotential({'disk': MiyamotoNagaiPotential( ... ),
                       'halo': NFWPotential( ... ),
                       'bulge': HernquistPotential( ... ),
                       'nucleus': HernquistPotential( ... )})

    MiyamotoNagai potential:

    >>> gpot = gp.MiyamotoNagaiPotential(m=1e11, a=6.5, b=0.26, units=gu.galactic)
    >>> gpx.io.gala_to_galax(gpot)
    MiyamotoNagaiPotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m_tot=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ),
      a=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) ),
      b=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) ) )

    NFW potential:

    >>> gpot = gp.NFWPotential(m=1e12, r_s=20, units=gu.galactic)
    >>> gpx.io.gala_to_galax(gpot)
    NFWPotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ),
      r_s=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) ) )

    Null potential:

    >>> gpot = gp.NullPotential()
    >>> gpx.io.gala_to_galax(gpot)
    NullPotential( units=DimensionlessUnitSystem(),
                   constants=ImmutableDict({'G': ...}) )
    """  # noqa: E501
    msg = (
        "`gala_to_galax` does not have a registered function to convert "
        f"{pot.__class__.__name__!r} to a `galax.AbstractPotentialBase` instance."
    )
    raise NotImplementedError(msg)


# -----------------------
# Helper functions

PT = TypeVar("PT", bound=gpx.AbstractPotentialBase)


def _get_frame(pot: gp.PotentialBase, /) -> cxo.AbstractOperator:
    frame = cxo.GalileanSpatialTranslationOperator(
        Quantity(pot.origin, unit=pot.units["length"])
    )
    if pot.R is not None:
        frame = cxo.GalileanRotationOperator(pot.R) | frame
    return cxo.simplify_op(frame)


def _apply_frame(frame: cxo.AbstractOperator, pot: PT, /) -> PT | gpx.PotentialFrame:
    return (
        pot if isinstance(frame, IdentityOperator) else gpx.PotentialFrame(pot, frame)
    )


# -----------------------------------------------------------------------------
# General rules


@gala_to_galax.register
def _gala_to_galax_composite(pot: gp.CompositePotential, /) -> gpx.CompositePotential:
    """Convert a Gala CompositePotential to a Galax potential."""
    return gpx.CompositePotential(**{k: gala_to_galax(p) for k, p in pot.items()})


_GALA_TO_GALAX_REGISTRY: dict[type[gp.PotentialBase], type[gpx.AbstractPotential]] = {
    gp.HernquistPotential: gpx.HernquistPotential,
    gp.IsochronePotential: gpx.IsochronePotential,
    gp.KeplerPotential: gpx.KeplerPotential,
    gp.KuzminPotential: gpx.KuzminPotential,
    gp.LogarithmicPotential: gpx.LogarithmicPotential,
    gp.MiyamotoNagaiPotential: gpx.MiyamotoNagaiPotential,
    gp.PlummerPotential: gpx.PlummerPotential,
    gp.PowerLawCutoffPotential: gpx.PowerLawCutoffPotential,
}


@gala_to_galax.register(gp.HernquistPotential)
@gala_to_galax.register(gp.IsochronePotential)
@gala_to_galax.register(gp.KeplerPotential)
@gala_to_galax.register(gp.MiyamotoNagaiPotential)
@gala_to_galax.register(gp.PlummerPotential)
@gala_to_galax.register(gp.PowerLawCutoffPotential)
def _gala_to_galax_registered(
    gala: gp.PotentialBase, /
) -> gpx.AbstractPotential | gpx.PotentialFrame:
    """Convert a Gala HernquistPotential to a Galax potential."""
    if isinstance(gala.units, GalaDimensionlessUnitSystem):
        msg = "Galax does not support converting dimensionless units."
        raise TypeError(msg)

    # TODO: this is a temporary solution. It would be better to map each
    # potential individually.
    params = dict(gala.parameters)
    params["m_tot"] = params.pop("m")

    pot = _GALA_TO_GALAX_REGISTRY[type(gala)](**params, units=gala.units)
    return _apply_frame(_get_frame(gala), pot)


# -----------------------------------------------------------------------------
# Builtin potentials


@gala_to_galax.register
def _gala_to_galax_null(_: gp.NullPotential, /) -> gpx.NullPotential:
    """Convert a Gala NullPotential to a Galax potential.

    Examples
    --------
    >>> import gala.potential as gp
    >>> import galax.potential as gpx

    >>> gpot = gp.NullPotential()
    >>> gpx.io.gala_to_galax(gpot)
    NullPotential( units=DimensionlessUnitSystem(),
                   constants=ImmutableDict({'G': ...}) )

    """
    return gpx.NullPotential(units=DimensionlessUnitSystem())


@gala_to_galax.register
def _gala_to_galax_nfw(
    gala: gp.NFWPotential, /
) -> gpx.NFWPotential | gpx.PotentialFrame:
    """Convert a Gala NFWPotential to a Galax potential.

    Examples
    --------
    >>> import gala.potential as gp
    >>> import gala.units as gu
    >>> import galax.potential as gpx

    >>> gpot = gp.NFWPotential(m=1e12, r_s=20, units=gu.galactic)
    >>> gpx.io.gala_to_galax(gpot)
    NFWPotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ),
      r_s=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) )
    )

    """  # noqa: E501
    params = gala.parameters
    pot = gpx.NFWPotential(m=params["m"], r_s=params["r_s"], units=gala.units)
    return _apply_frame(_get_frame(gala), pot)


@gala_to_galax.register
def _gala_to_galax_leesutotriaxialnfw(
    pot: gp.LeeSutoTriaxialNFWPotential, /
) -> gpx.LeeSutoTriaxialNFWPotential:
    """Convert a Gala LeeSutoTriaxialNFWPotential to a Galax potential.

    Examples
    --------
    >>> import gala.potential as gp
    >>> import gala.units as gu
    >>> import galax.potential as gpx

    >>> gpot = gp.LeeSutoTriaxialNFWPotential(
    ...     v_c=220, r_s=20, a=1, b=0.9, c=0.8, units=gu.galactic )
    >>> gpx.io.gala_to_galax(gpot)
    LeeSutoTriaxialNFWPotential(
      units=UnitSystem(kpc, Myr, solMass, rad),
      constants=ImmutableDict({'G': ...}),
      m=ConstantParameter( unit=Unit("solMass"), value=Quantity[...](value=f64[], unit=Unit("solMass")) ),
      r_s=ConstantParameter( unit=Unit("kpc"), value=Quantity[...](value=f64[], unit=Unit("kpc")) ),
      a1=ConstantParameter( unit=Unit(dimensionless), value=Quantity[...]( value=f64[], unit=Unit(dimensionless) ) ),
      a2=ConstantParameter( unit=Unit(dimensionless), value=Quantity[...]( value=f64[], unit=Unit(dimensionless) ) ),
      a3=ConstantParameter( unit=Unit(dimensionless), value=Quantity[...]( value=f64[], unit=Unit(dimensionless) ) )
    )

    """  # noqa: E501
    units = pot.units
    params = pot.parameters
    G = Quantity(pot.G, units["length"] ** 3 / units["time"] ** 2 / units["mass"])

    return gpx.LeeSutoTriaxialNFWPotential(
        m=params["v_c"] ** 2 * params["r_s"] / G,
        r_s=params["r_s"],
        a1=params["a"],
        a2=params["b"],
        a3=params["c"],
        units=units,
        constants={"G": G},
    )


# -----------------------------------------------------------------------------
# MW potentials


@gala_to_galax.register
def _gala_to_galax_bovymw2014(
    pot: gp.BovyMWPotential2014, /
) -> gpx.BovyMWPotential2014:
    """Convert a Gala BovyMWPotential2014 to a Galax potential.

    Examples
    --------
    .. invisible-code-block: python

        from galax.utils._optional_deps import GSL_ENABLED

    .. skip: start if(not GSL_ENABLED, reason="requires GSL")

    >>> import gala.potential as gp
    >>> import galax.potential as gpx

    >>> gpot = gp.BovyMWPotential2014()
    >>> gpx.io.gala_to_galax(gpot)
    BovyMWPotential2014({'disk': MiyamotoNagaiPotential( ... ),
                        'bulge': PowerLawCutoffPotential( ... ),
                        'halo': NFWPotential( ... )})

    .. skip: end

    """
    return gpx.BovyMWPotential2014(
        disk=gala_to_galax(pot["disk"]),
        bulge=gala_to_galax(pot["bulge"]),
        halo=gala_to_galax(pot["halo"]),
    )


@gala_to_galax.register
def _gala_to_galax_mw(pot: gp.MilkyWayPotential, /) -> gpx.MilkyWayPotential:
    """Convert a Gala MilkyWayPotential to a Galax potential.

    Examples
    --------
    >>> import gala.potential as gp
    >>> import galax.potential as gpx

    >>> gpot = gp.MilkyWayPotential()
    >>> gpx.io.gala_to_galax(gpot)
    MilkyWayPotential({'disk': MiyamotoNagaiPotential( ... ),
                       'halo': NFWPotential( ... ),
                       'bulge': HernquistPotential( ... ),
                       'nucleus': HernquistPotential( ... )})

    """
    return gpx.MilkyWayPotential(
        disk=gala_to_galax(pot["disk"]),
        halo=gala_to_galax(pot["halo"]),
        bulge=gala_to_galax(pot["bulge"]),
        nucleus=gala_to_galax(pot["nucleus"]),
    )
