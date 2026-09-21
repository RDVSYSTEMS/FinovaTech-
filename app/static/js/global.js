/* =====================================================
    SCRIPT.JS — Sistema de FinovaTech v10
   FinovaTech — SENA 2026
   
   Archivo principal del frontend. Se carga en TODAS las
   páginas y hace que la interfaz "cobre vida":

   SECCIONES DE ESTE ARCHIVO:
   1. AOS           -> Animaciones al hacer scroll.
   2. Menú           -> Header/footer dinámicos según la sesión
                        (menú público vs menú de usuario logueado).
   3. Toggle pass   -> Mostrar/ocultar contraseña (login/registro).
   4. Menú móvil    -> Menú hamburguesa y sidebar del panel.
   5. Scroll        -> Sombra del header y botón "volver arriba".
   6. Formularios   -> Ingresos/gastos, soporte y agendamiento.
   7. Buscador      -> Filtra filas de tablas en tiempo real.
   8. Contadores    -> Anima los números de estadísticas.

   NOTA: usa un solo listener de DOMContentLoaded para cargar
   el header y el footer dinámicamente en cada página.
   ===================================================== */

console.log(" Sistema iniciado — FinovaTech 2026");

/* =====================================================
   AOS — Animaciones al hacer scroll
   Debe inicializarse antes que cualquier otro script
   ===================================================== */

if (typeof AOS !== "undefined") {
    AOS.init({ duration: 800, once: true });
}

/* =====================================================
   FUNCIÓN AUXILIAR — Toggle de contraseña
   Reutilizada por login y registro para mostrar/ocultar
   ===================================================== */

function togglePasswordVisibilidad(botonId, inputId) {
    const btn  = document.getElementById(botonId);
    const input = document.getElementById(inputId);
    if (btn && input) {
        btn.addEventListener("click", function () {
            const tipo = input.type === "password" ? "text" : "password";
            input.type = tipo;
            btn.textContent = tipo === "password" ? "👁️" : "🙈";
        });
    }
}

/* =====================================================
   DOMContentLoaded — Todo lo que necesita el DOM listo
   Un solo listener para evitar duplicados
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ── Menú según sesión ──────────────────────
    const pagina = window.location.pathname;
    const rutasLogueadas = ['/panel', '/lista', '/notificacion', '/agendamiento'];
    const estaLogueado = rutasLogueadas.some(r => pagina.includes(r));

    const menuHTML = estaLogueado ? `
        <nav class="menu-superior">
            <a href="/panel">Dashboard</a>
            <a href="/lista">Lista</a>
            <a href="/agendamiento">Agendar</a>
            <a href="/notificacion">Notificaciones</a>
        </nav>
    ` : `
        <nav class="menu-superior">
            <a href="/">Inicio</a>
            <a href="/servicios.html">Servicios</a>
            <a href="/agendamiento">Agendar</a>
            <a href="/login">Iniciar sesión</a>
            <a href="/registro" class="btn-nav">Registrarse</a>
        </nav>
    `;

    // ── Header dinámico ────────────────────────
    const headerDiv = document.getElementById("header");
    if (headerDiv) {
        headerDiv.innerHTML = `
        <header class="header-glass">
            <div class="logo">
                <div class="logo-img-wrap">
                    <img src="/static/assets/img/RDV_systems logo 200x200px.png" alt="Logo">
                </div>
                <div class="logo-text">
                    <h2>Finanzas</h2>
                    <span>FinovaTech</span>
                </div>
            </div>
            <button id="menu-toggle" class="menu-toggle" aria-label="Abrir menú">☰</button>
            ${menuHTML}
        </header>`;
    }

    // ── Footer dinámico ────────────────────────
    const footerDiv = document.getElementById("footer");
    if (footerDiv) {
        footerDiv.innerHTML = `
        <footer>
            <p>© 2026 FinovaTech. Todos los derechos reservados.</p>
            <p>Proyecto desarrollado para el SENA - Técnico en Programación de Software.</p>
            <div class="footer-links">
                <a href="/contacto.html">Contacto y Créditos</a>
                <a href="/soporte.html">Soporte</a>
                <a href="/terminos.html">Términos y condiciones</a>
            </div>
        </footer>`;
    }

    // ── Menú hamburguesa ───────────────────────
    const toggle = document.getElementById("menu-toggle");
    const menu   = document.querySelector(".menu-superior");
    if (toggle && menu) {
        toggle.addEventListener("click", function () {
            menu.classList.toggle("abierto");
        });
    }

    // ── Sidebar toggle (móvil, páginas panel) ──
    const btnSidebar = document.getElementById("sidebar-toggle");
    const sidebar    = document.querySelector(".panel-sidebar");
    if (btnSidebar && sidebar) {
        btnSidebar.addEventListener("click", function () {
            sidebar.classList.toggle("abierto");
            btnSidebar.classList.toggle("activo");
            btnSidebar.textContent = sidebar.classList.contains("abierto") ? "✕" : "☰";
        });

        // Cerrar sidebar al hacer clic fuera
        document.addEventListener("click", function (e) {
            if (!sidebar.contains(e.target) && e.target !== btnSidebar) {
                sidebar.classList.remove("abierto");
                btnSidebar.classList.remove("activo");
                btnSidebar.textContent = "☰";
            }
        });
    }

});

/* =====================================================
   SCROLL — Evento único para sombra del header
   y botón volver arriba. Separados antes pero
   unificados para rendimiento.
   ===================================================== */

