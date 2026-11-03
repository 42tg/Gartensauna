#!/usr/bin/env bash
# OpenFOAM v1912 source headers/build tools + a small GPL-compatible boundary fix.
set -euo pipefail
sauna_root=$(cd "$(dirname "$0")/.." && pwd)
sauna_source_parent=${SAUNA_FOAM_SOURCE_PARENT:-"$sauna_root/build/openfoam-source"}
sauna_source="$sauna_source_parent/openfoam-OpenFOAM-v1912.200626"
sauna_archive="$sauna_source_parent/openfoam_1912.200626.orig.tar.bz2"
mkdir -p "$sauna_source_parent" "$sauna_root/build/thermal-lib"
if [[ ! -f "$sauna_source/etc/bashrc" ]]; then
  curl --fail --location --retry 2 --max-time 180 \
    https://snapshot.ubuntu.com/ubuntu/20260828T000000Z/pool/universe/o/openfoam/openfoam_1912.200626.orig.tar.bz2 \
    -o "$sauna_archive"
  echo "c75ca0f04cc4f49708296c1926cbde9d0138b3fef298fed54270dfe29e2df404  $sauna_archive" | sha256sum -c -
  tar --no-same-owner -xjf "$sauna_archive" -C "$sauna_source_parent"
fi
# The upstream environment script is not safe under nounset.
set +e +u
set +o pipefail
source "$sauna_source/etc/bashrc" WM_MPLIB=DUMMY
set -euo pipefail
export SAUNA_FOAM_LIBDIR=${FOAM_RUNTIME_ROOT:+"$FOAM_RUNTIME_ROOT/usr/lib"}
SAUNA_FOAM_LIBDIR=${SAUNA_FOAM_LIBDIR:-/usr/lib}
export FOAM_USER_LIBBIN="$sauna_root/build/thermal-lib"
make -C "$sauna_source/wmake/src"
(cd "$sauna_source" && wmakeLnIncludeAll)
wmake libso "$sauna_root/simulation/thermal/boundary"
test -s "$FOAM_USER_LIBBIN/libsaunaThermal.so"
