#!/bin/bash

## Variables ##
tourney="tourney66"
N=6
S=6
TL=180
G=16
count=$G

pushd $tourney
while [ $count -gt 0 ]; do
	for i in $(seq 1 $count); do
		mkdir -p knock_R${count}/match$i/zips
	done
	if [ $count -eq $G ]; then
		for i in $(seq 1 $count); do
			echo $i
			pushd group$i
			top2=$(sort -k2 -n -r log/leaderboard.txt | head -n2)
			echo $top2
			first=$(echo $top2 | cut -d' ' -f1)
			second=$(echo $top2 | cut -d' ' -f3)
			echo $first
			echo $second
			cp zips/${first}.zip ../knock_R${count}/match$i/zips
			if [ $(( $i % 2 )) -eq 0 ]; then
				cp zips/${second}.zip ../knock_R${count}/match$(( $i - 1 ))/zips
			else
				cp zips/${second}.zip ../knock_R${count}/match$(( $i + 1 ))/zips
			fi
			ls ../knock_R${count}/match$i/zips
			popd
		done
	else
		for i in $(seq 1 $(( $count * 2 ))); do
			echo $i
			pushd knock_R$(( $count * 2 ))/match$i
			first=$(sort -k2 -n -r log/leaderboard.txt | head -n1 | cut -d' ' -f1)
			echo $first
			cp zips/${first}.zip ../../knock_R${count}/match$(( $(( $i + 1 )) / 2 ))/zips
			popd
		done
	fi
	for i in $(seq 1 $count); do
		pushd knock_R${count}/match$i
		pushd zips
		arr=(*)
		popd
		echo $arr
		echo ${#arr[@]}
		declare -A scores
	    player1zip="${arr[0]}"
	    player2zip="${arr[1]}"
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

	    # Compile the user code
	    if [ -d "$player1" ]; then
		    cp -R ../../../../../Yinsh/* $player1
		else
			echo "Bot Folder for ${player1} not found. skipping..." 
			continue
		fi

		if [ -d "$player2" ]; then
		    cp -R ../../../../../Yinsh/* $player2
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
		popd
		for K in "${!scores[@]}"; do echo $K ${scores[$K]} | tee -a log/leaderboard.txt ; done
		unset scores
		popd
	done
	count=$(( $count / 2 ))
done
popd
