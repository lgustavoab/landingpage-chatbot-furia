// === Seletores e Variáveis ===
const track = document.querySelector(".carousel-track");
let slides = document.querySelectorAll(".carousel-img");

let index = 1;
let intervalo;
const intervaloTempo = 5000;

// === Botão do Chatbot ===
const toggleButton = document.getElementById("toggle-chatbot");
const chatbotDiv = document.getElementById("chatbot");

toggleButton.addEventListener("click", () => {
  if (chatbotDiv.style.display === "none" || chatbotDiv.style.display === "") {
    chatbotDiv.style.display = "block";
    toggleButton.textContent = "❌ Fechar Chat";
  } else {
    chatbotDiv.style.display = "none";
    toggleButton.textContent = "💬 Abrir Chat";
  }
});

// === Carrossel ===
function configurarCarrossel() {
  const primeiroClone = slides[0].cloneNode(true);
  const ultimoClone = slides[slides.length - 1].cloneNode(true);

  primeiroClone.id = "first-clone";
  ultimoClone.id = "last-clone";

  track.appendChild(primeiroClone);
  track.prepend(ultimoClone);

  slides = document.querySelectorAll(".carousel-img");
  const largura = slides[index].clientWidth;

  track.style.transform = `translateX(-${largura * index}px)`;
}

function moverPara(indexNovo) {
  const largura = slides[index].clientWidth;
  track.style.transition = "transform 0.5s ease-in-out";
  track.style.transform = `translateX(-${largura * indexNovo}px)`;
  index = indexNovo;
}

function avancarSlide() {
  if (index >= slides.length - 1) return;
  moverPara(index + 1);
}

function voltarSlide() {
  if (index <= 0) return;
  moverPara(index - 1);
}

function reiniciarSeClone() {
  const largura = slides[index].clientWidth;
  if (slides[index].id === "first-clone") {
    track.style.transition = "none";
    index = 1;
    track.style.transform = `translateX(-${largura * index}px)`;
  }
  if (slides[index].id === "last-clone") {
    track.style.transition = "none";
    index = slides.length - 2;
    track.style.transform = `translateX(-${largura * index}px)`;
  }
}

function iniciarAuto() {
  intervalo = setInterval(() => {
    avancarSlide();
  }, intervaloTempo);
}

function pararAuto() {
  clearInterval(intervalo);
}

// === Eventos ===
track.addEventListener("mouseenter", pararAuto);
track.addEventListener("mouseleave", iniciarAuto);
track.addEventListener("transitionend", reiniciarSeClone);
window.addEventListener("resize", () => moverPara(index));
window.addEventListener("DOMContentLoaded", () => {
  configurarCarrossel();
  iniciarAuto();
});

// === Dados de exemplo para a loja ===
const products = [
  { id: 1, name: "Camiseta FURIA | Adidas Preta", price: "R$ 359,00",
    img: "produtos/camiseta1.png",
    link: "https://www.furia.gg/produto/camiseta-oficial-furia-adidas-preta-150265"
  },
  { id: 2, name: "Boné FURIA Preto", price: "R$ 119,00",
    img: "produtos/bone1.png",
    link: "https://www.furia.gg/produto/bone-furia-preto-150142"
  },
  { id: 3, name: "Calça Moletom FURIA", price: "R$ 209,40",
    img: "produtos/moleton1.png",
    link: "https://www.furia.gg/produto/calca-moletom-furia-magic-panthera-preta-150206"
  },
  { id: 4, name: "Moletom Careca FURIA", price: "R$ 239,00",
    img: "produtos/moleton2.png",
    link: "https://www.furia.gg/produto/moletom-careca-furia-future-is-black-preto-150151"
  }
];

function renderStore() {
  const grid = document.getElementById("store-grid");
  products.forEach(prod => {
    const card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-image-thumb" data-full="/static/${prod.img}">
        <img src="/static/${prod.img}" alt="${prod.name}" loading="lazy">
      </div>
      <div class="product-info">
        <h3>${prod.name}</h3>
        <p>${prod.price}</p>
        <a href="${prod.link}" target="_blank">Comprar</a>
      </div>`;
    grid.appendChild(card);
  });
}

function setupImageLightbox() {
  const modal    = document.getElementById("image-modal");
  const modalImg = document.getElementById("image-modal-img");
  const closeBtn = document.getElementById("image-modal-close");

  // Abre o lightbox
  document.querySelectorAll(".product-image-thumb").forEach(thumb => {
    thumb.addEventListener("click", () => {
      modalImg.src = thumb.dataset.full;
      // Dupla garantia: classe e style
      modal.classList.add("show");
      modal.style.display = "flex";
    });
  });

  // Fecha ao clicar no botão
  closeBtn.addEventListener("click", () => {
    modal.classList.remove("show");
    modal.style.display = "none";
    modalImg.src = "";
  });

  // Fecha ao clicar fora da imagem (no overlay)
  modal.addEventListener("click", e => {
    if (e.target === modal) {
      modal.classList.remove("show");
      modal.style.display = "none";
      modalImg.src = "";
    }
  });
}

// dentro do seu DOMContentLoaded
window.addEventListener('DOMContentLoaded', () => {
  renderStore();
  setupImageLightbox();
  // outras iniciais…
});

// ===== Header: hide on scroll down, show on scroll up =====
let lastScrollY = window.pageYOffset;
const header = document.querySelector('header');

window.addEventListener('scroll', () => {
  const currentScrollY = window.pageYOffset;

  if (currentScrollY > lastScrollY) {
    // rolando pra baixo → esconde o header
    header.classList.add('hidden');
  } else {
    // rolando pra cima → mostra o header
    header.classList.remove('hidden');
  }

  // atualiza posição para a próxima iteração
  lastScrollY = currentScrollY;
});


document.addEventListener('DOMContentLoaded', () => {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.sidebar nav a');

  const ativarLink = () => {
    let scrollPos = window.scrollY + window.innerHeight / 3; 
    sections.forEach(sec => {
      if (sec.offsetTop <= scrollPos && (sec.offsetTop + sec.offsetHeight) > scrollPos) {
        const id = sec.getAttribute('id');
        navLinks.forEach(a => {
          a.classList.toggle('active', a.getAttribute('href') === `#${id}`);
        });
      }
    });
  };

  // dispara sempre que o usuário rolar
  window.addEventListener('scroll', ativarLink);
  // também ao carregar pra já marcar o topo
  ativarLink();
});