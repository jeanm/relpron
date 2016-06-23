#!/usr/bin/perl

# Copyright (C) 2016 Laura Rimell <laura.rimell@cl.cam.ac.uk>
# This software is licensed under the GNU General Public License, version 3.

# Calculates MAP within head nouns. Only the properties with the correct head noun are
# ranked for each term.
# Uses output of relpron_eval.py.

$testfile = $ARGV[0];

open(GOLDFILE, "devset");
open(TESTFILE, $testfile);

%correct_hn = ();
while(<GOLDFILE>){
    m/\S+ (\S+)_N: (\S+)_N that .*/;
    $correct_hn{$1} = $2;
}


%aps_by_hn = ();   # hn => running total of APs for each term in that head noun
%terms_by_hn = ();  # hn => number of terms
$tot = 0;  # running total of number of terms (sanity check on overall MAP)
$vals = 0; # running total of APS (sanity check on overall MAP)
$in_target_list = 0;
while(<TESTFILE>){
    if(m/^AP over queries = terms$/){
	$in_target_list = 1;
	next;
    }
    if($in_target_list == 0){
	next;
    }
    if(m/^$/){
	last;
    }
    m/(\S+) ([\d\.]+)/;
    $aps_by_hn{$correct_hn{$1}} += $2;
    $terms_by_hn{$correct_hn{$1}} += 1;
    $vals += $2;
    $tot += 1;
#     print "Incrementing $1 $correct_hn{$1} $2\n";
}


#print "\n\n";
for $hn (keys %terms_by_hn){
    print "$hn " . $aps_by_hn{$hn} / $terms_by_hn{$hn} . "   terms " . $terms_by_hn{$hn} . "\n";
}

print "Overall " . $vals / $tot . "    terms " . $tot . "\n";
