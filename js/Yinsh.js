// var dimension = [document.documentElement.clientWidth, document.documentElement.clientHeight];
var size = parseInt(document.currentScript.getAttribute('size'));
var rings = parseInt(document.currentScript.getAttribute('rings'));
var rows = parseInt(document.currentScript.getAttribute('rows'));
var seq = parseInt(document.currentScript.getAttribute('seq'));
var dimension = [ size , size ];

var game_canvas = document.getElementById('GameBoard');
game_canvas.width = dimension[1];
game_canvas.height = dimension[1];
var game_ctx = game_canvas.getContext("2d");

var piece_canvas = document.getElementById('PieceLayer');
piece_canvas.width = dimension[1];
piece_canvas.height = dimension[1];
var piece_ctx = piece_canvas.getContext("2d");

var guide_canvas = document.getElementById('GuideLayer');
guide_canvas.width = dimension[1];
guide_canvas.height = dimension[1];
var guide_ctx = guide_canvas.getContext("2d");

var test_canvas = document.getElementById('TestLayer');
test_canvas.width = dimension[1];
test_canvas.height = dimension[1];
var test_ctx = test_canvas.getContext("2d");

game_ctx.fillStyle = "#1999c4";
game_ctx.fillRect(0, 0, game_canvas.width, game_canvas.height);

var centerx = game_canvas.width/2;
var centery = game_canvas.width/2;

var spacing = game_canvas.height/rows;
var altitude=spacing*Math.sqrt(3)/2;

var current_player=0;

var player=new Array(2);
player[0]={board_rings:0, rings_won:0, color:"#c47719", current_ring:[-1,-1], five_row:new Array(0)};
player[1]={board_rings:0, rings_won:0, color:"#0a4fd8", current_ring:[-1,-1], five_row:new Array(0)};

/* The game state for a player
0-Place Rings
1-Select Ring
2-Move Ring
3-Remove Row
4-Remove Ring
*/
var required_move=0;

// Variables for game.py
var is_valid=false

function SwitchPlayer(){
	current_player=(current_player+1)%2;
}

/*
0-empty
-1,1-player tokens
-2,2-player rings

*/

function Point(x, y) {
  this.x = x;
  this.y = y;
  this.piece=0;
  this.guide=false;
}

var positions = new Array(rows);
for (var i = 0; i < rows; i++) {
  positions[i] = new Array(rows);
}

function PlotPoints(){
	for (var i = 0; i < rows; i++) {
		var x=i-rings;
		var low=-rings;
		var high=rings;
		
		if(x==0){
			low=-(rings-1); high=(rings-1);
		}
		
		if(x>=1&&x<=(rings-1)){
			low=-(rings)+x;
		}
		
		if(x==(rings)){
			low=1; high=(rings-1);
		}

		if(x>=-(rings-1)&&x<=-1){
			high=rings+x;
		}

		if(x==-(rings)){
			low=-(rings-1); high=-1;
		}

		for(var j=0;j<rows;j++){
			var y=j-(rings);
			
			if(!(y>=low&&y<=high)){
				positions[i][j]= new Point(-1,-1);
				continue;
			}
			
			positions[i][j]= new Point(centerx+altitude*x,centery-spacing*(y-x/2));
			positions[i][j].valid=true;
		}
	}
}

function DrawBoardLines(){
	for(var i=0;i<rows;i++){
		var begin=0;
		var end=rows-1;
		var j=0;

		while(positions[i][j].x==-1&&j<rows){
			j++;
			if(j==rows){
				break;
			}
		}
		begin=j;
		while(positions[i][j].x!=-1&&j<rows){
			j++;
			if(j==rows){
				break;
			}
		}
		end=j-1;
		game_ctx.beginPath();
		game_ctx.strokeStyle="#ffffff";
		game_ctx.moveTo(positions[i][begin].x,positions[i][begin].y);
		game_ctx.lineTo(positions[i][end].x,positions[i][end].y);
		//game_ctx.moveTo(0,0);
		//game_ctx.lineTo(100,100);
		game_ctx.stroke();
		
	}
	for(var j=0;j<rows;j++){
		var begin=0;
		var end=rows-1;
		var i=0;

		while(positions[i][j].x==-1&&i<rows){
			i++;
			if(i==rows){
				break;
			}
		}
		begin=i;
		while(positions[i][j].x!=-1&&i<rows){
			i++;
			if(i==rows){
				break;
			}
		}
		end=i-1;
		game_ctx.beginPath();
		game_ctx.moveTo(positions[begin][j].x,positions[begin][j].y);
		game_ctx.lineTo(positions[end][j].x,positions[end][j].y);
		//ctx.moveTo(0,0);
		//ctx.lineTo(100,100);
		game_ctx.stroke();
		
	}

	for(var i=0;i<rows;i++){
		for(var j=0;j<rows;j++){
			var x=i-rings;
			var y=j-rings;
			if(Math.abs(x)==rings||(x==-(rings-1)&&y==-(rings-1))||(x==-(rings-1)&&y==1)||(x==1&&y==-(rings-1))){
				game_ctx.beginPath();
				game_ctx.moveTo(positions[i][j].x,positions[i][j].y);
				game_ctx.lineTo(positions[rings-y][rings-x].x,positions[rings-y][rings-x].y);
				//game_ctx.moveTo(0,0);
				//game_ctx.lineTo(100,100);
				game_ctx.stroke();
			}

		}
	}
}

