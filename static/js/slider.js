let slidePosition=0;
const sliders=document.querySelectorAll('.slider-item');
const totalSlider=sliders.length;

function updatePosition(){
	sliders.forEach(slide=>{
		slide.classList.remove('active');
		slide.classList.add('hidden');
	});

	sliders[slidePosition].classList.add('active');
}

function PrevSlide(){
	if(slidePosition==0){
		slidePosition=totalSlider-1;
	}else{
		slidePosition--;
	}
	updatePosition();
}

function NextSlide(){
	if(slidePosition==totalSlider-1){
		slidePosition=0;
	}else{
		slidePosition++;
	}
	updatePosition();
}

setInterval(()=>{
	if(slidePosition==totalSlider-1){
		slidePosition=0;
	}else{
		slidePosition++;
	}
	updatePosition();
},10000);