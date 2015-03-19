#!/usr/bin/python
# coding: utf

import readline
import sys
import traceback
import tpg
import itertools

def make_op(s):
    return {
        '+': lambda x,y: x+y,
        '-': lambda x,y: x-y,
        '*': lambda x,y: x*y,
        '/': lambda x,y: x/y,
        '&': lambda x,y: x&y,
        '|': lambda x,y: x|y,
        '^': lambda x,y: x**y
    }[s]

class Vector(list):
    def __init__(self, *argp, **argn):
        list.__init__(self, *argp, **argn)

    def __str__(self):
        return "[" + " ".join(str(c) for c in self) + "]"

    def __op(self, a, op):
        try:
            return self.__class__(op(s,e) for s,e in zip(self, a))
        except TypeError:
            return self.__class__(op(c,a) for c in self)

    def __add__(self, a): return self.__op(a, lambda c,d: c+d)
    def __sub__(self, a): return self.__op(a, lambda c,d: c-d)
    def __div__(self, a): return self.__op(a, lambda c,d: c/d)
    def __mul__(self, a): return self.__op(a, lambda c,d: c*d)

    def __and__(self, a):
        try:
            return reduce(lambda s, (c,d): s+c*d, zip(self, a), 0)
        except TypeError:
            return self.__class__(c and a for c in self)

    def __or__(self, a):
        try:
            return self.__class__(itertools.chain(self, a))
        except TypeError:
            return self.__class__(c or a for c in self)

class Matrix(Vector):
    def __init__(self, *argp, **argn):
        Vector.__init__(self, *argp, **argn)

    def __str__(self):
        maxlen = 0
        for row in self:
            for column in row:
                curlen = len(str(column))
                if curlen > maxlen:
                    maxlen = curlen
        result = ''
        for row in self:
            result += '['
            for column in row:
                result += str(column).rjust(maxlen + 1)
            result += ' ]\n'
        return result[:len(result) - 1]

    def __mul__(self, a):
        try:
            result = Matrix()
            for i in range(len(self)):
                result.append([])
                for j in range(len(a[0])):
                    result[i].append(0)
                    for k in range(len(a)):
                        result[i][j] += self[i][k] * a[k][j]
            return result
        except:
            pass
        try:
            result = Vector()
            for i in range(len(self)):
                result.append(0)
                for j in range(len(a)):
                    result[i] += self[i][j] * a[j]
            return result
        except:
            pass
        return Vector.__mul__(self, a)
            

class Calc(tpg.Parser):
    r"""

    separator spaces: '\s+' ;
    separator comment: '#.*' ;

    token fnumber: '\d+[.]1\d*' float ;
    token number: '\d+' int ;
    token op1: '[|&+-]' make_op ;
    token op2: '[*/]' make_op ;
    token op3: '[\^]' make_op ;
    token id: '\w+' ;

    START/e -> Operator $e=None$ | Expr/e | $e=None$ ;
    Operator -> Assign ;
    Assign -> id/i '=' Expr/e $Vars[i]=e$ ;
    Expr/t -> Fact/t ( op1/op Fact/f $t=op(t,f)$ )* ;
    Fact/f -> Pow/f ( op2/op Pow/p $f=op(f,p)$ )* ;
    Pow/p -> Atom/p ( op3/op Atom/a $p=op(p,a)$ )* ;
    Atom/a ->   Matrix/a
              | Vector/a
              | id/i ( check $i in Vars$ | error $"Undefined variable '{}'".format(i)$ ) $a=Vars[i]$
              | fnumber/a
              | number/a
              | '\(' Expr/a '\)' ;
    Matrix/$Matrix(a)$ -> '\[' Vectors/a '\]' ; 
    Vectors/v -> Vector/a Vectors/t $v=[a]+t$ | Vector/a $v=[a]$ ;
    Vector/$Vector(a)$ -> '\[' '\]' $a=[]$ | '\[' Atoms/a '\]' ;
    Atoms/v -> Atom/a Atoms/t $v=[a]+t$ | Atom/a $v=[a]$ ;

    """

calc = Calc()
Vars={}
PS1='-->'

Stop=False
command_buffer = []

while not Stop:
    if len(command_buffer):
        line = command_buffer.pop()
        if len(line):
            print PS1, line
        else:
            continue
    else:
        try:
            line = raw_input(PS1 + " ")
        except KeyboardInterrupt:
            print '\nKeyboardInterrupt'
            line = ''
        except EOFError:
            print '\nExiting'
            line = 'exit'
        except:
            traceback.print_exc(1)
            line = ''
            print ''
            pass
    if line == 'exit':
        Stop = True
        continue
    if line[:7] == 'source ':
        try:
            f = open(line[7:])
            command_buffer = list(reversed(f.read().split('\n')))
        except:
            traceback.print_exc(1) 
            pass
        continue
    try:
        res = calc(line)
    except tpg.Error as exc:
        print >> sys.stderr, exc
        res = None
    except:
        traceback.print_exc(1)
        res = None
    if res != None:
        print res
