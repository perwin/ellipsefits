#!/usr/bin/env python3

"""Unit test for ellipsefits.py"""

import unittest
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as Interp


import ellipsefits_copy as ellipsefits   # module to be tested


# prepare input and reference data

efitFileDir = '/Beleriand/data/sdss/n5831/'
efitFile_tdump = efitFileDir + "el_n5831rss_tdump.txt"
efitFile_fits = efitFileDir + "el_n5831rss.fits"

# Values for ellipse fits to NGC 5831 SDSS r-band image (sky-sub.), 
# taken from the FITS-table version
n5831_startSma = np.array([1.0178389549255371, 1.0483740568161011, 1.0798252820968628,
        1.1122200489044189, 1.1455866098403931])
n5831_endSma = np.array([190.48722839355469, 196.20184326171875, 202.087890625,
        208.15052795410156, 214.39503479003906])
n5831_startPA_correct = np.array([100.83729553, 100.63247681,  100.54562378,  
        100.44206238, 100.08587646])
n5831_intens = np.array([9595.8203125, 9565.73046875, 9534.61621094, 9503.18066406,
        9469.71386719])
n5831_flux = 100 * n5831_intens
# Assumed zero point = 26.2829
n5831_sb = np.array([16.327694, 16.331104, 16.334642, 16.338226, 16.342056])
# ellipticity, axis ratio, r_eq
n5831_startEll = np.array([0.2120698, 0.21750439999999999, 0.22277189999999999, 
                    0.2284563, 0.2334621])
n5831_startq = np.array([0.7879302, 0.7824956, 0.7772280999999, 0.7715437, 0.76653789999999])
n5831_startReq = np.array([0.90348919010738549, 0.92737886451308393, 0.95197956250163829, 
                    0.97694691320309268, 1.0029860506078907])

# interpolated intensity values
# intensity_spline = InterpolatedUnivariateSpline(self.n5831efit_fits['sma'],  
#                     self.n5831efit_fits['intens'])
# correct = intensity_spline(r)
# Values for a = 85, 86, 87, 88, 89
n5831_interp = np.array([ 56.09949942,  54.91316007,  54.12624965,  53.47276029,  52.66247574])




class EllipseCircumCheck( unittest.TestCase ):
    def testEllipseCircum( self ):
        # circular case
        correct = 2*np.pi
        self.assertEqual(ellipsefits.EllipseCircum(1.0, 1.0), correct)
        # elliptical case
        a = 1.0
        b = 0.5
        self.assertEqual(4.8442241102738377, ellipsefits.EllipseCircum(a, b))

    def testEllipseCircum_array( self ):
        aa = np.array([1.0, 1.0, 1.0])
        bb = np.array([1.0, 0.5, 0.1])
        correct = [2*np.pi, 4.8442241102738377, 4.0639741801008959]
        result = ellipsefits.EllipseCircum(aa, bb)
        for i in range(3):
            self.assertEqual(correct[i], result[i])


class EllipseRCheck( unittest.TestCase ):
    def testEllipseR( self ):
        # circular case
        input = np.array([0.0, 45.0, 90.0, 135.0, 180.0])
        correct = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        result = ellipsefits.EllipseR(1.0, 0.0, 0.0, input)
        for i in range(5):
            self.assertEqual(correct[i], result[i])
        # ell = 0.5
        correct = np.array([1.0, 0.6324555320336759, 0.5, 0.6324555320336759, 1.0])
        result = ellipsefits.EllipseR(1.0, 0.5, 0.0, input)
        for i in range(5):
            self.assertEqual(correct[i], result[i])
        # ell = 0.5, pa = 45
        correct = np.array([0.6324555320336759, 1.0, 0.6324555320336759, 0.5, 0.6324555320336759])
        result = ellipsefits.EllipseR(1.0, 0.5, 45.0, input)
        for i in range(5):
            self.assertEqual(correct[i], result[i])
        # ell = 0.5, pa = 135
        correct = np.array([0.6324555320336759, 0.5, 0.6324555320336759, 1.0, 0.6324555320336759])
        result = ellipsefits.EllipseR(1.0, 0.5, 135.0, input)
        for i in range(5):
            self.assertEqual(correct[i], result[i])


