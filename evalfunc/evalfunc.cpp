//Weights
std::vector<std::vector<int> > row_weights = {1, 3, 9, 27, 81};
int w0=1;
int w9=1;
int w8=1;
int w7=1;
int w6=1;
int w5=1;
int w4=1;
int w3=1;
int w2=1;
int w1=1;
int a0=0.5;
int b0=0.5;
int b1=0.5;

//Calculate strength of 5 row
float Board::MarkerScore(Element marker, Element ring){
	float marker_score=0;
	int allot=0;
	int col,row;
	//N to S rows
	for (col = 1; col < current_board.size()-1; col++) {
		allot=0;
		row=0;
		while(current_board[col][row]==E){
				row++;
		}
		for (; row < current_board[0].size()
			||current_board[col][row]==E; row+=2) {

			
			if(current_board[col][row]==marker) {
				marker_score+=row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else if(current_board[col][row]==ring) {
				marker_score+=0.5*row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else{
				allot=0;
			}
		}
		
	}

	row=0;
	col=4;
	//2-5th SE diagonal lines
	for(int count=0;count<4;count++,row+=SW_Dir.first,col+=SW_Dir.second){
		allot=0;
		for(int a=row,b=col;current_board[a][b]!=I;a+=SE_Dir.first,b+=SE_Dir.second){
			if(current_board[a][b]==marker) {
				marker_score+=row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else if(current_board[a][b]==ring) {
				marker_score+=0.5*row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else{
				allot=0;
			}
		}
	}

	//Middle SE diagonal line
	row+=S_Dir.first;
	col+=S_Dir.second;
	allot=0;
	for(int a=row,b=col;current_board[a][b]!=I;a+=SE_Dir.first,b+=SE_Dir.second){
		if(current_board[a][b]==marker) {
			marker_score+=row_weights[allot];
			if(allot!=4){
				allot++;
			}
		}
		else if(current_board[a][b]==ring) {
			marker_score+=0.5*row_weights[allot];
			if(allot!=4){
				allot++;
			}
		}
		else{
			allot=0;
		}
	}

	//Next 4 points with NE and SE lines
	row+=SW_Dir.first;
	col+=SW_Dir.second;
	for(int count=0;count<4;count++,row+=S_Dir.first,col+=S_Dir.second){
		allot=0;
		for(int a=row,b=col;current_board[a][b]!=I;a+=SE_Dir.first,b+=SE_Dir.second){
			if(current_board[a][b]==marker) {
				marker_score+=row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else if(current_board[a][b]==ring) {
				marker_score+=0.5*row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else{
				allot=0;
			}
		}
		allot=0;
		for(int a=row,b=col;current_board[a][b]!=I;a+=NE_Dir.first,b+=NE_Dir.second){
			if(current_board[a][b]==marker) {
				marker_score+=row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else if(current_board[a][b]==ring) {
				marker_score+=0.5*row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else{
				allot=0;
			}
		}
	}

	//Middle NE diagonal line
	row+=SE_Dir.first;
	col+=SE_Dir.second;
	allot=0;
	for(int a=row,b=col;current_board[a][b]!=I;a+=NE_Dir.first,b+=NE_Dir.second){
		if(current_board[a][b]==marker) {
			marker_score+=row_weights[allot];
			if(allot!=4){
				allot++;
			}
		}
		else if(current_board[a][b]==ring) {
			marker_score+=0.5*row_weights[allot];
			if(allot!=4){
				allot++;
			}
		}
		else{
			allot=0;
		}
	}

	// Last 2-5th NE diagonal lines
	row+=S_Dir.first;
	col+=S_Dir.second;
	for(int count=0;count<4;count++,row+=SE_Dir.first,col+=SE_Dir.second){
		allot=0;
		for(int a=row,b=col;current_board[a][b]!=I;a+=NE_Dir.first,b+=NE_Dir.second){
			if(current_board[a][b]==marker) {
				marker_score+=row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else if(current_board[a][b]==ring) {
				marker_score+=0.5*row_weights[allot];
				if(allot!=4){
					allot++;
				}
			}
			else{
				allot=0;
			}
		}
	}
	return marker_score;
}

//Calculate security of markers
int Board::FlippedUtility(Element marker, Element ring, Dir dir, int i, int j){
	int row=i+dir.first,col=j+dir.second;
	int marker_count=0;
	while(current_board[row][col]==E){
		row+=dir.first;
		col+=dir.second;
	}
	while(current_board[row][col]!=I){
		if(current_board[row][col]==marker){
			marker_count++;
		}
		else if(current_board[row][col]==E){
			return marker_count;
		}
		else if(current_board[row][col]==B_RING
			||current_board[row][col]==W_RING){
			return 0;
		}
		row+=dir.first;
		col+=dir.second;
	}
	return 0;
}

//Calculate security of markers
float Board::FlippedScore(Element marker, Element ring){
	float flipped_score=0;
	for (int i = 0; i < current_board.size(); i++) {
		for (int j = 0; j < current_board.size(); j++){
			if(current_board[i][j]==ring){
				flipped_score+=board.FlippedUtility(marker,ring,N_Dir,i,j);
				flipped_score+=board.FlippedUtility(marker,ring,NE_Dir,i,j);
				flipped_score+=board.FlippedUtility(marker,ring,SE_Dir,i,j);
				flipped_score+=board.FlippedUtility(marker,ring,S_Dir,i,j);
				flipped_score+=board.FlippedUtility(marker,ring,SW_Dir,i,j);
				flipped_score+=board.FlippedUtility(marker,ring,NW_Dir,i,j);
			}
		}
	}
}

//Count no of markers
float Board::CountMarkers(Element e){
	float marker_count = 0;
	for (int i = 0; i < current_board.size(); i++) {
		for (int j = 0; j < current_board[0].size(); j++) {
			
			if(current_board[i][j]==e) {
				marker_count++;
			}
		}
		
	}
	return marker_count;
}

//Calculate mobility of rings
int Board::MobilityUtility(Element ring, Dir dir, int i, int j){
	int row=i+dir.first,col=j+dir.second;
	int space_count=0;
	while(current_board[row][col]==E){
		space_count++;
		row+=dir.first;
		col+=dir.second;
	}
	while(current_board[row][col]!=I){
		if(current_board[row][col]==E){
			return space_count+1;
		}
		else if(current_board[row][col]==B_RING
			||current_board[row][col]==W_RING){
			return space_count;
		}
		row+=dir.first;
		col+=dir.second;
	}
	return space_count;
}

//Calculate mobility of rings
float Board::MobilityScore(Element ring){
	float mobility_score=0;
	for (int i = 0; i < current_board.size(); i++) {
		for (int j = 0; j < current_board.size(); j++){
			if(current_board[i][j]==ring){
				flipped_score+=board.MobilityUtility(ring,N_Dir,i,j);
				flipped_score+=board.MobilityUtility(ring,NE_Dir,i,j);
				flipped_score+=board.MobilityUtility(ring,SE_Dir,i,j);
				flipped_score+=board.MobilityUtility(ring,S_Dir,i,j);
				flipped_score+=board.MobilityUtility(ring,SW_Dir,i,j);
				flipped_score+=board.MobilityUtility(ring,NW_Dir,i,j);
			}
		}
	}
}

float GameState::EvalFunc(){
	float no_B_markers = board.CountMarkers(B_MARKER);
	float no_W_markers = board.CountMarkers(W_MARKER);

	float B_row = board.MarkerScore(B_MARKER,B_RING);
	float W_row = board.MarkerScore(W_MARKER,W_RING);

	Element flip_ring;
	//player hasn't moved yet
	if(current_player==0){
		flip_ring=W_RING;
	}
	else{
		flip_ring=B_RING;
	}	
	float flip_B_markers = board.FlippedScore(B_MARKER,flip_ring);
	float flip_W_markers = board.FlippedScore(W_MARKER,flip_ring);

	float mobility_B_ring = board.MobilityScore(B_RING);
	float mobility_W_ring = board.MobilityScore(W_RING);
	

	return (w0*no_B_markers
	+ w1*B_row
	+ w2*flip_B_markers
	+ w3*mobility_B_ring
	+ w4*playerBScore)*(a0+b0*playerBScore)

	+ (w5*no_W_markers
	+ w6*W_row
	+ w7*flip_W_markers
	+ w8*mobility_W_ring
	+ w9*playerAScore)*(a0+b1*playerAScore);
}