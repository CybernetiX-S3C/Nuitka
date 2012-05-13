#     Copyright 2012, Kay Hayen, mailto:kayhayen@gmx.de
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     If you submit patches or make the software available to licensors of
#     this software in either form, you automatically them grant them a
#     license for your part of the code under "Apache License 2.0" unless you
#     choose to remove this notice.
#
#     Kay Hayen uses the right to license his code under only GPL version 3,
#     to discourage a fork of Nuitka before it is "finished". He will later
#     make a new "Nuitka" release fully under "Apache License 2.0".
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, version 3 of the License.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#     Please leave the whole of this copyright notice intact.
#
""" Node for constant expressions. Can be any builtin type.

"""

from .NodeBases import CPythonNodeBase, CPythonExpressionMixin

from nuitka.Constants import (
    getConstantIterationLength,
    isIterableConstant,
    isIndexConstant,
    isNumberConstant,
    isMutable,
)

class CPythonExpressionConstantRef( CPythonNodeBase, CPythonExpressionMixin ):
    kind = "EXPRESSION_CONSTANT_REF"

    def __init__( self, constant, source_ref ):
        CPythonNodeBase.__init__( self, source_ref = source_ref )

        self.constant = constant

    def __repr__( self ):
        return "<Node %s value %s at %s>" % ( self.kind, self.constant, self.source_ref )

    def makeCloneAt( self, source_ref ):
        return self.__class__( self.constant, source_ref )

    def getDetails( self ):
        return { "value" : repr( self.constant ) }

    def getDetail( self ):
        return repr( self.constant )

    def computeNode( self, constraint_collection ):
        # Cannot compute any further.
        return self, None, None

    def isCompileTimeConstant( self ):
        # Virtual method, pylint: disable=R0201
        return True

    def getCompileTimeConstant( self ):
        return self.constant

    getConstant = getCompileTimeConstant

    def isMutable( self ):
        return isMutable( self.constant )

    def isNumberConstant( self ):
        return isNumberConstant( self.constant )

    def isIndexConstant( self ):
        return isIndexConstant( self.constant )

    def isStringConstant( self ):
        return type( self.constant ) is str

    def isIndexable( self ):
        return self.constant is None or self.isNumberConstant()

    def isKnownToBeIterable( self, count ):
        if isIterableConstant( self.constant ):
            return count is None or getConstantIterationLength( self.constant ) == count
        else:
            return False

    def isKnownToBeIterableAtMin( self, count, constraint_collection ):
        length = self.getIterationLength( constraint_collection )

        return length is not None and length >= count

    def canPredictIterationValues( self, constraint_collection ):
        return self.isKnownToBeIterable( None )

    def getIterationValue( self, count, constraint_collection ):
        assert count < len( self.constant )

        return CPythonExpressionConstantRef( self.constant[ count ], self.source_ref )

    def isBoolConstant( self ):
        return type( self.constant ) is bool

    def mayHaveSideEffects( self, constraint_collection ):
        # Constants have no side effects
        return False

    def extractSideEffects( self ):
        # Constants have no side effects
        return ()

    def mayRaiseException( self, exception_type ):
        # Virtual method, pylint: disable=R0201,W0613

        # Constants won't raise any kind of exception.
        return False

    def mayProvideReference( self ):
        return self.isMutable()

    def getIntegerValue( self, constraint_collection ):
        if self.isNumberConstant():
            return int( self.constant )
        else:
            return None

    def getIterationLength( self, constraint_collection ):
        if isIterableConstant( self.constant ):
            return getConstantIterationLength( self.constant )
        else:
            return None

    def getStrValue( self ):
        if type( self.constant ) is str:
            return self
        else:
            return CPythonExpressionConstantRef(
                constant   = str( self.constant ),
                source_ref = self.getSourceReference()
            )