# def CorrectPosAngle( posAngle, telescopePA=None, flipFlag=False, outputNP=False ):
class CorrectPACheck( unittest.TestCase ):
    def testCorrectPA_basic( self ):
        # single values check, telPA = 0
        input = [-90.0, -45.0, -10.0, 0.0, 10.0, 45.0, 90.0]
        correct = [90.0, 135.0, 170.0, 0.0, 10.0, 45.0, 90.0]
        for i in range(len(input)):
            self.assertEqual(correct[i], ellipsefits.CorrectPosAngle(input[i]))

    def testCorrectPA_basic_array( self ):
        # multiple values in numpy array, telPA = 0
        input = np.array([-90.0, -45.0, -10.0, 0.0, 10.0, 45.0, 90.0])
        correct =        [90.0,  135.0, 170.0, 0.0, 10.0, 45.0, 90.0]
        output = ellipsefits.CorrectPosAngle(input)
        for i in range(len(input)):
            self.assertEqual(correct[i], output[i])
        # same, using a list as input
        output = ellipsefits.CorrectPosAngle(list(input))
        for i in range(len(input)):
            self.assertEqual(correct[i], output[i])
        
    def testCorrectPA_telPA( self ):
        # correct multiple values with telescope PA = 10 specified
        input = np.array([-90.0, -45.0, -10.0, 0.0, 10.0, 45.0, 90.0])
        correct =        [100.0, 145.0,  0.0, 10.0, 20.0, 55.0, 100.0]
        output = ellipsefits.CorrectPosAngle(input, telescopePA=10)
        for i in range(len(input)):
            self.assertEqual(correct[i], output[i])
        # correct multiple values with telescope PA = 270 specified
        input = np.array([-90.0, -45.0, -10.0, 0.0,  10.0,  45.0, 90.0])
        correct =        [0.0,    45.0,  80.0, 90.0, 100.0, 135.0, 0.0]
        output = ellipsefits.CorrectPosAngle(input, telescopePA=270)
        for i in range(len(input)):
            self.assertEqual(correct[i], output[i])
    
    def testCorrectPA_flip( self ):
        # correct for left-right image reflection (reflection about y axis)
        input = np.array([-90.0, -45.0, -10.0, 0.0,  10.0,  45.0, 90.0])
        correct =        [90.0,   45.0,  10.0, 0.0, 170.0, 135.0, 90.0]
        output = ellipsefits.CorrectPosAngle(input, flipFlag=True)
        for i in range(len(input)):
            self.assertEqual(correct[i], output[i])


class ReadEllipseCheck( unittest.TestCase ):
    def setUp(self):
        self.n5831efit_tdump = ellipsefits.ReadEllipse(efitFile_tdump)
        self.n5831efit_fits = ellipsefits.ReadEllipse(efitFile_fits)
        self.n5831efit_fits_arcsec = ellipsefits.ReadEllipse(efitFile_fits,pix=0.396)
        self.n5831efit_fits_correctpa = ellipsefits.ReadEllipse(efitFile_fits,telPA=89.99)
        self.n5831efit_fits_sb = ellipsefits.ReadEllipse(efitFile_fits, zp=26.2829,
                    fluxconv=100.0, fluxUnits='blah')

    def testReadEllipse_SMA( self ):
        # check tdump and FITS versions
        # tdump output differs from FITS table values at few x 10^-7 level in
        # relative terms
        for i in range(5):
            deltaRel = abs((n5831_startSma[i] - self.n5831efit_tdump['sma'][i]) / 
                        n5831_startSma[i])
            self.assertLess(deltaRel, 1e-6)
        for i in range(-5,-1):
            deltaRel = abs((n5831_endSma[i] - self.n5831efit_tdump['sma'][i]) / 
                        n5831_endSma[i])
            self.assertLess(deltaRel, 1e-6)
        for i in range(5):
            self.assertEqual(n5831_startSma[i], self.n5831efit_fits['sma'][i])
        for i in range(-5,-1):
            self.assertEqual(n5831_endSma[i], self.n5831efit_fits['sma'][i])

        # check associated metatdata
        correct = 'pixels'
        # WARNING: NON-DICT ATTRIBUTE
        self.assertEqual(correct, self.n5831efit_fits.sma_units)

    def testReadEllipse_SMA_arcsec( self ):
        # test for semi-major-axis units with user-specified pixel scale
        pixScale = 0.396
        for i in range(5):
            correctSma_arcsec = pixScale * n5831_startSma[i]
            deltaRel = abs((correctSma_arcsec - 
                        self.n5831efit_fits_arcsec['sma'][i]) / correctSma_arcsec)
            self.assertLess(deltaRel, 1e-6)
        
        # check associated metatdata
        correct = 'arc sec'
        # WARNING: NON-DICT ATTRIBUTE
        self.assertEqual(correct, self.n5831efit_fits_arcsec.sma_units)
        correct = 0.396
        # WARNING: NON-DICT ATTRIBUTE
        self.assertEqual(correct, self.n5831efit_fits_arcsec.units_per_pix)

    def testReadEllipse_PA( self ):
        # test for corrected PA values
        for i in range(5):
            deltaRel = abs((n5831_startPA_correct[i] - 
                        self.n5831efit_fits_correctpa['pa'][i]) / n5831_startPA_correct[i])
            self.assertLess(deltaRel, 1e-6)

    def testReadEllipse_SB( self ):
        """Test that we convert intensities to mag/arcsec^2, given an input
        zero point."""
        # test for valid surface-brightness values
        for i in range(5):
            deltaRel = abs((n5831_sb[i] - 
                        self.n5831efit_fits_sb['sb'][i]) / n5831_sb[i])
            self.assertLess(deltaRel, 1e-6)

        # check associated metatdata
        correct = 26.2829
        # WARNING: NON-DICT ATTRIBUTE
        self.assertEqual(correct, self.n5831efit_fits_sb.zp_sb)

    def testReadEllipse_fluxconv( self ):
        """Test that we convert intensities to arbitrary fluxes, given an input
        flux conversion factor."""
        for i in range(5):
            deltaRel = abs((n5831_flux[i] - 
                        self.n5831efit_fits_sb['flux'][i]) / n5831_flux[i])
            self.assertLess(deltaRel, 1e-6)

        # check associated metatdata
        correct = 100.0
        # WARNING: NON-DICT ATTRIBUTE
        self.assertEqual(correct, self.n5831efit_fits_sb.fluxconv)
        # check associated metatdata
        correct = "blah"
        # WARNING: NON-DICT ATTRIBUTE
        self.assertEqual(correct, self.n5831efit_fits_sb.flux_units)

    def testReadEllipse_Ell( self ):
        """Test that we correctly read in ellipticity values, and also that we
        correctly convert these to q (= b/a) and r_eq values. """
        # test for ellipticity values
        for i in range(5):
            deltaRel = abs((n5831_startEll[i] - 
                        self.n5831efit_fits['ellip'][i]) / n5831_startEll[i])
            self.assertLess(deltaRel, 1e-6)
        # test for axis-ratio values
        for i in range(5):
            deltaRel = abs((n5831_startq[i] - self.n5831efit_fits['q'][i]) / n5831_startq[i])
            self.assertLess(deltaRel, 1e-6)
        # test for r_eq values
        for i in range(5):
            deltaRel = abs((n5831_startReq[i] - self.n5831efit_fits['r_eq'][i]) / n5831_startReq[i])
            self.assertLess(deltaRel, 1e-6)


