/* NYX monetization bootstrap.
 * Ads remain disabled until the owner adds a valid AdSense publisher ID and ad-unit IDs.
 * For EEA/UK/CH traffic, configure Google's certified Privacy & messaging CMP (or another
 * Google-certified TCF CMP) in the AdSense account before enabling ad delivery.
 */
(()=>{"use strict";
 const config=window.NYX_ADS_CONFIG||{publisherId:"",slots:[]};
 const pub=String(config.publisherId||"").trim();
 const slots=Array.isArray(config.slots)?config.slots.filter(x=>x&&String(x.id||"").trim()):[];
 if(!/^ca-pub-\\d+$/.test(pub)||!slots.length)return;
 if(!window.__tcfapi)return; // fail closed: never request ads without the configured CMP
 let started=false;
 const start=()=>{
   if(started)return;started=true;
   const script=document.createElement("script");
   script.async=true;script.crossOrigin="anonymous";
   script.src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client="+encodeURIComponent(pub);
   script.onload=()=>{
     const anchors=[...document.querySelectorAll("[data-nyx-ad-anchor]")];
     slots.forEach((slot,index)=>{
       const anchor=anchors[index];if(!anchor)return;
       const ins=document.createElement("ins");
       ins.className="adsbygoogle";ins.style.display="block";
       ins.setAttribute("data-ad-client",pub);ins.setAttribute("data-ad-slot",String(slot.id));
       ins.setAttribute("data-ad-format",slot.format||"auto");
       ins.setAttribute("data-full-width-responsive","true");
       anchor.classList.add("is-active");anchor.append(ins);
       try{(window.adsbygoogle=window.adsbygoogle||[]).push({})}catch(error){anchor.classList.remove("is-active");anchor.replaceChildren()}
     });
   };
   document.head.append(script);
 };
 try{
   window.__tcfapi("addEventListener",2,(tcData,success)=>{
     if(!success||!tcData)return;
     if(tcData.eventStatus==="tcloaded"||tcData.eventStatus==="useractioncomplete")start();
   });
 }catch(error){/* Keep ads disabled if the CMP API is unavailable. */}
})();
