// static/js/auth.js

import { auth } from "./firebase-init.js";

import {
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/12.12.1/firebase-auth.js";

const provider = new GoogleAuthProvider();

const btnLoginGoogle = document.getElementById("btn-login-google");
const btnLogout = document.getElementById("btn-logout");
const userInfo = document.getElementById("user-info");

if (btnLoginGoogle) {
  btnLoginGoogle.addEventListener("click", async () => {
    try {
      const resultado = await signInWithPopup(auth, provider);
      const usuario = resultado.user;

      console.log("Usuário logado:", usuario);

      alert(`Bem-vindo, ${usuario.displayName}!`);
    } catch (error) {
      console.error("Erro no login com Google:", error);
      alert("Erro ao fazer login com Google.");
    }
  });
}

if (btnLogout) {
  btnLogout.addEventListener("click", async () => {
    try {
      await signOut(auth);
      alert("Usuário saiu da conta.");
    } catch (error) {
      console.error("Erro ao sair:", error);
    }
  });
}

onAuthStateChanged(auth, (usuario) => {
  if (usuario) {
    if (userInfo) {
      userInfo.innerHTML = `
        <p>Logado como: ${usuario.displayName}</p>
        <p>Email: ${usuario.email}</p>
      `;
    }
  } else {
    if (userInfo) {
      userInfo.innerHTML = "<p>Nenhum usuário logado.</p>";
    }
  }
});