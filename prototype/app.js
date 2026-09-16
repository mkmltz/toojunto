const KEY="toojunto_mvp01";
const initial={
  role:"gestor",screen:"login",loggedIn:false,
  user:{name:"Moisés",email:"moises@demo.com"},
  group:{
    id:1,name:"Caixinha dos Amigos",value:200,cycles:10,start:"10/09/2026",
    status:"Ativo",drawDone:false,currentCycle:3,
    pixKey:"ana@pix.com",recipient:"Ana",progress:60
  },
  participants:[
    {name:"Moisés",initial:"M",position:1,status:"confirmado"},
    {name:"Ana",initial:"A",position:2,status:"confirmado"},
    {name:"Carlos",initial:"C",position:3,status:"confirmado"},
    {name:"Juliana",initial:"J",position:4,status:"confirmado"},
    {name:"Rafael",initial:"R",position:5,status:"confirmado"},
    {name:"Fernanda",initial:"F",position:6,status:"confirmado"},
    {name:"Lucas",initial:"L",position:7,status:"confirmado"},
    {name:"Patrícia",initial:"P",position:8,status:"confirmado"},
    {name:"Bruno",initial:"B",position:9,status:"confirmado"},
    {name:"Camila",initial:"C",position:10,status:"confirmado"}
  ],
  invites:[
    {name:"João",phone:"(71) 99999-1111",status:"Pendente"},
    {name:"Marina",phone:"(71) 99999-2222",status:"Aceito"}
  ],
  payments:[
    {id:1,payer:"Carlos",cycle:3,value:200,status:"Pendente",date:"14/09/2026"},
    {id:2,payer:"Juliana",cycle:3,value:200,status:"Confirmado",date:"13/09/2026"},
    {id:3,payer:"Rafael",cycle:3,value:200,status:"Confirmado",date:"12/09/2026"}
  ],
  history:[
    {date:"10/09/2026",event:"Grupo criado",detail:"Caixinha dos Amigos"},
    {date:"11/09/2026",event:"Sorteio realizado",detail:"Ordem de contemplação definida"},
    {date:"13/09/2026",event:"Pagamento confirmado",detail:"Juliana → Ana · R$ 200"},
  ],
  order:[]
};
let state=load();
function load(){try{return JSON.parse(localStorage.getItem(KEY))||structuredClone(initial)}catch(e){return structuredClone(initial)}}
function save(){localStorage.setItem(KEY,JSON.stringify(state))}
function money(v){return v.toLocaleString("pt-BR",{style:"currency",currency:"BRL"})}
function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
function initials(name){return name.split(" ").map(x=>x[0]).slice(0,2).join("").toUpperCase()}
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2200)}
const App={
  go(screen){state.screen=screen;save();render()},
  login(){
    const email=document.getElementById("loginEmail")?.value.trim();
    const pass=document.getElementById("loginPassword")?.value;
    if(!email||!pass){toast("Informe e-mail e senha");return}
    state.loggedIn=true;state.user.email=email;state.screen="home";save();render();toast("Login realizado");
  },
  signup(){
    const name=document.getElementById("signupName")?.value.trim();
    const email=document.getElementById("signupEmail")?.value.trim();
    const pass=document.getElementById("signupPassword")?.value;
    if(!name||!email||!pass){toast("Preencha os campos obrigatórios");return}
    state.loggedIn=true;state.user={name,email};state.screen="home";save();render();toast("Conta criada");
  },
  logout(){state.loggedIn=false;state.screen="login";save();render();toast("Você saiu da conta")},
  toggleRole(){state.role=state.role==="gestor"?"participante":"gestor";save();render();toast("Perfil: "+(state.role==="gestor"?"Gestor":"Participante"))},
  reset(){if(confirm("Resetar o protótipo para o cenário inicial?")){state=structuredClone(initial);save();render();toast("Protótipo resetado")}},
  showHelp(){modal(`<h2>Como testar</h2><p>Este é um protótipo funcional, sem backend. Os dados ficam salvos no navegador.</p><ul><li>Alterne Gestor/Participante no botão “MS”.</li><li>Crie um grupo e veja o fluxo.</li><li>Faça o sorteio.</li><li>Registre e confirme um pagamento.</li></ul><button class="btn btn-primary" onclick="closeModal()">Entendi</button><button class="btn btn-secondary" onclick="App.logout();closeModal()">Sair da conta</button><button class="btn btn-secondary" onclick="App.reset();closeModal()">Resetar demonstração</button>`)},
  createGroup(){
    const n=document.getElementById("gname").value.trim(), v=Number(document.getElementById("gvalue").value), q=Number(document.getElementById("gq").value), c=Number(document.getElementById("gc").value);
    if(!n||!v||!q||!c){toast("Preencha os campos obrigatórios");return}
    state.group={...state.group,name:n,value:v,cycles:c,currentCycle:1,progress:0,drawDone:false};
    state.participants=[{name:state.user.name,initial:initials(state.user.name),position:1,status:"confirmado"}];
    state.history.unshift({date:new Date().toLocaleDateString("pt-BR"),event:"Grupo criado",detail:n});
    save();toast("Grupo criado");App.go("groups");
  },
  invite(){
    const n=document.getElementById("iname").value.trim(), p=document.getElementById("iphone").value.trim();
    if(!n){toast("Informe o nome");return}
    const token=Math.random().toString(36).slice(2,10)+Date.now().toString(36).slice(-4);
    const link=`https://app.toojunto.com.br/convite/${token}`;
    const message=`Olá, ${n}! 👋\\n\\nVocê foi convidado(a) para participar da caixinha "${state.group.name}" no TooJunto.\\n\\nClique no link para ver o convite e entrar no grupo:\\n${link}\\n\\nTooJunto — sua caixinha, organizada e transparente.`;
    state.invites.unshift({id:Date.now(),name:n,phone:p,status:"Pendente",token,link,message});
    state.lastInvite={name:n,phone:p,link,message};
    save();toast("Convite criado com link");App.go("invite-link");
  },
  copyInviteLink(){
    const link=state.lastInvite?.link;
    if(!link){toast("Nenhum convite disponível");return}
    const done=()=>toast("Link copiado");
    if(navigator.clipboard){navigator.clipboard.writeText(link).then(done).catch(()=>fallbackCopy(link,done))}
    else fallbackCopy(link,done);
  },
  copyInviteMessage(){
    const msg=state.lastInvite?.message;
    if(!msg){toast("Nenhum convite disponível");return}
    const done=()=>toast("Mensagem copiada");
    if(navigator.clipboard){navigator.clipboard.writeText(msg).then(done).catch(()=>fallbackCopy(msg,done))}
    else fallbackCopy(msg,done);
  },
  openWhatsApp(){
    const invite=state.lastInvite;
    if(!invite){toast("Nenhum convite disponível");return}
    const phone=(invite.phone||"").replace(/\\D/g,"");
    const url=phone?`https://wa.me/55${phone}?text=${encodeURIComponent(invite.message)}`:`https://wa.me/?text=${encodeURIComponent(invite.message)}`;
    window.open(url,"_blank");
  },
  acceptInvite(){toast("Convite aceito");state.invites=state.invites.map(x=>x.status==="Pendente"?{...x,status:"Aceito"}:x);save();App.go("groups")},
  draw(){
    if(state.group.drawDone){toast("O sorteio já foi realizado");return}
    let arr=[...state.participants];for(let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]]}
    state.order=arr.map((p,i)=>({...p,draw:i+1}));state.group.drawDone=true;
    state.history.unshift({date:new Date().toLocaleDateString("pt-BR"),event:"Sorteio realizado",detail:"Ordem de contemplação definida"});
    save();App.go("draw-result");
  },
  registerPayment(){
    const pay={id:Date.now(),payer:state.role==="gestor"?"Moisés":"Moisés",cycle:state.group.currentCycle,value:state.group.value,status:"Pendente",date:new Date().toLocaleDateString("pt-BR")};
    state.payments.unshift(pay);save();toast("Pagamento registrado");App.go("payments");
  },
  confirmPayment(id,ok=true){
    const p=state.payments.find(x=>x.id===id);if(!p)return;
    p.status=ok?"Confirmado":"Recusado";
    state.history.unshift({date:new Date().toLocaleDateString("pt-BR"),event:ok?"Pagamento confirmado":"Pagamento recusado",detail:`${p.payer} · ${money(p.value)}`});
    save();toast(ok?"Pagamento confirmado":"Pagamento recusado");render();
  }
};
function nav(active){document.getElementById("bottomNav").style.display="flex";document.querySelectorAll("[data-nav]").forEach(b=>b.classList.toggle("active",b.dataset.nav===active))}
function layout(content,active="home"){document.getElementById("app").innerHTML=content;nav(active)}
function header(title,sub=""){return `<div class="screen-title"><div><h1>${title}</h1>${sub?`<p class="subtitle">${sub}</p>`:""}</div><div class="role"><button class="${state.role==="gestor"?"active":""}" onclick="state.role='gestor';save();render()">Gestor</button><button class="${state.role==="participante"?"active":""}" onclick="state.role='participante';save();render()">Participante</button></div></div>`}
function render(){
 const s=state.screen;
 if(!state.loggedIn && s!=="login" && s!=="signup") return loginScreen();
 if(s==="login")return loginScreen();
 if(s==="signup")return signupScreen();
 if(s==="home")return home();
 if(s==="groups")return groups();
 if(s==="create-group")return createGroupScreen();
 if(s==="invites")return invites();
 if(s==="invite")return inviteScreen();
 if(s==="invite-link")return inviteLinkScreen();
 if(s==="invite-received")return inviteReceived();
 if(s==="group")return groupScreen();
 if(s==="draw")return drawScreen();
 if(s==="draw-result")return drawResult();
 if(s==="payment")return paymentScreen();
 if(s==="payments")return payments();
 if(s==="contemplation")return contemplation();
 if(s==="history")return historyScreen();
 layout(`<div class="empty">Tela não encontrada.<button class="btn btn-primary" onclick="App.go('home')">Voltar</button></div>`);
}
function loginScreen(){
 document.getElementById("bottomNav").style.display="none";
 document.getElementById("app").innerHTML=`
 <div style="min-height:calc(100vh - 84px);display:flex;align-items:center;justify-content:center">
   <div style="width:100%;max-width:430px">
     <div class="center" style="margin-bottom:26px">
       <div class="brand-mark" style="margin:auto;width:58px;height:58px;border-radius:18px;font-size:27px">T</div>
       <h1 style="margin-top:14px">Bem-vindo ao TooJunto</h1>
       <p class="subtitle">Sua caixinha, organizada e transparente.</p>
     </div>
     <div class="card">
       <label>E-mail</label>
       <input id="loginEmail" type="email" value="moises@demo.com" placeholder="seu@email.com" autocomplete="email">
       <label>Senha</label>
       <input id="loginPassword" type="password" value="123456" placeholder="Digite sua senha" autocomplete="current-password">
       <button class="btn btn-primary" onclick="App.login()">Entrar</button>
       <button class="btn btn-secondary" onclick="App.go('signup')">Criar minha conta</button>
       <button class="btn" onclick="toast('Fluxo de recuperação será incluído nas próximas versões')">Esqueci minha senha</button>
     </div>
     <p class="center small">Protótipo funcional V0.1 · Dados simulados</p>
   </div>
 </div>`;
}
function signupScreen(){
 document.getElementById("bottomNav").style.display="none";
 document.getElementById("app").innerHTML=`
 <div style="min-height:calc(100vh - 84px);display:flex;align-items:center;justify-content:center">
  <div style="width:100%;max-width:430px">
   <button class="back" onclick="App.go('login')">← Voltar para entrar</button>
   <div class="center" style="margin-bottom:18px"><h1>Criar sua conta</h1><p class="subtitle">É rápido. Vamos começar pelo básico.</p></div>
   <div class="card">
    <label>Nome completo *</label><input id="signupName" placeholder="Como você quer ser chamado?">
    <label>E-mail *</label><input id="signupEmail" type="email" placeholder="seu@email.com">
    <label>Telefone</label><input id="signupPhone" placeholder="(71) 99999-9999">
    <label>Senha *</label><input id="signupPassword" type="password" placeholder="Crie uma senha">
    <button class="btn btn-primary" onclick="App.signup()">Criar conta</button>
   </div>
  </div>
 </div>`;
}
function home(){
 layout(`
 <section class="hero">
   <span class="badge" style="background:#2C744B;color:#fff">Protótipo V0.1</span>
   <h1 style="margin-top:12px">Sua caixinha,<br>organizada e transparente.</h1>
   <p>Um jeito simples de criar, participar, pagar e acompanhar uma caixinha em grupo.</p>
   <button class="btn btn-primary" onclick="App.go('group')">Abrir minha caixinha</button>
 </section>
 ${header("Olá, "+esc(state.user.name)+"!","Vamos continuar de onde paramos.")}
 <div class="card"><div style="display:flex;justify-content:space-between;gap:10px"><div><strong>${esc(state.group.name)}</strong><div class="small">${money(state.group.value)} por mês · ${state.group.cycles} ciclos</div></div><span class="badge">${state.group.status}</span></div>
 <div style="margin-top:15px" class="small">Progresso do grupo</div><div class="progress" style="margin-top:6px"><div style="width:${state.group.progress}%"></div></div>
 <button class="btn btn-primary" onclick="App.go('group')">Ver grupo</button></div>
 <div class="grid">
   <div class="stat"><strong>${state.group.currentCycle}/${state.group.cycles}</strong><span>Ciclo atual</span></div>
   <div class="stat"><strong>${state.participants.length}</strong><span>Participantes</span></div>
 </div>
 <div class="card" style="margin-top:14px"><h2>Atalhos</h2>
   <button class="btn btn-secondary" onclick="App.go('create-group')">+ Criar nova caixinha</button>
   <button class="btn btn-secondary" onclick="App.go('invites')">Convites</button>
   <button class="btn btn-secondary" onclick="App.go('draw')">Sorteio</button>
 </div>`);
}
function groups(){layout(`${header("Meu grupo","Acompanhe a caixinha em um só lugar.")}
<div class="card"><div style="display:flex;justify-content:space-between"><div><h2>${esc(state.group.name)}</h2><div class="small">${money(state.group.value)} por ciclo</div></div><span class="badge">${state.group.status}</span></div>
<div class="grid" style="margin-top:14px"><div class="stat"><strong>${state.participants.length}</strong><span>Participantes</span></div><div class="stat"><strong>${state.group.currentCycle}</strong><span>Ciclo atual</span></div></div>
<button class="btn btn-primary" onclick="App.go('group')">Detalhes do grupo</button></div>
<div class="card"><h2>O que fazer agora?</h2>
<button class="btn btn-secondary" onclick="App.go('payment')">Registrar pagamento</button>
<button class="btn btn-secondary" onclick="App.go('draw')">Ver sorteio</button></div>`,"groups")}
function createGroupScreen(){layout(`<button class="back" onclick="App.go('home')">← Voltar</button>${header("Criar caixinha","Comece com o básico.")}
<div class="card"><label>Nome da caixinha *</label><input id="gname" placeholder="Ex.: Caixinha dos Amigos">
<label>Valor por ciclo *</label><input id="gvalue" type="number" value="200" min="1">
<label>Quantidade de participantes *</label><input id="gq" type="number" value="10" min="2">
<label>Quantidade de ciclos *</label><input id="gc" type="number" value="10" min="2">
<button class="btn btn-primary" onclick="App.createGroup()">Criar caixinha</button></div>`)}
function invites(){layout(`${header("Convites","Pessoas que você convidou para participar.")}
<div class="card"><button class="btn btn-primary" onclick="App.go('invite')">+ Convidar pessoa</button></div>
<div class="card"><div class="list">${state.invites.map(i=>`<div class="list-item"><div class="person"><div class="person-icon">${initials(i.name)}</div><div><strong>${esc(i.name)}</strong><div class="small">${esc(i.phone||"Sem telefone")}</div>${i.link?`<div class="small" style="color:var(--green)">Link gerado</div>`:""}</div></div><span class="badge ${i.status==="Pendente"?"pending":""}">${i.status}</span></div>`).join("")||`<div class="empty">Nenhum convite.</div>`}</div></div>`,"groups")}
function inviteScreen(){layout(`<button class="back" onclick="App.go('invites')">← Voltar</button>${header("Convidar pessoa","Envie o convite pelo canal que você já usa.")}
<div class="alert">No MVP 0.1, o convite pode ser enviado manualmente por WhatsApp. O TooJunto registra o convite.</div>
<div class="card"><label>Nome *</label><input id="iname" placeholder="Nome da pessoa"><label>Telefone</label><input id="iphone" placeholder="(71) 99999-9999"><button class="btn btn-primary" onclick="App.invite()">Criar convite</button></div>
<div class="card"><h2>Simular recebimento</h2><p class="small">Use este botão para testar a tela de convite recebido.</p><button class="btn btn-warning" onclick="App.go('invite-received')">Ver convite recebido</button></div>`)}
function groupScreen(){layout(`${header(esc(state.group.name),`${money(state.group.value)} por ciclo · ${state.group.cycles} ciclos`)}
<div class="card"><h2>Progresso</h2><div class="small">Ciclo ${state.group.currentCycle} de ${state.group.cycles}</div><div class="progress" style="margin:8px 0 14px"><div style="width:${state.group.progress}%"></div></div><div class="small">${state.group.progress}% concluído</div></div>
<div class="card"><h2>Próxima contemplação</h2><div class="person"><div class="person-icon">${initials(state.group.recipient)}</div><div><strong>${state.group.recipient}</strong><div class="small">Valor: ${money(state.group.value)}</div></div></div></div>
<div class="card"><h2>Participantes</h2><div class="list">${state.participants.map(p=>`<div class="list-item"><div class="person"><div class="person-icon">${p.initial}</div><div><strong>${esc(p.name)}</strong><div class="small">Posição ${p.position}</div></div></div><span class="badge">${p.status}</span></div>`).join("")}</div></div>
<div class="card"><button class="btn btn-primary" onclick="App.go('draw')">Sorteio</button><button class="btn btn-secondary" onclick="App.go('payment')">Registrar pagamento</button><button class="btn btn-secondary" onclick="App.go('history')">Ver histórico</button></div>`,"groups")}
function drawScreen(){layout(`${header("Sorteio","Defina a ordem de contemplação do grupo.")}
<div class="card center"><div class="small">Participantes confirmados</div><div class="big-number">${state.participants.length}</div><p>Depois do sorteio, a ordem fica registrada no grupo.</p>
${state.group.drawDone?`<span class="badge">Sorteio já realizado</span><button class="btn btn-primary" onclick="App.go('draw-result')">Ver resultado</button>`:`<button class="btn btn-primary" onclick="App.draw()">Realizar sorteio</button>`}</div>
<div class="alert">Protótipo: o sorteio é simulado localmente e não representa ainda a regra definitiva de produção.</div>`)}
function drawResult(){const order=state.order.length?state.order:state.participants.map((p,i)=>({...p,draw:i+1}));layout(`${header("Resultado do sorteio","Ordem de contemplação registrada.")}
<div class="card center"><span class="badge">Sorteio concluído</span><h2 style="margin-top:12px">Ordem definida</h2><p class="small">Esta lista é apenas uma simulação do MVP.</p></div>
<div class="card"><div class="list">${order.map((p,i)=>`<div class="list-item"><div class="person"><div class="person-icon">${i+1}</div><div><strong>${esc(p.name)}</strong><div class="small">${i===0?"Próxima contemplação":"Contemplação "+(i+1)}</div></div></div>${i===0?`<span class="badge">Próximo</span>`:""}</div>`).join("")}</div></div>
<button class="btn btn-primary" onclick="App.go('contemplation')">Ver contemplação</button>`,"groups")}
function paymentScreen(){const recipient=state.group.recipient;layout(`<button class="back" onclick="App.go('group')">← Voltar</button>${header("Registrar pagamento","O dinheiro é pago diretamente entre as pessoas.")}
<div class="card"><div class="small">Você deve pagar</div><h2>${money(state.group.value)}</h2><div class="person"><div class="person-icon">${initials(recipient)}</div><div><strong>${esc(recipient)}</strong><div class="small">Ciclo ${state.group.currentCycle}</div></div></div><label>Chave Pix</label><div class="pix">${esc(state.group.pixKey)}</div><button class="btn btn-secondary" onclick="copyPix()">Copiar chave Pix</button>
<button class="btn btn-primary" onclick="App.registerPayment()">Informar que paguei</button></div>
<div class="alert">O TooJunto não movimenta o dinheiro. Ele registra a declaração e permite a confirmação pelo gestor.</div>`,"payments")}
function payments(){layout(`${header("Pagamentos","Declarações e confirmações do grupo.")}
<div class="card"><button class="btn btn-primary" onclick="App.go('payment')">+ Registrar pagamento</button></div>
<div class="card"><div class="list">${state.payments.map(p=>`<div class="list-item"><div><strong>${esc(p.payer)}</strong><div class="small">Ciclo ${p.cycle} · ${money(p.value)} · ${p.date}</div></div><span class="badge ${p.status==="Pendente"?"pending":p.status==="Recusado"?"danger":""}">${p.status}</span></div>
${state.role==="gestor"&&p.status==="Pendente"?`<div class="btn-row"><button class="btn btn-primary" onclick="App.confirmPayment(${p.id},true)">Confirmar</button><button class="btn btn-danger" onclick="App.confirmPayment(${p.id},false)">Recusar</button></div>`:""}`).join("")||`<div class="empty">Nenhum pagamento registrado.</div>`}</div></div>`,"payments")}
function contemplation(){layout(`${header("Contemplação","Veja quem recebe neste ciclo.")}
<div class="card center"><div class="small">Ciclo ${state.group.currentCycle}</div><div class="person" style="justify-content:center;margin:18px 0"><div class="person-icon">${initials(state.group.recipient)}</div></div><h2>${esc(state.group.recipient)}</h2><div class="big-number">${money(state.group.value)}</div><span class="badge">Contemplação registrada</span></div>
<div class="card"><h2>Próximos passos</h2><p class="small">Os participantes realizam os pagamentos diretamente. O grupo acompanha os registros pelo TooJunto.</p><button class="btn btn-primary" onclick="App.go('payments')">Acompanhar pagamentos</button></div>`,"groups")}
function historyScreen(){layout(`${header("Histórico","Tudo que aconteceu no grupo fica registrado.")}
<div class="card"><div class="list">${state.history.map(h=>`<div class="list-item"><div><strong>${esc(h.event)}</strong><div class="small">${esc(h.detail)}</div></div><span class="small">${h.date}</span></div>`).join("")}</div></div>`,"history")}
function fallbackCopy(text,done){
 const ta=document.createElement("textarea");ta.value=text;ta.style.position="fixed";ta.style.opacity="0";
 document.body.appendChild(ta);ta.focus();ta.select();
 try{document.execCommand("copy");done()}catch(e){toast("Selecione e copie manualmente")}ta.remove();
}
function modal(html){document.body.insertAdjacentHTML("beforeend",`<div class="modal-backdrop" id="modal"><div class="modal">${html}</div></div>`)}
function closeModal(){document.getElementById("modal")?.remove()}
function copyPix(){navigator.clipboard?.writeText(state.group.pixKey).then(()=>toast("Chave Pix copiada")).catch(()=>toast("Copie a chave manualmente"))}
document.addEventListener("click",e=>{if(e.target.id==="modal")closeModal()});
render();

