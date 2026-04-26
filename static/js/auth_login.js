// static/js/auth_login.js

import { auth } from "./firebase_init.js";

import {
    GoogleAuthProvider,
    signInWithPopup,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    updateProfile
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";


const formLogin = document.getElementById("form-login");
const btnCriarConta = document.getElementById("btn-criar-conta");
const btnGoogle = document.getElementById("btn-google");
const authMessage = document.getElementById("auth-message");


function mostrarMensagem(texto) {
    if (authMessage) {
        authMessage.innerText = texto;
    }
}


async function enviarTokenParaBackend(usuarioFirebase) {
    const idToken = await usuarioFirebase.getIdToken();

    const resposta = await fetch("/auth/session-login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            idToken: idToken
        })
    });

    const dados = await resposta.json();

    if (!resposta.ok || !dados.ok) {
        throw new Error(dados.erro || "Erro ao criar sessão no servidor.");
    }

    window.location.href = dados.redirect;
}


if (formLogin) {
    formLogin.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const senha = document.getElementById("senha").value;

        try {
            mostrarMensagem("Entrando...");

            const credencial = await signInWithEmailAndPassword(
                auth,
                email,
                senha
            );

            await enviarTokenParaBackend(credencial.user);
        } catch (error) {
            console.error(error);
            mostrarMensagem("Erro ao entrar. Verifique e-mail e senha.");
        }
    });
}


if (btnCriarConta) {
    btnCriarConta.addEventListener("click", async function () {
        const nome = document.getElementById("nome").value;
        const email = document.getElementById("email").value;
        const senha = document.getElementById("senha").value;

        if (!nome || !email || !senha) {
            mostrarMensagem("Informe nome, e-mail e senha para criar a conta.");
            return;
        }

        try {
            mostrarMensagem("Criando conta...");

            const credencial = await createUserWithEmailAndPassword(
                auth,
                email,
                senha
            );

            await updateProfile(credencial.user, {
                displayName: nome
            });

            await enviarTokenParaBackend(credencial.user);
        } catch (error) {
            console.error(error);
            mostrarMensagem("Erro ao criar conta. Talvez esse e-mail já exista.");
        }
    });
}


if (btnGoogle) {
    btnGoogle.addEventListener("click", async function () {
        try {
            mostrarMensagem("Abrindo login com Google...");

            const provider = new GoogleAuthProvider();

            const credencial = await signInWithPopup(
                auth,
                provider
            );

            await enviarTokenParaBackend(credencial.user);
        } catch (error) {
            console.error(error);
            mostrarMensagem("Erro ao entrar com Google.");
        }
    });
}