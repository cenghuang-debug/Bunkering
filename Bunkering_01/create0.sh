#!/bin/bash
# ================================================
# Automatic 0/ folder generator — updated March 2025
# Changes:
#   - No 'inlet' patch
#   - Low velocity inflow (-0.1 0 0) moved to 'right' boundary
#   - right now uses fixedValue for U
# ================================================

mkdir -p 0

# ==================== U ====================
cat > 0/U << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    right
    {
        type            fixedValue;
        value           uniform (-0.1 0 0);
    }
    left
    {
        type            pressureInletOutletVelocity;
        value           $internalField;
        phi             phi;
    }
    front
    {
        type            pressureInletOutletVelocity;
        value           $internalField;
        phi             phi;
    }
    back
    {
        type            pressureInletOutletVelocity;
        value           $internalField;
        phi             phi;
    }
    top
    {
        type            pressureInletOutletVelocity;
        value           $internalField;
        phi             phi;
    }
    bottom
    {
        type            noSlip;
    }
    bunkering-boat_m
    {
        type            noSlip;
    }
    bunkering-quay_m
    {
        type            noSlip;
    }
    nozzle_holder_wall
    {
        type            noSlip;
    }
    nozzle
    {
        type            flowRateInletVelocity;
        volumetricFlowRate
        {
            type            csvFile;
            file            "$FOAM_CASE/constant/vfr_H2_half.csv";
            nHeaderLine     1;
            refColumn       0;
            componentColumns (1);
            separator       ",";
            mergeSeparators no;
            outOfBounds     clamp;
        }
        value           $internalField;
        rho             rho;
        rhoInlet        8.6e-2;
    }
}
// ************************************************************************* //
EOF

# ==================== p ====================
cat > 0/p << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 101325;

boundaryField
{
    right               { type fixedValue; value $internalField; }
    left                { type fixedValue; value $internalField; }
    front               { type fixedValue; value $internalField; }
    back                { type fixedValue; value $internalField; }
    top                 { type fixedValue; value $internalField; }
    bottom              { type zeroGradient; }
    bunkering-boat_m    { type zeroGradient; }
    bunkering-quay_m    { type zeroGradient; }
    nozzle_holder_wall  { type zeroGradient; }
    nozzle              { type totalPressure; p0 uniform 101325; value $internalField; }
}
// ************************************************************************* //
EOF

# ==================== p_rgh ====================
cat > 0/p_rgh << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 101325;

boundaryField
{
    right               { type fixedFluxPressure; value $internalField; }
    left                { type fixedFluxPressure; value $internalField; }
    front               { type fixedFluxPressure; value $internalField; }
    back                { type fixedFluxPressure; value $internalField; }
    top                 { type fixedFluxPressure; value $internalField; }
    bottom              { type fixedFluxPressure; value $internalField; }
    bunkering-boat_m    { type fixedFluxPressure; value $internalField; }
    bunkering-quay_m    { type fixedFluxPressure; value $internalField; }
    nozzle_holder_wall  { type fixedFluxPressure; value $internalField; }
    nozzle              { type totalPressure; p0 uniform 101325; value $internalField; }
}
// ************************************************************************* //
EOF

# ==================== T ====================
cat > 0/T << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];
internalField   uniform 300;

boundaryField
{
    right               { type inletOutlet; inletValue uniform 300; value $internalField; }
    left                { type inletOutlet; inletValue uniform 300; value $internalField; }
    front               { type inletOutlet; inletValue uniform 300; value $internalField; }
    back                { type inletOutlet; inletValue uniform 300; value $internalField; }
    top                 { type inletOutlet; inletValue uniform 300; value $internalField; }
    bottom              { type zeroGradient; }
    bunkering-boat_m    { type zeroGradient; }
    bunkering-quay_m    { type zeroGradient; }
    nozzle_holder_wall  { type zeroGradient; }
    nozzle              { type fixedValue; value uniform 300; }
}
// ************************************************************************* //
EOF

# ==================== k ====================
cat > 0/k << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      k;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0.1;

