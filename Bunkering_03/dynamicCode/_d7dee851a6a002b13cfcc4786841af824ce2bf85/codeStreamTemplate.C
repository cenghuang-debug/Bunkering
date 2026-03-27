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

extern "C" void codeStream_d7dee851a6a002b13cfcc4786841af824ce2bf85(Foam::Ostream& os, const Foam::dictionary& dict)
{
//{{{ begin code
    #line 75 "/home/chenhu/OpenFOAM/chenhu-v2406/run/Bunkering/Bunkering_03/system/snappyHexMeshDict/geometry/#codeStream"
// Access top-level config correctly
            const dictionary& cfg = dict.parent().subDict("refinementBoxesCfg");

            const label  n     = readLabel(cfg.lookup("nLevels"));
            const scalar s     = readScalar(cfg.lookup("scalingFactor"));
            const scalar dx1   = readScalar(cfg.lookup("dx_level_1"));
            const scalar dy1   = readScalar(cfg.lookup("dy_level_1"));
            const scalar dz1   = readScalar(cfg.lookup("dz_level_1"));
            const scalar zBase = readScalar(cfg.lookup("zBase"));
            const word pre     = cfg.lookupOrDefault<word>("namePrefix","refinementBox_");
            const word suf     = cfg.lookupOrDefault<word>("nameSuffix","xsmall");

            for (label i = 1; i <= n; ++i)
            {
                const scalar powSi = pow(s, scalar(i-1));
                const scalar dx    = dx1 / powSi;
                const scalar dy    = dy1 / powSi;
                const scalar dz    = dz1 / powSi;

                const scalar xmin = -dx, ymin = -dy, zmin = zBase;
                const scalar xmax =  dx, ymax =  dy, zmax = zBase + dz;

                os  << "    " << pre << i << suf << "\n"
                    << "    {\n"
                    << "        type box;\n"
                    << "        min (" << xmin << " " << ymin << " " << zmin << ");\n"
                    << "        max (" << xmax << " " << ymax << " " << zmax << ");\n"
                    << "    }\n";
            }
//}}} end code
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //

