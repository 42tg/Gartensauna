#include <initializer_list>
#include <cassert>
#include <cmath>
#include "../simulation/thermal/boundary/relaxMixed.H"
int main() {
    assert(saunaThermal::rampPower(3000,0,500,0)==0);
    assert(saunaThermal::rampPower(3000,0,500,250)==1500);
    assert(saunaThermal::rampPower(3000,0,500,700)==3000);
    assert(saunaThermal::rampPower(3000,0,0,0)==3000);
    for (double f : {0., .2, .7, 1.})
        for (double a : {.05, .2, .8, 1.}) {
            double reference=500, gradientValue=400, previous=300;
            auto c=saunaThermal::relaxMixed(f,reference,previous,a);
            double actual=c.fraction*c.reference+(1-c.fraction)*gradientValue;
            double expected=a*(f*reference+(1-f)*gradientValue)+(1-a)*previous;
            assert(std::abs(actual-expected)<1e-10);
            // Once converged, relaxation must not alter any physical boundary.
            previous=f*reference+(1-f)*gradientValue;
            c=saunaThermal::relaxMixed(f,reference,previous,a);
            actual=c.fraction*c.reference+(1-c.fraction)*gradientValue;
            assert(std::abs(actual-previous)<1e-10);
        }
    // The upstream gradient formula would yield 272 K, instead of 320 K.
    auto c=saunaThermal::relaxMixed(0,0,300,.2);
    assert(std::abs(c.fraction*c.reference+(1-c.fraction)*400-320)<1e-10);
}
