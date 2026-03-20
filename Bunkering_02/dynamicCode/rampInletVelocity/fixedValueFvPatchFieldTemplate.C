/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2019-2021 OpenCFD Ltd.
    Copyright (C) YEAR AUTHOR, AFFILIATION
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "fixedValueFvPatchFieldTemplate.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "unitConversion.H"
#include "PatchFunction1.H"

//{{{ begin codeInclude

//}}} end codeInclude


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

// dynamicCode:
// SHA1 = af596b38e24be9a0bb0635c4a2cf888153de7bd0
//
// unique function name that can be checked if the correct library version
// has been loaded
extern "C" void rampInletVelocity_af596b38e24be9a0bb0635c4a2cf888153de7bd0(bool load)
{
    if (load)
    {
        // Code that can be explicitly executed after loading
    }
    else
    {
        // Code that can be explicitly executed before unloading
    }
}

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

makeRemovablePatchTypeField
(
    fvPatchVectorField,
    rampInletVelocityFixedValueFvPatchVectorField
);

} // End namespace Foam


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::
rampInletVelocityFixedValueFvPatchVectorField::
rampInletVelocityFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(p, iF)
{
    if (false)
    {
        printMessage("Construct rampInletVelocity : patch/DimensionedField");
    }
}


Foam::
rampInletVelocityFixedValueFvPatchVectorField::
rampInletVelocityFixedValueFvPatchVectorField
(
    const rampInletVelocityFixedValueFvPatchVectorField& rhs,
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    parent_bctype(rhs, p, iF, mapper)
{
    if (false)
    {
        printMessage("Construct rampInletVelocity : patch/DimensionedField/mapper");
    }
}


Foam::
rampInletVelocityFixedValueFvPatchVectorField::
rampInletVelocityFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const dictionary& dict
)
:
    parent_bctype(p, iF, dict)
{
    if (false)
    {
        printMessage("Construct rampInletVelocity : patch/dictionary");
    }
}


Foam::
rampInletVelocityFixedValueFvPatchVectorField::
rampInletVelocityFixedValueFvPatchVectorField
(
    const rampInletVelocityFixedValueFvPatchVectorField& rhs
)
:
    parent_bctype(rhs),
    dictionaryContent(rhs)
{
    if (false)
    {
        printMessage("Copy construct rampInletVelocity");
    }
}


Foam::
rampInletVelocityFixedValueFvPatchVectorField::
rampInletVelocityFixedValueFvPatchVectorField
(
    const rampInletVelocityFixedValueFvPatchVectorField& rhs,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(rhs, iF)
{
    if (false)
    {
        printMessage("Construct rampInletVelocity : copy/DimensionedField");
    }
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::
rampInletVelocityFixedValueFvPatchVectorField::
~rampInletVelocityFixedValueFvPatchVectorField()
{
    if (false)
    {
        printMessage("Destroy rampInletVelocity");
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void
Foam::
rampInletVelocityFixedValueFvPatchVectorField::updateCoeffs()
{
    if (this->updated())
    {
        return;
    }

    if (false)
    {
        printMessage("updateCoeffs rampInletVelocity");
    }

//{{{ begin code
    #line 76 "/home/chenhu/OpenFOAM/chenhu-v2406/run/Bunkering/Bunkering_02/0/U/boundaryField/nozzle"
const fvPatch& patch = this->patch();
            const scalar t = this->db().time().value();

            // User parameters:
            const scalar Umax = 20; //1630;         // final velocity
            const scalar t_ramp = 0.01;       // ramp time (seconds)

            scalar scale = min(1.0, t / t_ramp);

            forAll(patch, faceI)
            {
                // direction assumed x-axis, adjust to your nozzle direction
                operator[](faceI) = vector(Umax * scale, 0, 0);
            }
//}}} end code

    this->parent_bctype::updateCoeffs();
}


// ************************************************************************* //

