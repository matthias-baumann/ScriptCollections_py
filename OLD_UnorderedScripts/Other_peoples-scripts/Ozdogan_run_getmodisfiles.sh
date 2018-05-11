#!/bin/sh

for year in 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011
do
echo $year
./MBDTcl_MOD13Q1.sh MOD13Q1 $year tile.h20v03.txt
done

