/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
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

Description
    Template for use with codeStream.

\*---------------------------------------------------------------------------*/

#include "dictionary.H"
#include "Ostream.H"
#include "Pstream.H"
#include "pointField.H"
#include "tensor.H"
#include "unitConversion.H"

//{{{ begin codeInclude

//}}} end codeInclude

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

extern "C" void codeStream_f67e2fd5cb1766e4ac0d6ce8844f56377f01c3ad(Foam::Ostream& os, const Foam::dictionary& dict)
{
//{{{ begin code
    #line 216 "/home/chenhu/OpenFOAM/chenhu-v2406/run/Bunkering/Bunkering_02/system/snappyHexMeshDict/castellatedMeshControls/refinementRegions/#codeStream"
// refinementRegions -> castellatedMeshControls -> TOP
                const dictionary& cfg = dict.parent().parent().subDict("refinementBoxesCfg");

                const label n  = readLabel(cfg.lookup("nLevels"));
                const word pre = cfg.lookupOrDefault<word>("namePrefix","refinementBox_");
                const word suf = cfg.lookupOrDefault<word>("nameSuffix","xsmall");

                for (label i = 1; i <= n; ++i)
                {
                    os  << "    " << pre << i << suf << "\n"
                        << "    {\n"
                        << "        mode inside;\n"
                        << "        levels ((" << i << " " << i << "));\n"
                        << "    }\n";
                }
//}}} end code
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //

