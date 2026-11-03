# Energy-preserving relaxed thermal boundary

The two C++ files derive from OpenCFD OpenFOAM v1912.200626's `externalWallHeatFluxTemperature` and retain its GPL-3.0-or-later license and upstream copyright notices. `COPYING` contains the upstream license. This is a project-local boundary type, `saunaHeatFluxTemperature`; system OpenFOAM libraries are not modified.

Upstream source archive: Ubuntu source `openfoam_1912.200626.orig.tar.bz2`, SHA256 `c75ca0f04cc4f49708296c1926cbde9d0138b3fef298fed54270dfe29e2df404`.

Changes:
1. Rename the type to avoid overriding upstream registration.
2. Relax the *complete mixed boundary value*. If the original mixed fraction is `f`, reference value `r`, extrapolated gradient value `g`, previous wall temperature `Tp` and relaxation `a`, the target is `a*(f*r + (1-f)*g) + (1-a)*Tp`. Use `f_new=a*f+1-a` and `r_new=(a*f*r+(1-a)*Tp)/f_new`. The gradient is unchanged. Upstream v1912 uses `r_new=a*r+(1-a)*Tp` instead, which does not preserve the fixed point for `a<1`, and for `f=0` creates an artificial sink.
3. Serialize relaxation for **all** boundary modes so restarts preserve the numerics.

A standalone C++ regression test uses the production relaxation helper. Full CFD audits independently check prescribed heater power against outgoing heat; this prevents a visually convincing but nonconservative result from passing.

Build with `bash scripts/build_thermal_boundary.sh`. Only matching v1912 headers are used. The download is hash checked. Compile output is ignored; the source and exact build procedure are versioned.

The boundary also supports `rampStartPower` and `rampIterations` for a linear startup continuation of the prescribed heater power. With `buoyantSimpleFoam`, the independent coordinate is the SIMPLE iteration count, not physical seconds. The final fixed point uses the full target power. This helper is tested together with relaxation and serialized for deterministic restarts.
