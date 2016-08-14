# doellipse -- IRAF task to do ellipse fits to an image by wrapping the
# stsdas.analysis.isophote.ellipse task, with several standard options set.
# The output table file is automatically converted to text-file format
# (using tables.tdump) and also to FITS table format (using tables.tcopy).
#
#   The default is to do logarithmic semi-major axis spacing, with a default inner 
# sma = 3 pixels and a default logarithmic spacing of delta=0.03 in sma.  
# If linear_sma=yes, then delta = spacing in pixels.
#
#    Since this is a wrapper around ellipse, most of the documentation for
# ellipse is applicable. In particular, the standard ellipse behavior of
# automatically using a pixel-list (PL) image as a mask *if* it and the
# data image have the same name and extensions of ".pl" and ".fit" (*not* ".fits")
# applies.

# Copyright (c) 2016, Peter Erwin
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

procedure doellipse( image, table, xc, yc, a_0, pa_0, ell_0, max )

string  image  {prompt = 'input image name '}
string  table  {prompt = 'output table name '}
real  xc  {prompt = 'initial isophote center X'}
real  yc  {prompt = 'initial isophote center Y'}
real  a_0  {prompt = 'initial semi-major axis'}
real  pa_0  {prompt = 'initial position angle'}
real  ell_0  {prompt = 'initial ellipticity'}
real  max  {prompt = 'maximum semi-major axis'}
real  a_min = 3.0      {prompt = 'minimum semi-major axis '}
real  delta = 0.03     {prompt = 'spacing in semi-major axis '}
bool  linear_sma = no  {prompt = 'do linear spacing in semi-major axis? '}
bool  fix_center = no  {prompt = 'hold center fixed to initial (x0,y0)? '}
bool  fix_pa = no  {prompt = 'hold PA fixed to initial value? '}
bool  fix_ell = no  {prompt = 'hold ellipticity fixed to initial value? '}
bool  extra_harmonics = yes  {prompt = 'compute and save m=5--8 harmonics? '}
string  inputellipse = "" {prompt = 'table with input ellipses for no-fit mode '}


begin

  string table_tab, table_fits, tdump_txt
  string  script_string

  table_tab = table // ".tab"
  table_fits = table // ".fits"
  tdump_txt = table // "_tdump.txt"
  # Remove old table, if it exists
  delete(files=table_tab, verify=no)
  delete(files=table_fits, verify=no)
  delete(files=tdump_txt, verify=no)

  # Define starting ellipse:
  geompar.x0 = xc
  geompar.y0 = yc
  geompar.ellip0 = ell_0
  geompar.pa0 = pa_0
  geompar.sma0 = a_0

  # Define iteration parameters
  geompar.minsma = a_min
  geompar.maxsma = max
  geompar.step = delta
  geompar.linear = linear_sma

  # Specify free ellipses:
  geompar.recenter = yes
  geompar.xylearn = yes
  controlpar.hcenter = fix_center
  controlpar.hellip = fix_ell
  controlpar.hpa = fix_pa
  
  # optional higher-order harmonics
  if (extra_harmonics == yes) {
    samplepar.harmonics = "5 6 7 8"
  } else {
    samplepar.harmonics = "none"
  }

  # Do the fits:
  if (inputellipse != "") {
    ellipse( input=image, output=table_tab, inellip=inputellipse )
  } 
  else {
    ellipse( input=image, output=table_tab )
  }

  # Make FITS and text-file versions:
  tcopy( intable=table_tab, outtable=table_fits )
  tdump( table=table_tab, >tdump_txt )
  print("FITS-table output saved to file ", table_fits)
  print("Full text output saved to file ", tdump_txt)

end