# def IntensityFromRadius( ellipseFit, radius, ZP=None ):
class IntensityFromRadiusCheck( unittest.TestCase ):
    def setUp(self):
        self.n5831efit_fits = ellipsefits.ReadEllipse(efitFile_fits)
        self.n5831efit_fits_arcsec = ellipsefits.ReadEllipse(efitFile_fits,pix=0.396)
        self.intensity_spline = Interp(self.n5831efit_fits['sma'], 
                            self.n5831efit_fits['intens'])
    
    def testSingleRadius( self ):
        r = 1.0483740568161011
        correct = 9565.73046875
        result = ellipsefits.IntensityFromRadius(self.n5831efit_fits, r)
        deltaRel = np.abs(result - correct)/correct
        self.assertLess(deltaRel, 1e-8)

    def testSingleRadius_interpolated( self ):
        r = 1.5
        correct = self.intensity_spline(r)
        result = ellipsefits.IntensityFromRadius(self.n5831efit_fits, r)
        deltaRel = np.abs(result - correct)/correct
        self.assertLess(deltaRel, 1e-8)

    def testMultiRadius_interpolated( self ):
        aa = np.array([85.0, 86.0, 87.0, 88.0, 89])
        result = ellipsefits.IntensityFromRadius(self.n5831efit_fits, aa)
        for i in range(len(aa)):
            deltaRel = np.abs(result[i] - n5831_interp[i])/n5831_interp[i]
            self.assertLess(deltaRel, 1e-8)


class EquivRadiusCheck( unittest.TestCase ):
    def setUp(self):
        self.n5831efit_fits = ellipsefits.ReadEllipse(efitFile_fits)

    def testSingleSMA( self ):
        a = self.n5831efit_fits['sma']
        q = self.n5831efit_fits['q']
        b = q*a
        r_eq_correct = np.sqrt(a*b)
        result = ellipsefits.EquivRadius(self.n5831efit_fits)
        deltaRel = np.abs(result - r_eq_correct) / r_eq_correct
        for i in range(10):
            self.assertLess(deltaRel[i], 1.0e-8)
        for i in range(-10, 0):
            self.assertLess(deltaRel[i], 1.0e-8)


#def ConvertHigherOrder_Iraf2Bender( a, ell, B_iraf, percentStyle=True ):
class BenderIRAFConversionScheck( unittest.TestCase ):
    def testIRAF2Bedner( self ):
        a = 10.0
        ell = 0.5
        B_4 = 0.05
        correct = 3.5355339059327378
        result = ellipsefits.ConvertHigherOrder_Iraf2Bender(a, ell, B_4)
        deltaRel = np.abs(result - correct) / correct
        self.assertLess(deltaRel, 1.0e-8)

    def testIRAF2Bedner_roundtrip( self ):
        a = 10.0
        ell = 0.5
        B_4 = 0.05
        a_4 = ellipsefits.ConvertHigherOrder_Iraf2Bender(a, ell, B_4)
        B_4_result = ellipsefits.ConvertHigherOrder_Bender2Iraf(a, ell, a_4)
        deltaRel = np.abs(B_4_result - B_4) / B_4
        self.assertLess(deltaRel, 1.0e-8)
        

if __name__ == "__main__":
    
    print("** Unit tests for ellipsefits.py **")
    unittest.main()   
