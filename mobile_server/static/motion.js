var imgArray = []; //图片文件名数组，带路径
var typeArray = []; //图片类型数组，0=壁纸，1=动态，2=主题
var linkArray = []; //图片对应链接数组
$.fn.loadimg = function(){
	h = "";
	for(i=0; i<imgArray.length; i++)
	{
		link = (linkArray[i])? linkArray[i] : "#";
		switch(typeArray[i]){
		case 0:
			h = '<li><a href="'+ link +'"><img src="'+ imgArray[i] +'" class="scale43" /></a></li>';
			break;
		case 1:
			h = '<li><span>动态</span><a href="'+ link +'"><img src="'+ imgArray[i] +'" class="scale35" /></a></li>';
			break;
		case 2:
			h = '<li><span>主题</span><a href="'+ link +'"><img src="'+ imgArray[i] +'" class="scale35" /></a></li>';
			break;
		}
		n = i % 3 + 1;
		$("#findlist" + n).append(h);
	}
};

$(document).ready(function(){
 	
	$("input[type=radio]").click(function(){
		$("label").each(function(){ $(this).css({"background-image":"url(static/images/radio_n.png)"}); $(this).children("input").removeAttr("name"); });
		$(this).parent("label").css({"background-image":"url(static/images/radio_y.png)"});
        $(this).attr("name","sex");
        if($(".logo").hasClass("avatar1")==false){
        if($(this).parent("label").hasClass("radiom1"))
            $(".logo img").attr("src","static/images/logo2.png");
        else
            $(".logo img").attr("src","static/images/logo3.png");
        }

	});
//	$("input[type=radio]").each(function(){
//		if($(this).attr("checked") == "checked")/
//		{
//			$(this).parent("label").css({"background-image":"url(static/images/radio_y.png)"});
//		}else{
//			$(this).parent("label").css({"background-image":"url(static/images/radio_n.png)"});
//		}
//	});
	
	$.fn.loadimg();
	$(".scale43").each(function(){
		w = $(this).width();
		$(this).height(w*3/4);
	});
	$(".scale44").each(function(){
		w = $(this).width();
		$(this).height(w);
	});
	$(".scale32").each(function(){
		w = $(this).width();
		$(this).height(w*2/3);
	});
	$(".scale35").each(function(){
		w = $(this).width();
		$(this).height(w*5/3);
	});
	$(".scale11").each(function(){
		w = $(this).width();
		$(this).height(w);
	});
});
