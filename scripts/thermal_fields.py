"""OpenFOAM v1912 ideal-gas RANS + grey diffuse discrete-ordinates radiation."""
from thermal_case import header,PATCHES

def write_case(dest,meta):
    c=meta['config'];T0=c['initial_temperature_C']+273.15;Tin=c['supply_temperature_C']+273.15;Ta=c['outside_temperature_C']+273.15
    q=c['inlet_flow_m3h']/3600;u=q/meta['patches']['supply']['area_m2']
    k=max(1.5*(.05*u)**2,1e-5);eps=max(.09**.75*k**1.5/.02,1e-6)
    def dictionary(folder,name,text):
        p=dest/folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(header('dictionary',name)+text+'\n')
    def field(name,dim,value,bc,vector=False):
        p=dest/'0'/name;p.parent.mkdir(exist_ok=True)
        p.write_text(header('volVectorField' if vector else 'volScalarField',name)+f'dimensions [{dim}];\ninternalField uniform {value};\nboundaryField\n{{\n'+ '\n'.join(f'{n}\n{{{bc[n]}}}' for n in PATCHES)+'\n}\n')
    U={n:'type noSlip;' for n in PATCHES};U['supply']=f'type fixedValue; value uniform (0 {u} 0);';U['exhaust']='type pressureInletOutletVelocity; value uniform (0 0 0);'
    field('U','0 1 -1 0 0 0 0','(0 0 0)',U,True)
    p={n:'type calculated; value uniform 101325;' for n in PATCHES};field('p','1 -1 -2 0 0 0 0',101325,p)
    prgh={n:'type fixedFluxPressure; value uniform 101325;' for n in PATCHES};prgh['exhaust']='type prghPressure; p uniform 101325; value uniform 101325;'
    field('p_rgh','1 -1 -2 0 0 0 0',101325,prgh)
    thermal={};qr='qr qr; qrRelaxation 0.1;' if c['radiation'] else ''
    for n in PATCHES:
        if n=='supply':thermal[n]=f'type fixedValue; value uniform {Tin};'
        elif n=='exhaust':thermal[n]=f'type inletOutlet; inletValue uniform {Tin}; value uniform {T0};'
        else:
            mode=f'mode power; Q {c["heater_power_W"]}; rampStartPower 0; rampIterations {c["ramp_iterations"]};' if n=='heater' else 'mode flux; q uniform 0;' if n=='benches' else f'mode coefficient; h uniform {c[{"walls":"wall","glass":"glass","roof":"roof","floor":"floor"}[n]+"_conductance_W_m2K"]}; Ta constant {Ta};'
            thermal[n]=f'type saunaHeatFluxTemperature; {mode} kappaMethod fluidThermo; {qr} relaxation 0.2; value uniform {T0};'
    field('T','0 0 0 1 0 0 0',T0,thermal)
    for name,dim,val,walltype in [('k','0 2 -2 0 0 0 0',k,'kqRWallFunction'),('epsilon','0 2 -3 0 0 0 0',eps,'epsilonWallFunction'),('nut','0 2 -1 0 0 0 0',0,'nutkWallFunction'),('alphat','1 -1 -1 0 0 0 0',0,'compressible::alphatWallFunction')]:
        bc={n:f'type {walltype}; value uniform {val};'+(' Prt 0.85;' if name=='alphat' else '') for n in PATCHES}
        if name in ('k','epsilon'):
            bc['supply']=f'type fixedValue; value uniform {val};';bc['exhaust']=f'type inletOutlet; inletValue uniform {val}; value uniform {val};'
        else:
            for n in ('supply','exhaust'):bc[n]=f'type calculated; value uniform {val};'
        field(name,dim,val,bc)
    dictionary('constant','thermophysicalProperties','''thermoType { type heRhoThermo; mixture pureMixture; transport sutherland; thermo hConst; equationOfState perfectGas; specie specie; energy sensibleEnthalpy; }
mixture { specie { molWeight 28.97; } thermodynamics { Cp 1005; Hf 0; } transport { As 1.458e-6; Ts 110.4; } }
''')
    dictionary('constant','turbulenceProperties','simulationType RAS; RAS { RASModel buoyantKEpsilon; turbulence on; printCoeffs on; }')
    (dest/'constant/g').write_text(header('uniformDimensionedVectorField','g')+f'dimensions [0 1 -2 0 0 0 0]; value (0 0 {-c["gravity_m_s2"]});\n')
    dictionary('constant','radiationProperties',f'''radiation {"on" if c['radiation'] else "off"};
radiationModel {"fvDOM" if c['radiation'] else "none"};
fvDOMCoeffs {{ nPhi {c['radiation_nPhi']}; nTheta {c['radiation_nTheta']}; tolerance 1e-4; maxIter 5; }}
solverFreq 1;
absorptionEmissionModel constantAbsorptionEmission;
constantAbsorptionEmissionCoeffs {{ absorptivity absorptivity [0 -1 0 0 0 0 0] 0; emissivity emissivity [0 -1 0 0 0 0 0] 0; E E [1 -1 -3 0 0 0 0] 0; }}
scatterModel none; sootModel none;
''')
    dictionary('constant','boundaryRadiationProperties','\n'.join(f'{n} {{type lookup; emissivity {1 if n in ("supply","exhaust") else c["surface_emissivity"]}; absorptivity {1 if n in ("supply","exhaust") else c["surface_emissivity"]}; transmissivity 0;}}' for n in PATCHES))
    if c['radiation']:
        field('IDefault','1 0 -3 0 0 0 0',0,{n:'type greyDiffusiveRadiation; value uniform 0;' for n in PATCHES})
    dictionary('system','fvSchemes','''ddtSchemes { default steadyState; }
gradSchemes { default cellLimited Gauss linear 1; }
divSchemes {
 default none;
 div(phi,U) bounded Gauss upwind;
 div(phi,h) bounded Gauss upwind;
 div(phi,K) bounded Gauss upwind;
 div(phi,k) bounded Gauss upwind;
 div(phi,epsilon) bounded Gauss upwind;
 div(Ji,Ii_h) Gauss upwind;
 div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
''')
    dictionary('system','fvSolution','''solvers {
 p_rgh { solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0; maxIter 200; }
 Ii { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0; maxIter 100; }
 "(U|h|k|epsilon)" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.05; }
}
SIMPLE { nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 101325; }
relaxationFactors { fields { rho 1; p_rgh 0.3; } equations { U 0.1; h 0.1; k 0.3; epsilon 0.3; "ILambda.*" 0.7; } }
''')
    dictionary('system','controlDict',f'''application buoyantSimpleFoam;
libs ("libsaunaThermal.so");
startFrom latestTime; startTime 0; stopAt endTime; endTime {c['iterations']}; deltaT 1;
writeControl timeStep; writeInterval 100; purgeWrite 3;
writeFormat ascii; writePrecision 10; writeCompression off; timeFormat general; timePrecision 8;
runTimeModifiable false;
functions {{ }}
''')
