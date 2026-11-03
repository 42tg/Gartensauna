// Project-local mixed boundary relaxation, GPL-3.0-or-later.
#ifndef SAUNA_RELAX_MIXED_H
#define SAUNA_RELAX_MIXED_H
namespace saunaThermal {
inline double rampPower(double target, double start, double iterations, double step) {
    if (iterations <= 0 || step >= iterations) return target;
    const double f = step > 0 ? step/iterations : 0;
    return start + f*(target-start);
}
struct MixedCoefficients { double fraction; double reference; };
inline MixedCoefficients relaxMixed(double fraction, double reference,
                                    double previous, double relaxation) {
    const double f = relaxation*fraction + (1-relaxation);
    return {f, f > 1e-15
        ? (relaxation*fraction*reference + (1-relaxation)*previous)/f
        : reference};
}
}
#endif
