#!/bin/bash

## Variables ##
tourney="tourney66"
N=6 # Board Size
S=6 # Sequence Length
TL=180 # Time Limit
G=16 # No. of groups

num=$(find Submissions/* -maxdepth 0 -type d | wc -l)
echo $num submissions found

mkdir -p $tourney
pushd $tourney
for i in $(seq 1 $G); do
	echo $i
	mkdir -p group$i/zips
done
popd

for filename in Submissions/*; do
	for zip in "$filename"/*; do
	    file="$(cut -d'/' -f3 <<<"$zip")"
	    botname="$(cut -d'.' -f1 <<<"$file")"
	    echo $botname
	    group=`grep -i -w $botname seeds.txt | cut -d' ' -f2`
	    echo $group
	    cp $zip $tourney/group$group/zips
	done
done

pushd $tourney
for i in $(seq 1 $G); do
	echo $i
	pushd group$i
	pushd zips
	arr=(*)
	popd
	echo $arr
	echo ${#arr[@]}
	declare -A scores
	for ((i=0; i<${#arr[@]}; i++)); do
	    for ((j=i+1; j<${#arr[@]}; j++)); do
		    echo $i, $j, ${#arr[@]}
		    player1zip="${arr[$i]}"
		    player2zip="${arr[$j]}"
		    player1="$(cut -d'.' -f1 <<<"$player1zip")"
		    player2="$(cut -d'.' -f1 <<<"$player2zip")"
		    echo "game"
		    echo $player1
		    echo $player2
		    if [ ! ${scores[$player1]+_} ]; then
		    	scores[$player1]=0.0 
		    fi
		    if [ ! ${scores[$player2]+_} ]; then
		    	scores[$player2]=0.0 
		    fi
			if [ -d log/${player1}_${player2} ]; then
				rm -rf log/${player1}_${player2}
			fi
			mkdir -p log/${player1}_${player2}
			cp zips/${player1zip} log/${player1}_${player2}
			cp zips/${player2zip} log/${player1}_${player2}
			pushd log/${player1}_${player2}
			unzip "$player1zip" > /dev/null 2>&1
			rm $player1zip
			unzip "$player2zip" > /dev/null 2>&1
			rm $player2zip
		    pwd
		    # Compile the user code
		    if [ -d "$player1" ]; then
			    cp -R ../../../../Yinsh/* $player1
			else
				echo "Bot Folder for ${player1} not found. skipping..." 
				continue
			fi

			if [ -d "$player2" ]; then
			    cp -R ../../../../Yinsh/* $player2
			else
				echo "Bot Folder for ${player2} not found. skipping..." 
				continue
			fi
 
			mkdir -p logs
			cd $player1
			bash compile.sh >> ../logs/compile_player1.log 2>&1
			cd ..
			cat logs/compile_player1.log
			cd $player2
			bash compile.sh >> ../logs/compile_player2.log 2>&1
			cd ..
			cat logs/compile_player2.log

			###########################
			#		  Game 1		  #
			###########################

			# Run the code
			mkdir -p logs/game1
			echo "#Game1" >> logs/result.txt
			echo "*** Game 1 ***"
			pushd $player1 > /dev/null 2>&1
			python2 server.py 10010 -n $N -s $S -NC 2 -TL $TL -LOG ../logs/game1/game.log &
			server_pid=$!
			sleep 1
			python2 client.py 0.0.0.0 10010 run.sh > ../logs/game1/${player1}.log 2>&1 &
			client1_pid=$!
			sleep 2
			popd > /dev/null 2>&1
			pushd $player2 > /dev/null 2>&1
			python2 client.py 0.0.0.0 10010 run.sh > ../logs/game1/${player2}.log 2>&1 &
			client2_pid=$!
			sleep 2
			popd > /dev/null 2>&1

			# Wait for completion
			wait $client1_pid
			wait $client2_pid
			wait $server_pid

			killall chrome

			# Put Player 1 score in output
			score1=`grep -o "Player 1 SCORE : [0-9.]*" logs/game1/game.log | awk -F" " '{print $5}'`
			echo "${score1}" >> logs/result.txt
			echo $score1
			# Put Player 2 score in output
			score2=`grep -o "Player 2 SCORE : [0-9.]*" logs/game1/game.log | awk -F" " '{print $5}'`
			echo "${score2}" >> logs/result.txt
			echo $score2
			curr_score=${scores[$player1]}
			scores[$player1]=$(echo "$curr_score + $score1" | bc)
			curr_score=${scores[$player2]}
			scores[$player2]=$(echo "$curr_score + $score2" | bc)
			for K in "${!scores[@]}"; do echo $K ${scores[$K]}; done

			###########################
			#		  Game 2		  #
			###########################

			# Run the code
			mkdir -p logs/game2
			echo "#Game2" >> logs/result.txt
			echo "*** Game 2 ***"
			pushd $player2 > /dev/null 2>&1
			python2 server.py 10010 -n $N -s $S -NC 2 -TL $TL -LOG ../logs/game2/game.log &
			server_pid=$!
			sleep 1
			python2 client.py 0.0.0.0 10010 run.sh > ../logs/game2/${player2}.log 2>&1 &
			client1_pid=$!
			sleep 2
			popd > /dev/null 2>&1
			pushd $player1 > /dev/null 2>&1
			python2 client.py 0.0.0.0 10010 run.sh > ../logs/game2/${player1}.log 2>&1 &
			client2_pid=$!
			sleep 2
			popd > /dev/null 2>&1

			# Wait for completion
			wait $client1_pid
			wait $client2_pid
			wait $server_pid

			killall chrome

			# Put Player 1 score in output
			score1=`grep -o "Player 1 SCORE : [0-9.]*" logs/game2/game.log | awk -F" " '{print $5}'`
			echo "${score1}" >> logs/result.txt
			echo $score1
			# Put Player 2 score in output
			score2=`grep -o "Player 2 SCORE : [0-9.]*" logs/game2/game.log | awk -F" " '{print $5}'`
			echo "${score2}" >> logs/result.txt
			echo $score2
			curr_score=${scores[$player1]}
			scores[$player1]=$(echo "$curr_score + $score2" | bc)
			curr_score=${scores[$player2]}
			scores[$player2]=$(echo "$curr_score + $score1" | bc)
			for K in "${!scores[@]}"; do echo $K ${scores[$K]}; done
			pkill -P $$

			popd
		done
	done
	for K in "${!scores[@]}"; do echo $K ${scores[$K]} | tee -a log/leaderboard.txt ; done
	unset scores
	popd
done
popd