PlotPoints();
DrawBoardLines();

function PlaceRings(xcoord,ycoord){
	if(positions[xcoord][ycoord].piece==0){
		piece_ctx.beginPath();
		piece_ctx.strokeStyle=player[current_player].color;
		piece_ctx.lineWidth=5;
		piece_ctx.arc(positions[xcoord][ycoord].x,positions[xcoord][ycoord].y,altitude/2.4,0,Math.PI*2);
		piece_ctx.stroke();
		piece_ctx.lineWidth=1;
		positions[xcoord][ycoord].piece=Math.pow(-1,current_player)*2;
		player[current_player].board_rings++;
		if(player[current_player].board_rings==rings&&player[(current_player+1)%2].board_rings==rings){
				required_move=1;
		}
		SwitchPlayer();
        return true
	} else {
        return false
    }
}

function BlackGuides(xcoord,ycoord,asign,bsign,guide){
	var token_line=0;
	for(var a=asign, b=bsign;xcoord+a>=0&&xcoord+a<rows&&ycoord+b>=0&&ycoord+b<rows
		&&Math.abs(positions[xcoord+a][ycoord+b].piece)!=2&&positions[xcoord+a][ycoord+b].x!=-1;a+=asign,b+=bsign){
		if(positions[xcoord+a][ycoord+b].piece!=0){
			token_line=1;
			continue;
		}
		guide_ctx.beginPath();
		guide_ctx.strokeStyle="black";
		guide_ctx.arc(positions[xcoord+a][ycoord+b].x,positions[xcoord+a][ycoord+b].y,altitude/8,0,Math.PI*2);
		guide_ctx.fillStyle = "black";
		guide_ctx.fill();
		guide_ctx.stroke();
		positions[xcoord+a][ycoord+b].guide=guide;
		if(token_line==1){
			break;
		}
	}
}

function SelectRings(xcoord,ycoord){
	if(positions[xcoord][ycoord].piece==Math.pow(-1,current_player)*2){
		guide_ctx.beginPath();
		guide_ctx.strokeStyle="black";
		guide_ctx.arc(positions[xcoord][ycoord].x,positions[xcoord][ycoord].y,altitude*3/10,0,Math.PI*2);

		var grd=guide_ctx.createRadialGradient(positions[xcoord][ycoord].x,positions[xcoord][ycoord].y,altitude*3/20
			,positions[xcoord][ycoord].x,positions[xcoord][ycoord].y,altitude*3/10);

		grd.addColorStop(0,player[current_player].color);
		grd.addColorStop(1,"#444444");
		guide_ctx.fillStyle=grd;
		//guide_ctx.fillStyle = player[current_player].color;
		guide_ctx.fill();
		guide_ctx.stroke();
		player[current_player].current_ring=[xcoord,ycoord];
		
		BlackGuides(xcoord,ycoord,1,1,true);
		BlackGuides(xcoord,ycoord,-1,-1,true);
		BlackGuides(xcoord,ycoord,0,1,true);
		BlackGuides(xcoord,ycoord,1,0,true);
		BlackGuides(xcoord,ycoord,0,-1,true);
		BlackGuides(xcoord,ycoord,-1,0,true);
		
		required_move=2;
        return true
	} else {
        return false
    }
}

