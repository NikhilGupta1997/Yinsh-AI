var dimension = [document.documentElement.clientWidth, document.documentElement.clientHeight];

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

var centerx = game_canvas.width/2;
var centery = game_canvas.width/2;

var spacing = game_canvas.height/11;
var altitude=spacing*Math.sqrt(3)/2;

var current_player=0;

var player=new Array(2);
player[0]={board_rings:0, rings_won:0, color:"#BBBBBB", current_ring:[-1,-1], five_row:new Array(0)};
player[1]={board_rings:0, rings_won:0, color:"#4F4F4F", current_ring:[-1,-1], five_row:new Array(0)};

/*
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

var positions = new Array(11);
for (var i = 0; i < 11; i++) {
  positions[i] = new Array(11);
}

function LineTest(){
	game_ctx.beginPath();
	//game_ctx.moveTo(positions[i][begin].x,positions[i][begin].y);
	//game_ctx.lineTo(positions[i][end].x,positions[i][end].y);
	game_ctx.moveTo(0,0);
	game_ctx.lineTo(100,100);
	game_ctx.stroke();
}

function PlotPoints(){
	for (var i = 0; i < 11; i++) 
	{
		

		var x=i-5;
		var low=-5;
		var high=5;
		if(x==0){
			low=-4;
			high=4;
		}
		if(x>=1&&x<=4){
			low=-5+x;
		}
		if(x==5){
			low=1;
			high=4;
		}
		if(x>=-4&&x<=-1){
			high=5+x;
		}
		if(x==-5){
			low=-4;
			high=-1;
		}

		for(var j=0;j<11;j++){
			var y=j-5;
			
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
	for(var i=0;i<11;i++){
		var begin=0;
		var end=10;
		var j=0;

		while(positions[i][j].x==-1&&j<11){
			j++;
			if(j==11){
				break;
			}
		}
		begin=j;
		while(positions[i][j].x!=-1&&j<11){
			j++;
			if(j==11){
				break;
			}
		}
		end=j-1;
		game_ctx.beginPath();
		game_ctx.strokeStyle="#888888";
		game_ctx.moveTo(positions[i][begin].x,positions[i][begin].y);
		game_ctx.lineTo(positions[i][end].x,positions[i][end].y);
		//game_ctx.moveTo(0,0);
		//game_ctx.lineTo(100,100);
		game_ctx.stroke();
		
	}
	for(var j=0;j<11;j++){
		var begin=0;
		var end=10;
		var i=0;

		while(positions[i][j].x==-1&&i<11){
			i++;
			if(i==11){
				break;
			}
		}
		begin=i;
		while(positions[i][j].x!=-1&&i<11){
			i++;
			if(i==11){
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

	for(var i=0;i<11;i++){
		for(var j=0;j<11;j++){
			var x=i-5;
			var y=j-5;
			if(Math.abs(x)==5||(x==-4&&y==-4)||(x==-4&&y==1)||(x==1&&y==-4)){
				game_ctx.beginPath();
				game_ctx.moveTo(positions[i][j].x,positions[i][j].y);
				game_ctx.lineTo(positions[5-y][5-x].x,positions[5-y][5-x].y);
				//game_ctx.moveTo(0,0);
				//game_ctx.lineTo(100,100);
				game_ctx.stroke();
			}

		}
	}
}

function ActualColor(){
	test_ctx.clearRect(0, 0, test_canvas.width, test_canvas.height);
	for(var i=0;i<11;i++){
		for(var j=0;j<11;j++){

			if(positions[i][j].x==-1){
				continue;
			}
			test_ctx.beginPath();

			test_ctx.strokeStyle="#444444";
			if(positions[i][j].piece==0){
				test_ctx.fillStyle = "#000000";
			}
			if(positions[i][j].piece==-1){
				test_ctx.fillStyle = "#FF0000";
			}
			if(positions[i][j].piece==-2){
				test_ctx.fillStyle = "#FF00FF";
			}
			if(positions[i][j].piece==1){
				test_ctx.fillStyle = "#0000FF";
			}
			if(positions[i][j].piece==2){
				test_ctx.fillStyle = "#00FFFF";
			}
			

			test_ctx.arc(positions[i][j].x,positions[i][j].y,spacing/1.9,0,Math.PI*2);
			test_ctx.globalAlpha = 0.5;
			test_ctx.fill();			
			test_ctx.stroke();

			test_ctx.globalAlpha = 1.0
			test_ctx.strokeStyle="#000000";
		}
	}
}

function ColorItUp(){

	for(var i=0;i<11;i++){
		for(var j=0;j<11;j++){

			if(positions[i][j].x==-1){
				continue;
			}
			ctx.beginPath();
			if(i==0){
				game_ctx.strokeStyle="#FF0000";
			}
			else if(i==1){
				game_ctx.strokeStyle="#00FF00";
			}
			else if(i==2){
				game_ctx.strokeStyle="#0000FF";
			}
			else if(i==3){
				game_ctx.strokeStyle="#FFFF00";
			}
			else if(i==4){
				game_ctx.strokeStyle="#00FFFF";
			}
			else if(i==5){
				game_ctx.strokeStyle="#000000";
			}
			else if(i==6){
				game_ctx.strokeStyle="#004400";
			}
			else if(i==7){
				game_ctx.strokeStyle="#000044";
			}
			else if(i==8){
				game_ctx.strokeStyle="#444400";
			}
			else if(i==9){
				game_ctx.strokeStyle="#004444";
			}
			else if(i==10){
				game_ctx.strokeStyle="#444444";
			}

			game_ctx.arc(positions[i][j].x,positions[i][j].y,10,0,Math.PI*2);
			game_ctx.stroke();
			if(j==6){
				game_ctx.globalAlpha = 0.5;
				game_ctx.fillStyle = "red";
				game_ctx.fill();
				game_ctx.globalAlpha = 1.0;
			}
			if(j==4){
				game_ctx.globalAlpha = 0.5;
				game_ctx.fillStyle = "blue";
				game_ctx.fill();
				game_ctx.globalAlpha = 1.0;
			}
			game_ctx.strokeStyle="#000000";
		}
	}
}



PlotPoints();
//ColorItUp();

DrawBoardLines();
//LineTest();

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
		if(player[current_player].board_rings==5&&player[(current_player+1)%2].board_rings==5){
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
	for(var a=asign, b=bsign;xcoord+a>=0&&xcoord+a<11&&ycoord+b>=0&&ycoord+b<11
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
	for(var a=asign, b=bsign;xring+a>=0&&xring+a<11&&yring+b>=0&&yring+b<11
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
	for(var i=0;i<11;i++){
		for(var j=0;j+4<11;j++){
			if(Math.abs(positions[i][j].piece)!=1||positions[i][j].x==-1)
				continue;
			var isrow=true;
			for(var k=1;k<=4;k++){
				if(positions[i][j].piece!=positions[i][j+k].piece||positions[i][j+k].x==-1||j+k>=11){
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
			player[row_player].five_row.push([[i,j],[i,j+1],[i,j+2],[i,j+3],[i,j+4]]);
			
		}
	}
	for(var i=0;i+4<11;i++){
		for(var j=0;j<11;j++){
			if(Math.abs(positions[i][j].piece)!=1||positions[i][j].x==-1)
				continue;
			var isrow=true;
			for(var k=1;k<=4;k++){
				if(positions[i][j].piece!=positions[i+k][j].piece||positions[i+k][j].x==-1||i+k>=11){
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
			player[row_player].five_row.push([[i,j],[i+1,j],[i+2,j],[i+3,j],[i+4,j]]);
			
		}
	}
	for(var i=0;i<11;i++){
		for(var j=0;j<11;j++){
			if(Math.abs(positions[i][j].piece)!=1||positions[i][j].x==-1)
				continue;
			var isrow=true;
			for(var k=1;k<=4;k++){
				if(i+k>=11||j+k>=11||positions[i][j].piece!=positions[i+k][j+k].piece||positions[i+k][j+k].x==-1){
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
			player[row_player].five_row.push([[i,j],[i+1,j+1],[i+2,j+2],[i+3,j+3],[i+4,j+4]]);
			
		}
	}
	
}

function HighlightRow(){
	guide_ctx.clearRect(0, 0, guide_canvas.width, guide_canvas.height);
	if(player[current_player].five_row.length!=0){
		for(var i=0;i<player[current_player].five_row.length;i++){
			for(var j=0;j<5;j++){
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
		required_move=3;
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

function RemoveRow(xcoord,ycoord){
	var row_count=0;
	var select_row=-1;
	for(var i=0;i<player[current_player].five_row.length;i++){
		for(var j=0;j<5;j++){
			if(player[current_player].five_row[i][j][0]==xcoord&&player[current_player].five_row[i][j][1]==ycoord){
				row_count++;
				select_row=i;
			}
		}
	}
	if(row_count==1){
		for(var k=0;k<5;k++){
			var xclear=player[current_player].five_row[select_row][k][0];
			var yclear=player[current_player].five_row[select_row][k][1];
			piece_ctx.clearRect(positions[xclear][yclear].x-altitude/1.9, positions[xclear][yclear].y-altitude/1.9
					, altitude*1.1, altitude*1.1);
			positions[xclear][yclear].piece=0;

			for(var i=0;i<player[current_player].five_row.length;i++){
				if(i==select_row){
					continue;
				}
				for(var j=0;j<5;j++){
					if(player[current_player].five_row[i][j][0]==player[current_player].five_row[select_row][k][0]
						&&player[current_player].five_row[i][j][1]==player[current_player].five_row[select_row][k][1]){
							player[current_player].five_row.splice(i,1);
					}
				}
			}


		}

		player[current_player].five_row.splice(select_row,1);
		required_move=4;

		HighlightRow();
        return true
	} else {
        return false
    }


}

function RemoveRing(xcoord,ycoord){
	if(positions[xcoord][ycoord].piece==Math.pow(-1,current_player)*2){
		player[current_player].rings_won++;
		positions[xcoord][ycoord].board_rings--;

		piece_ctx.clearRect(positions[xcoord][ycoord].x-altitude/1.9, positions[xcoord][ycoord].y-altitude/1.9, altitude*1.1, altitude*1.1);
		piece_ctx.beginPath();
		piece_ctx.strokeStyle=player[current_player].color;
		piece_ctx.lineWidth=1;
		piece_ctx.arc(Math.pow(-1,current_player)*player[current_player].rings_won*(altitude)+(piece_canvas.width/2),altitude/2,altitude/2,0,Math.PI*2);
		piece_ctx.stroke();
		piece_ctx.lineWidth=1;

		positions[xcoord][ycoord].piece=0;
		if(player[current_player].rings_won==3){
			required_move=5;
		}
		else if(player[current_player].five_row.length==0){
			SwitchPlayer();
			if(player[current_player].five_row.length==0){
				required_move=2;
			}
			else{
				required_move=3;
				HighlightRow();
			}
		}
		else{
			required_move=3;
				HighlightRow();
		}
        return true
	} else {
        return false
    }
}

function IsClickValid(mouse){
	for(var i=0;i<11;i++){
		for(var j=0;j<11;j++){
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
					}
					else if(required_move==4){
						valid = RemoveRing(i,j);
					}
                    is_valid = valid
			}
		}
	}
	//ActualColor();
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
            /*game_ctx.beginPath();
			game_ctx.arc(canvasMousePosition.x,canvasMousePosition.y,10,0,Math.PI*2);
			game_ctx.stroke();*/
        }
    }, false);

