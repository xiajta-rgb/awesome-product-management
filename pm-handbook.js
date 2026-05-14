(function(){
window.addEventListener('scroll',function(){
var h=document.documentElement;
var scrollTop=h.scrollTop||document.body.scrollTop;
var scrollHeight=h.scrollHeight-h.clientHeight;
var progress=(scrollTop/scrollHeight)*100;
document.getElementById('progressBar').style.width=progress+'%';

var sections=document.querySelectorAll('.chapter,.section,.hero');
var navLinks=document.querySelectorAll('.side-nav a[href^="#"]');
var current='';
sections.forEach(function(s){
var top=s.offsetTop-200;
if(scrollTop>=top)current=s.getAttribute('id');
});
navLinks.forEach(function(l){
l.classList.remove('active');
if(l.getAttribute('href')==='#'+current)l.classList.add('active');
});
});

var observer=new IntersectionObserver(function(entries){
entries.forEach(function(e){
if(e.isIntersecting){
e.target.classList.add('visible');
}
});
},{threshold:0.1,rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.animate-in').forEach(function(el){observer.observe(el)});

document.querySelectorAll('.side-nav a').forEach(function(a){
a.addEventListener('click',function(){
if(window.innerWidth<=1024){
document.querySelector('.side-nav').classList.remove('open');
}
});
});
})();