boundaryField
{
    right               { type inletOutlet; inletValue $internalField; value $internalField; }
    left                { type inletOutlet; inletValue $internalField; value $internalField; }
    front               { type inletOutlet; inletValue $internalField; value $internalField; }
    back                { type inletOutlet; inletValue $internalField; value $internalField; }
    top                 { type inletOutlet; inletValue $internalField; value $internalField; }
    bottom              { type kqRWallFunction; value $internalField; }
    bunkering-boat_m    { type kqRWallFunction; value $internalField; }
    bunkering-quay_m    { type kqRWallFunction; value $internalField; }
    nozzle_holder_wall  { type kqRWallFunction; value $internalField; }
    nozzle              { type turbulentIntensityKineticEnergyInlet; intensity 0.05; value $internalField; }
}
// ************************************************************************* //
EOF

# ==================== epsilon ====================
cat > 0/epsilon << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      epsilon;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -3 0 0 0 0];
internalField   uniform 0.1;

boundaryField
{
    right               { type inletOutlet; inletValue $internalField; value $internalField; }
    left                { type inletOutlet; inletValue $internalField; value $internalField; }
    front               { type inletOutlet; inletValue $internalField; value $internalField; }
    back                { type inletOutlet; inletValue $internalField; value $internalField; }
    top                 { type inletOutlet; inletValue $internalField; value $internalField; }
    bottom              { type epsilonWallFunction; value $internalField; }
    bunkering-boat_m    { type epsilonWallFunction; value $internalField; }
    bunkering-quay_m    { type epsilonWallFunction; value $internalField; }
    nozzle_holder_wall  { type epsilonWallFunction; value $internalField; }
    nozzle              { type turbulentMixingLengthDissipationRateInlet; mixingLength 0.01; value $internalField; }
}
// ************************************************************************* //
EOF

# ==================== nut & alphat ====================
for field in nut alphat; do
cat > 0/$field << 'EOF'
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      FIELDNAME;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [FIELD_DIM];
internalField   uniform 0;

boundaryField
{
    right               { type calculated; value $internalField; }
    left                { type calculated; value $internalField; }
    front               { type calculated; value $internalField; }
    back                { type calculated; value $internalField; }
    top                 { type calculated; value $internalField; }
    bottom              { type WALL_FUNCTION; value $internalField; }
    bunkering-boat_m    { type WALL_FUNCTION; value $internalField; }
    bunkering-quay_m    { type WALL_FUNCTION; value $internalField; }
    nozzle_holder_wall  { type WALL_FUNCTION; value $internalField; }
    nozzle              { type calculated; value $internalField; }
}
// ************************************************************************* //
EOF

sed -i "s/FIELDNAME/$field/g" 0/$field

if [ "$field" = "alphat" ]; then
    sed -i 's/WALL_FUNCTION/alphatJayatillekeWallFunction; Prt 0.85/g' 0/$field
    sed -i 's/FIELD_DIM/[1 -1 -1 0 0 0 0]/g' 0/$field
else
    sed -i 's/WALL_FUNCTION/nutkWallFunction/g' 0/$field
    sed -i 's/FIELD_DIM/[0 2 -1 0 0 0 0]/g' 0/$field
fi
done

# ==================== Species (H2, air, Ydefault) ====================
for field in H2 air Ydefault; do
cat > 0/$field << EOF
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      $field;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];
internalField   uniform $( [[ $field == "H2" ]] && echo 0 || echo 1 );

boundaryField
{
    right               { type inletOutlet; inletValue uniform $( [[ $field == "H2" ]] && echo 0 || echo 1 ); value \$internalField; }
    left                { type inletOutlet; inletValue uniform $( [[ $field == "H2" ]] && echo 0 || echo 1 ); value \$internalField; }
    front               { type inletOutlet; inletValue uniform $( [[ $field == "H2" ]] && echo 0 || echo 1 ); value \$internalField; }
    back                { type inletOutlet; inletValue uniform $( [[ $field == "H2" ]] && echo 0 || echo 1 ); value \$internalField; }
    top                 { type inletOutlet; inletValue uniform $( [[ $field == "H2" ]] && echo 0 || echo 1 ); value \$internalField; }
    bottom              { type zeroGradient; }
    bunkering-boat_m    { type zeroGradient; }
    bunkering-quay_m    { type zeroGradient; }
    nozzle_holder_wall  { type zeroGradient; }
    nozzle              { type fixedValue; value uniform $( [[ $field == "H2" ]] && echo 1 || echo 0 ); }
}
// ************************************************************************* //
EOF
done

echo "✅ All 0/ files created (no 'inlet' patch, low velocity moved to 'right')"
echo "   nozzle uses flowRateInletVelocity + CSV"
echo "   Ready for decomposePar and simulation!"