window.addEventListener("scroll", function () {
    const header = document.querySelector("header");
    if (header) {
        header.style.boxShadow = window.scrollY > 10
            ? "0 4px 20px rgba(0,0,0,0.4)"
            : "0 4px 15px rgba(0,0,0,0.2)";
    }

    const btnArriba = document.getElementById("btn-arriba");
    if (btnArriba) {
        btnArriba.style.display = window.scrollY > 300 ? "block" : "none";
    }
});

/* =====================================================
   FORMULARIOS GENERALES (ingresos/gastos)
   #formulario y #formulario2 — misma lógica
   ===================================================== */

["formulario", "formulario2"].forEach(function (id) {
    const form = document.querySelector("#" + id);
    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            // Este formulario pertenece al flujo legacy aún pendiente de backend.
            alert("✅ Información guardada");
            window.location.href = "lista.html";
        });
    }
});

/* =====================================================
   FORMULARIO DE SOPORTE
   Validación de nombre, correo, asunto y mensaje.
   ===================================================== */

const formSoporte = document.querySelector("#formSoporte");

if (formSoporte) {

    formSoporte.addEventListener("submit", function (e) {
        e.preventDefault();

        const nombre  = document.getElementById("soporte-nombre").value.trim();
        const correo  = document.getElementById("soporte-correo").value.trim();
        const asunto  = document.getElementById("soporte-asunto").value;
        const mensaje = document.getElementById("soporte-mensaje").value.trim();
        const error   = document.getElementById("soporte-error");
        const exito   = document.getElementById("soporte-exito");

        if (!nombre || !correo || !asunto || !mensaje) {
            error.textContent   = "❌ Completa todos los campos";
            error.style.display = "block";
            exito.style.display = "none";
            return;
        }

        if (!correo.includes("@") || !correo.includes(".")) {
            error.textContent   = "❌ Ingresa un correo válido";
            error.style.display = "block";
            exito.style.display = "none";
            return;
        }

        // Soporte muestra confirmación local; todavía no crea tickets persistentes.
        error.style.display  = "none";
        exito.style.display  = "block";
        formSoporte.reset();

        setTimeout(function () {
            exito.style.display = "none";
        }, 4000);
    });
}

/* =====================================================
   FORMULARIO DE AGENDAMIENTO
   Validación de fecha, hora y categoría.
   La fecha no puede ser anterior a hoy.
   ===================================================== */

const formAgenda = document.querySelector("#formAgenda");

if (formAgenda) {

    formAgenda.addEventListener("submit", function (e) {
        e.preventDefault();

        const fecha     = document.getElementById("fecha").value.trim();
        const hora      = document.getElementById("hora").value.trim();
        const categoria = document.getElementById("categoria").value;
        const error     = document.getElementById("agenda-error");
        const exito     = document.getElementById("agenda-exito");

        if (!fecha || !hora || !categoria) {
            error.textContent   = "❌ Completa todos los campos obligatorios";
            error.style.display = "block";
            exito.style.display = "none";
            return;
        }

        // Validar que la fecha no sea pasada
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);
        const fechaSel = new Date(fecha + "T00:00:00");
        if (fechaSel < hoy) {
            error.textContent   = "❌ La fecha no puede ser anterior a hoy";
            error.style.display = "block";
            exito.style.display = "none";
            return;
        }

        const datos = new FormData(formAgenda);
        fetch("/agendamiento", {
            method: "POST",
            body: datos,
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
            .then(function (respuesta) {
                return respuesta.json().then(function (resultado) {
                    if (!respuesta.ok) {
                        throw new Error(resultado.mensaje || "No fue posible guardar la sesión");
                    }
                    return resultado;
                });
            })
            .then(function (resultado) {
                error.style.display = "none";
                exito.textContent = "✅ " + resultado.mensaje;
                exito.style.display = "block";
                formAgenda.reset();
            })
            .catch(function (fallo) {
                error.textContent = "❌ " + fallo.message;
                error.style.display = "block";
                exito.style.display = "none";
            });
    });
}

/* =====================================================
   BUSCADOR EN TABLAS
   Filtra filas del tbody en tiempo real mientras
   el usuario escribe.
   ===================================================== */

const buscador = document.querySelector("#buscador");

if (buscador) {

    buscador.addEventListener("keyup", function () {
        const texto = buscador.value.toLowerCase();
        const filas = document.querySelectorAll("tbody tr");

        filas.forEach(function (fila) {
            fila.style.display = fila.textContent.toLowerCase().includes(texto) ? "" : "none";
        });
    });
}

/* =====================================================
   CONTADOR ESTADÍSTICAS
   Anima los números del index al hacer scroll
   usando IntersectionObserver.
   ===================================================== */

const contadores = document.querySelectorAll(".numero");

if (contadores.length > 0) {

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el     = entry.target;
                const target = +el.getAttribute("data-target");
                let current  = 0;
                const step   = Math.ceil(target / 60);

                const timer = setInterval(() => {
                    current += step;
                    if (current >= target) {
                        el.textContent = target;
                        clearInterval(timer);
                    } else {
                        el.textContent = current;
                    }
                }, 25);

                observer.unobserve(el);
            }
        });
    });

    contadores.forEach(c => observer.observe(c));
}