function RemoveBlackGuides(xring,yring,destx,desty,asign,bsign){
	var flip=0;
	if(Math.sign(destx-xring)==Math.sign(asign)&&Math.sign(desty-yring)==Math.sign(bsign)){
		flip=1;
	}
	for(var a=asign, b=bsign;xring+a>=0&&xring+a<rows&&yring+b>=0&&yring+b<rows
		&&Math.abs(positions[xring+a][yring+b].piece)!=2&&positions[xring+a][yring+b].x!=-1;a+=asign,b+=bsign){
		if(positions[xring+a][yring+b].piece==0){
			positions[xring+a][yring+b].guide=false;
			if(xring+a==destx&&yring+b==desty){

				piece_ctx.clearRect(positions[xring][yring].x-altitude/1.9, positions[xring][yring].y-altitude/1.9
					, altitude*1.1, altitude*1.1);

				positions[xring][yring].piece=Math.pow(-1,current_player);
				piece_ctx.beginPath();
				piece_ctx.strokeStyle="black";
				piece_ctx.arc(positions[xring][yring].x,positions[xring][yring].y,altitude*3/10,0,Math.PI*2);

				var grd=piece_ctx.createRadialGradient(positions[xring][yring].x,positions[xring][yring].y,altitude*3/20
					,positions[xring][yring].x,positions[xring][yring].y,altitude*3/10);

				grd.addColorStop(0,player[current_player].color);
				grd.addColorStop(1,"#444444");
				piece_ctx.fillStyle=grd;

				//piece_ctx.fillStyle = player[current_player].color;
				piece_ctx.fill();
				piece_ctx.stroke();

				positions[destx][desty].piece=Math.pow(-1,current_player)*2;
				piece_ctx.beginPath();
				piece_ctx.strokeStyle=player[current_player].color;
				piece_ctx.lineWidth=5;
				piece_ctx.arc(positions[destx][desty].x,positions[destx][desty].y,altitude/2.4,0,Math.PI*2);
				piece_ctx.stroke();
				piece_ctx.lineWidth=1;

				flip=0;
			}

		}
		if(flip==1&&Math.abs(positions[xring+a][yring+b].piece)==1){
			positions[xring+a][yring+b].piece*=-1;
			piece_ctx.beginPath();
			piece_ctx.strokeStyle="black";
			piece_ctx.arc(positions[xring+a][yring+b].x,positions[xring+a][yring+b].y,altitude*3/10,0,Math.PI*2);

			var grd=piece_ctx.createRadialGradient(positions[xring+a][yring+b].x,positions[xring+a][yring+b].y,altitude*3/20
					,positions[xring+a][yring+b].x,positions[xring+a][yring+b].y,altitude*3/10);

				
				
				

			if(positions[xring+a][yring+b].piece==1){
				grd.addColorStop(0,player[0].color);
				grd.addColorStop(1,"#444444");
				//piece_ctx.fillStyle = player[0].color;
			}
			else{
				grd.addColorStop(0,player[1].color);
				grd.addColorStop(1,"#444444");
				//piece_ctx.fillStyle = player[1].color;
			}

			piece_ctx.fillStyle=grd;
			
			piece_ctx.fill();
			piece_ctx.stroke();
		}
		
	}
}

function CheckRows(){
	for(var i=0;i<rows;i++){
		for(var j=0;j+seq-1<rows;j++){
			if(Math.abs(positions[i][j].piece)!=1||positions[i][j].x==-1)
				continue;
			var isrow=true;
			for(var k=1;k<=seq-1;k++){
				if(positions[i][j].piece!=positions[i][j+k].piece||positions[i][j+k].x==-1||j+k>=rows){
					isrow=false;
					break;
				}
			}
			if(isrow==false){
				continue;
			}
			
			var row_player=0;
			if(positions[i][j].piece==-1){
				row_player++;
			}
			var list = [];
			for(var k=0;k<seq;k++){
				list.push([i,j+k])
			}
			player[row_player].five_row.push(list)
			// player[row_player].five_row.push([[i,j],[i,j+1],[i,j+2],[i,j+3],[i,j+4]]);
			// player[row_player].five_row.push([[i, j+k] for k in range(seq)]);
			 
		}
	}
	for(var i=0;i+seq-1<rows;i++){
		for(var j=0;j<rows;j++){
			if(Math.abs(positions[i][j].piece)!=1||positions[i][j].x==-1)
				continue;
			var isrow=true;
			for(var k=1;k<=seq-1;k++){
				if(positions[i][j].piece!=positions[i+k][j].piece||positions[i+k][j].x==-1||i+k>=rows){
					isrow=false;
					break;
				}
			}
			if(isrow==false){
				continue;
			}
			
			var row_player=0;
			if(positions[i][j].piece==-1){
				row_player++;
			}
			// player[row_player].five_row.push([[i,j],[i+1,j],[i+2,j],[i+3,j],[i+4,j]]);
			var list = [];
			for(var k=0;k<seq;k++){
				list.push([i+k,j])
			}
			player[row_player].five_row.push(list)
			// player[row_player].five_row.push([[i+k, j] for k in range(seq)]);
			
		}
	}
	for(var i=0;i<rows;i++){
		for(var j=0;j<rows;j++){
			if(Math.abs(positions[i][j].piece)!=1||positions[i][j].x==-1)
				continue;
			var isrow=true;
			for(var k=1;k<=seq-1;k++){
				if(i+k>=rows||j+k>=rows||positions[i][j].piece!=positions[i+k][j+k].piece||positions[i+k][j+k].x==-1){
					isrow=false;
					break;
				}
			}
			if(isrow==false){
				continue;
			}
			
			var row_player=0;
			if(positions[i][j].piece==-1){
				row_player++;
			}
			// player[row_player].five_row.push([[i,j],[i+1,j+1],[i+2,j+2],[i+3,j+3],[i+4,j+4]]);
			var list = [];
			for(var k=0;k<seq;k++){
				list.push([i+k,j+k])
			}
			player[row_player].five_row.push(list)
			// player[row_player].five_row.push([[i+k, j+k] for k in range(seq)]);
			
		}
	}
	
}

