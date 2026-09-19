
(function(){
  // back to top
  var b=document.getElementById('back-to-top');
  if(b){window.addEventListener('scroll',function(){b.classList.toggle('show',window.scrollY>420)},{passive:true});
    b.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'})});}
  // search + category filter (progressive enhancement: all cards are already in the HTML)
  var grid=document.getElementById('game-grid');
  if(grid){
    var input=document.getElementById('search-input'),chips=document.querySelectorAll('.chip[data-cat]'),
        count=document.getElementById('result-count'),none=document.getElementById('no-results'),
        cards=Array.prototype.slice.call(grid.querySelectorAll('.card')),cat='All';
    function apply(){
      var q=(input.value||'').trim().toLowerCase(),n=0;
      cards.forEach(function(c){
        var ok=(cat==='All'||c.dataset.cat===cat)&&(!q||c.dataset.search.indexOf(q)!==-1);
        c.hidden=!ok; if(ok)n++;
      });
      count.textContent=n+' game'+(n===1?'':'s')+' found';
      none.hidden=n!==0;
    }
    input.addEventListener('input',apply);
    chips.forEach(function(ch){ch.addEventListener('click',function(){
      cat=ch.dataset.cat;chips.forEach(function(c){c.classList.remove('active');c.setAttribute('aria-pressed','false')});
      ch.classList.add('active');ch.setAttribute('aria-pressed','true');apply();});});
    var p=new URLSearchParams(location.search);
    if(p.get('search')){input.value=p.get('search');}
    if(p.get('category')){chips.forEach(function(c){if(c.dataset.cat.toLowerCase()===p.get('category').toLowerCase())c.click();});}
    apply();
  }
  // click-to-load game frame
  var btn=document.getElementById('load-game'),frame=document.getElementById('play-frame');
  if(btn&&frame){
    btn.addEventListener('click',function(){
      var f=document.createElement('iframe');
      f.src=frame.dataset.src;
      f.title=frame.dataset.title;
      f.setAttribute('allow','fullscreen; autoplay; gamepad');
      f.setAttribute('sandbox','allow-scripts allow-same-origin allow-pointer-lock allow-popups allow-forms');
      f.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
      frame.innerHTML='';frame.appendChild(f);f.focus();
    });
  }
  var fs=document.getElementById('fs-btn');
  if(fs&&frame){fs.addEventListener('click',function(){
    var el=frame.requestFullscreen?frame:null; if(el){el.requestFullscreen().catch(function(){});}
  });if(!frame.requestFullscreen){fs.hidden=true;}}
})();