function inviteLinkScreen(){
 document.getElementById("bottomNav").style.display="none";
 const i=state.lastInvite||{};
 layout(`<button class="back" onclick="App.go('invites')">← Voltar para convites</button>${header("Convite pronto","Agora você pode enviar o convite para a pessoa.")}
 <div class="card">
   <span class="badge">Convite gerado</span>
   <h2 style="margin-top:12px">${esc(i.name||"Pessoa convidada")}</h2>
   <p class="small">O link abaixo é o endereço que a pessoa usará para abrir o convite.</p>
   <label>Link do convite</label>
   <div class="pix" style="font-weight:600">${esc(i.link||"https://app.toojunto.com.br/convite/demo123")}</div>
   <button class="btn btn-primary" onclick="App.copyInviteLink()">Copiar link</button>
   <button class="btn btn-secondary" onclick="App.copyInviteMessage()">Copiar mensagem completa</button>
   <button class="btn btn-warning" onclick="App.openWhatsApp()">Abrir WhatsApp</button>
 </div>
 <div class="card">
   <h2>Mensagem para enviar</h2>
   <div class="alert" style="white-space:pre-line">${esc(i.message||"")}</div>
   <p class="small">No protótipo, o endereço usa um domínio de demonstração. Em produção, o link será gerado pelo backend.</p>
 </div>`);
}
function inviteReceived(){layout(`${header("Você foi convidado!","Uma pessoa quer que você participe desta caixinha.")}
<div class="card"><span class="badge">Convite</span><h2 style="margin-top:12px">${esc(state.group.name)}</h2><p>Valor por ciclo: <strong>${money(state.group.value)}</strong></p><p class="small">Você poderá acompanhar os pagamentos, a ordem de contemplação e o andamento do grupo.</p><button class="btn btn-primary" onclick="App.acceptInvite()">Aceitar convite</button><button class="btn btn-secondary" onclick="App.go('home')">Agora não</button></div>`)}
