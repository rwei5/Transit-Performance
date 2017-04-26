# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
# 
# @file                 DEA.py
# Description           Data Envelopment Analysis Core
# Author                Yongjian Mu
# Date                  9/13/2015
# Reference             https://github.com/metjush/envelopment-py
# ##################################################################################


import numpy as np
from scipy.optimize import fmin_slsqp


# ##################################################################################
# @brief                Data envelopment analysis core
#
# @class                DEA
# ##################################################################################
class DEA(object):

# ##################################################################################
# @brief                Constructor, init DEA class variables
# @param input          The coefficients of the formular, n x m array
# @param output         The value of the formular, n x r array
#
# @return               self               
# ##################################################################################
    def __init__(self, inputs, outputs):

        self.inputs = inputs
        self.outputs = outputs

        # n = number of entities (observations)
        # m = number of inputs (variables, features)
        # r = number of outputs
        self.n = inputs.shape[0]
        self.m = inputs.shape[1]
        self.r = outputs.shape[1]

        # iterators
        self.unit_ = range(self.n)
        self.input_ = range(self.m)
        self.output_ = range(self.r)

        # result arrays
        self.output_w = np.zeros((self.r, 1), dtype=np.float)  # output weights
        self.input_w = np.zeros((self.m, 1), dtype=np.float)  # input weights
        self.lambdas = np.zeros((self.n, 1), dtype=np.float)  # unit efficiencies
        self.efficiency = np.zeros_like(self.lambdas)  # thetas

# ##################################################################################
# @brief                The efficiency function with already computed weights
# @param unit           The number of entities
#
# @return               Efficiency
# ##################################################################################
    def __efficiency(self, unit):

        # compute efficiency
        denominator = np.dot(self.inputs, self.input_w)
        numerator = np.dot(self.outputs, self.output_w)

        return (numerator/denominator)[unit]

# ##################################################################################
# @brief                Calculate theta
# @param unit           The number of entities
# @param x              Combined weights
#
# @return               Theta
# ##################################################################################
    def __target(self, x, unit):

        in_w, out_w, lambdas = x[:self.m], x[self.m:(self.m+self.r)], x[(self.m+self.r):]  # unroll the weights
        denominator = np.dot(self.inputs[unit], in_w)
        numerator = np.dot(self.outputs[unit], out_w)

        return numerator/denominator

# ##################################################################################
# @brief                Constraints for optimization for one unit
# @param unit           The number of entities
# @param x              Combined weights
#
# @return               Array of constraints
# ##################################################################################
    def __constraints(self, x, unit):
        
        in_w, out_w, lambdas = x[:self.m], x[self.m:(self.m+self.r)], x[(self.m+self.r):]  # unroll the weights
        constr = []  # init the constraint array

        # for each input, lambdas with inputs
        for input in self.input_:
            t = self.__target(x, unit)
            lhs = np.dot(self.inputs[:, input], lambdas)
            cons = t*self.inputs[unit, input] - lhs
            constr.append(cons)

        # for each output, lambdas with outputs
        for output in self.output_:
            lhs = np.dot(self.outputs[:, output], lambdas)
            cons = lhs - self.outputs[unit, output]
            constr.append(cons)

        # for each unit
        for u in self.unit_:
            constr.append(lambdas[u])

        return np.array(constr)

# ##################################################################################
# @brief                Optimization of DEA model
#                       Use: http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.optimize.linprog.html
#                       A = coefficients in the constraints
#                       b = rhs of constraints
#                       c = coefficients of the target function
#
# @return               
# ##################################################################################
    def __optimize(self):
        
        d0 = self.m + self.r + self.n
        # iterate over units
        for unit in self.unit_:
            # weights
            x0 = np.random.rand(d0) - 0.5
            x0 = fmin_slsqp(self.__target, x0, f_ieqcons=self.__constraints, args=(unit,))
            # unroll weights
            self.input_w, self.output_w, self.lambdas = x0[:self.m], x0[self.m:(self.m+self.r)], x0[(self.m+self.r):]
            self.efficiency[unit] = self.__efficiency(unit)

# ##################################################################################
# @brief                Get names
# @param name           The name list
#
# @return               
# ##################################################################################
    def name_units(self, names):

        assert(self.n == len(names))

        self.names = names

# ##################################################################################
# @brief                Optimize dataset, generate the table
#
# @return               Generated table       
# ##################################################################################
    def fit(self):
        dict = {}
        self.__optimize()  # optimize

        print "Final thetas for each unit:\n"
        print "---------------------------\n"
        for n, eff in enumerate(self.efficiency):
            if len(self.names) > 0:
                name = "%s" % self.names[n]
            else:
                name = "%d" % (n+1)
            print "%s, %.4f" % (name, eff)
            print "\n"
            dict[str(name)] = float("%.4f" % eff[0])
        print "---------------------------\n"
        print dict
        return dict

# ##################################################################################
# @brief                Check data validation and return results
#
# @return               Generated table       
# ##################################################################################
    def getResult(self):
        loop_flag = True
        dict = {}
        while loop_flag:
            loop_flag = False
            dict = self.fit()
            for k, v in dict.items():
                if v < 0.0 or v > 1.0:
                    loop_flag = True
                    print "recalculate DEA!"
                    break;
        return dict