function HighlightRow(state=3){
	guide_ctx.clearRect(0, 0, guide_canvas.width, guide_canvas.height);
	if(player[current_player].five_row.length!=0){
		for(var i=0;i<player[current_player].five_row.length;i++){
			for(var j=0;j<seq;j++){
				var xindex=player[current_player].five_row[i][j][0];
				var yindex=player[current_player].five_row[i][j][1];

				guide_ctx.beginPath();
				guide_ctx.strokeStyle="black";
				guide_ctx.arc(positions[xindex][yindex].x,positions[xindex][yindex].y,altitude*3/10,0,Math.PI*2);
				guide_ctx.fillStyle = "black";
				guide_ctx.fill();
				guide_ctx.stroke();
			}
		}
		required_move=state;
	}
}

function MoveRings(xcoord,ycoord){
	if(positions[xcoord][ycoord].guide==true){
		guide_ctx.clearRect(0, 0, guide_canvas.width, guide_canvas.height);
		RemoveBlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],xcoord,ycoord,1,1);
		RemoveBlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],xcoord,ycoord,1,0);
		RemoveBlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],xcoord,ycoord,0,1);
		RemoveBlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],xcoord,ycoord,-1,0);
		RemoveBlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],xcoord,ycoord,0,-1);
		RemoveBlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],xcoord,ycoord,-1,-1);
		required_move=1;
		CheckRows();
		HighlightRow();
		if(required_move!=3){
			SwitchPlayer();
			HighlightRow(6);
		}
        return true
	}
	else{
		BlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],1,1,false);
		BlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],-1,-1,false);
		BlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],0,1,false);
		BlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],1,0,false);
		BlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],0,-1,false);
		BlackGuides(player[current_player].current_ring[0],player[current_player].current_ring[1],-1,0,false);
		guide_ctx.clearRect(0, 0, guide_canvas.width, guide_canvas.height);
		required_move=1;
        return false
	}
}

function matchPoints(px1, py1, px2, py2){
    if(px1 == px2 && py1 == py2){
        return true;
    } else {
        return false;
    }
}

function RemoveRow(x, y, state=4){
    if(x == null || y == null){
        return false;
    }
	var row_count=0;
	var select_row=-1;
	for(var i=0;i<player[current_player].five_row.length;i++){
        firstPointX = player[current_player].five_row[i][0][0];
        firstPointY = player[current_player].five_row[i][0][1];
        lastPointX = player[current_player].five_row[i][seq-1][0];
        lastPointY = player[current_player].five_row[i][seq-1][1];
        
        if(matchPoints(x, y, firstPointX, firstPointY) || matchPoints(x, y, lastPointX, lastPointY)) {
            if(state == 4) {
	            required_move=3.5;
	        }
	       	else{
	       		required_move=6.5;
	       	}
            return true;
        }
	}
	return false;
}

