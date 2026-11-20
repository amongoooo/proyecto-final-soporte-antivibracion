/* Acompaña a estilo/vidrio.css: llena el riel de cada slider hasta el pulgar (--p) y mueve el indicador de los
   controles segmentados (.seg) hacia el botón elegido (aria-selected o aria-pressed = true). */
(function(){
  'use strict';
  function fill(r){var a=+r.min||0,b=+r.max||100,v=+r.value;r.style.setProperty('--p',((v-a)/(b-a||1))*100+'%')}
  function allRanges(){[].forEach.call(document.querySelectorAll('input[type=range]'),fill)}
  document.addEventListener('input',function(e){if(e.target.type==='range')fill(e.target)},true);
  /* Los valores también cambian desde el código (botones que mueven el slider): se revisan en cada cuadro de forma barata. */
  var last=new WeakMap();
  function poll(){[].forEach.call(document.querySelectorAll('input[type=range]'),function(r){if(last.get(r)!==r.value){last.set(r,r.value);fill(r)}});requestAnimationFrame(poll)}

  function seg(host){
    var ind=host.querySelector(':scope>.seg-ind');
    if(!ind){ind=document.createElement('span');ind.className='seg-ind';ind.setAttribute('aria-hidden','true');host.insertBefore(ind,host.firstChild)}
    function place(scroll){
      var on=host.querySelector(':scope>button[aria-selected="true"],:scope>button[aria-pressed="true"]');
      if(!on){ind.style.opacity=0;return}
      ind.style.opacity=1;ind.style.width=on.offsetWidth+'px';ind.style.transform='translateX('+on.offsetLeft+'px)';
      if(scroll&&host.scrollWidth>host.clientWidth){var x=on.offsetLeft-(host.clientWidth-on.offsetWidth)/2;host.scrollTo({left:x,behavior:'smooth'})}
    }
    new MutationObserver(function(){place(true)}).observe(host,{subtree:true,attributes:true,attributeFilter:['aria-selected','aria-pressed'],childList:true});
    window.addEventListener('resize',function(){place(false)});
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){place(false)});
    place(false);
  }
  window.vidrioSeg=seg;
  function start(){allRanges();requestAnimationFrame(poll);[].forEach.call(document.querySelectorAll('.seg'),seg)}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
