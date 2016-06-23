#!/usr/bin/perl

# Copyright (C) 2016 Laura Rimell <laura.rimell@cl.cam.ac.uk>
# This software is licensed under the GNU General Public License, version 3.

# Calculates what percentage of top 10 properties have the correct head noun.
# Uses output from print_relpron_similarities.py

$testfile = $ARGV[0];

$depth = 10;

open(GOLDFILE, "devset");
open(TESTFILE, $testfile);

%correct_hn = ();
while(<GOLDFILE>){
    m/\S+ (\S+)_N: (\S+)_N that .*/;
    $correct_hn{$1} = $2;
}

%corr = ();   # term => num correct
%wrong = ();  # term => num wrong

$term = "";
$iter = 0;
while(<TESTFILE>){
    if(m/TERM: (\S+)/){
	$term = $1;
	$iter = 0;
    }
    if($iter == $depth){
	next;
    }
    if(m/\d [\d\.]+ [SO] (\S+)_N that .*/){
	if ($1 eq $correct_hn{$term}){
	    $corr{$term}++;
	}
	else{
	    $wrong{$term}++;
	}
	$iter++;
    }
}


%tot_by_hn = ();    # hn => running total of correct answers
%terms_by_hn = ();  # hn => number of terms
$overall_correct = 0;
$total_terms = 0;

for $t (keys %corr){
    $tot_by_hn{$correct_hn{$t}} += $corr{$t};
    $overall_correct += $corr{$t};
    $terms_by_hn{$correct_hn{$t}} += 1;
    $total_terms += 1;
}


for $hn (keys %tot_by_hn){
#    print "$hn:\n";
    for $k (keys %corr){
	if ($hn eq $correct_hn{$k}){
#	    print "$k $corr{$k}  $wrong{$k}\n";
	}
    }
#    print "\n";
}

# print "\n\n";
for $hn (keys %tot_by_hn){
    print "$hn " . $tot_by_hn{$hn} / ($depth*$terms_by_hn{$hn}) . "   terms " . $terms_by_hn{$hn} . "\n";
}

print "Overall " . $overall_correct / ($depth*$total_terms) . "    terms " . $total_terms . "\n";