function RemoveRowEnd(startX, startY, endX, endY, state=4){
    if(startX == null || startY == null){
        return false;
    }
	var row_count=0;
	var select_row=-1;
	for(var i=0;i<player[current_player].five_row.length;i++){
        firstPointX = player[current_player].five_row[i][0][0];
        firstPointY = player[current_player].five_row[i][0][1];
        lastPointX = player[current_player].five_row[i][seq-1][0];
        lastPointY = player[current_player].five_row[i][seq-1][1];
        
        if((matchPoints(startX, startY, firstPointX, firstPointY) && matchPoints(endX, endY, lastPointX,
                    lastPointY)) || (matchPoints(startX, startY, lastPointX, lastPointY) &&
                        matchPoints(endX, endY, firstPointX, firstPointY))) {
            select_row = i;
            row_count += 1;
         
        }
	}
	if(row_count>=1){
        var removeList = new Array();
        removeList.push(select_row);

		for(var k=0;k<seq;k++){
			var xclear=player[current_player].five_row[select_row][k][0];
			var yclear=player[current_player].five_row[select_row][k][1];
			piece_ctx.clearRect(positions[xclear][yclear].x-altitude/1.9, positions[xclear][yclear].y-altitude/1.9
					, altitude*1.1, altitude*1.1);
			positions[xclear][yclear].piece=0;

			for(var i=0;i<player[current_player].five_row.length;i++){
				if(i==select_row){
					continue;
				}
				for(var j=0;j<seq;j++){
					if(player[current_player].five_row[i][j][0]==player[current_player].five_row[select_row][k][0]
						&&player[current_player].five_row[i][j][1]==player[current_player].five_row[select_row][k][1]){
                            removeList.push(i);
					}
				}
			}
		}
        player[current_player].five_row.length = 0
		CheckRows();
		required_move=state;
		guide_ctx.clearRect(0, 0, guide_canvas.width, guide_canvas.height);
        return true
	} else {
        return false
    }
}

function RemoveRing(xcoord,ycoord,state=4){
	if(positions[xcoord][ycoord].piece==Math.pow(-1,current_player)*2){
		player[current_player].rings_won++;
		positions[xcoord][ycoord].board_rings--;

		piece_ctx.clearRect(positions[xcoord][ycoord].x-altitude/1.9, positions[xcoord][ycoord].y-altitude/1.9, altitude*1.1, altitude*1.1);
		piece_ctx.beginPath();
		piece_ctx.strokeStyle=player[current_player].color;
		piece_ctx.lineWidth=5;
		piece_ctx.arc(Math.pow(-1,current_player)*(player[current_player].rings_won+2)*(altitude)+(piece_canvas.width/2),altitude/2,altitude/2.4,0,Math.PI*2);
		piece_ctx.stroke();
		piece_ctx.lineWidth=1;

		positions[xcoord][ycoord].piece=0;
		if(player[current_player].rings_won==3){
			required_move=5;
			SwitchPlayer();
		}
		else if(player[current_player].five_row.length==0){
			if(state!=7){
				SwitchPlayer();
			}
			if(player[current_player].five_row.length==0){
				required_move=1;
			}
			else{
				HighlightRow(6);
			}
		}
		else{
			HighlightRow();
		}
        return true
	} else {
        return false
    }
}

var startX = null;
var startY = null;
function IsClickValid(mouse){
	for(var i=0;i<rows;i++){
		for(var j=0;j<rows;j++){
			if(positions[i][j].x==-1){
				continue;
			}
			if(positions[i][j].x-altitude/2<mouse.x&&positions[i][j].x+altitude/2>mouse.x
				&&positions[i][j].y-altitude/2<mouse.y&&positions[i][j].y+altitude/2>mouse.y){
                    valid = false
					if(required_move==0){
						valid = PlaceRings(i,j);
					}
					else if(required_move==1){
						valid = SelectRings(i,j);
					}
					else if(required_move==2){
						valid = MoveRings(i,j);
					}
                    else if(required_move==3){
                    	valid = RemoveRow(i,j);
                    	startX = i;
                    	startY = j;
                    }
                    else if(required_move==3.5){
                        valid = RemoveRowEnd(startX, startY, i,j);
                    }
					else if(required_move==4){
						valid = RemoveRing(i,j);
					}
					else if(required_move==6){ // Other player first removes row and then plays move
						valid = RemoveRow(i,j,7);
						startX = i;
                    	startY = j;
					}
					else if(required_move==6.5){
						valid = RemoveRowEnd(startX, startY, i,j, 7);
                    }
					else if(required_move==7){ // Other player first removes ring and then plays move
						valid = RemoveRing(i,j,7);
					}
                    is_valid = valid
			}
		}
	}
}

function getCanvasMousePosition (event) {
  var rect = piece_canvas.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

document.addEventListener('click', function(event) {
        lastDownTarget = event.target;
        if(lastDownTarget == piece_canvas||lastDownTarget == guide_canvas||lastDownTarget == game_canvas) {
        	var canvasMousePosition = getCanvasMousePosition(event);
        	IsClickValid(canvasMousePosition);
        }
    }, false);

