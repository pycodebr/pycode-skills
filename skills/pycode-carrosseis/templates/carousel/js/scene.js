/*
 * Desenho e animação do conceito. Carousel.onSlide(n, fn) roda depois que o texto entrou;
 * Carousel.animate(n, fn, {duration}) registra o slide em vídeo (fn recebe t em segundos).
 *
 * Regras do vídeo: o mesmo t gera sempre o mesmo quadro (nada de Math.random ou Date.now;
 * use Carousel.rng(semente)), o quadro 0 já mostra o título inteiro (é o pôster) e o movimento
 * usa só transform, opacity e stroke-dashoffset.
 */
(() => {
  const C = window.Carousel;

  // Exemplo: na capa, o trilho se desenha da esquerda para a direita e o objeto herói sobe.
  C.animate(1, (t, slide) => {
    const line = slide.querySelector('.rail-line');
    const glow = slide.querySelector('.rail-glow');
    const p = C.ease.inOut(C.prog(t, 0.3, 2.2));
    for (const path of [line, glow]) {
      if (!path) continue;
      const len = path.getTotalLength();
      path.style.strokeDasharray = `${len}`;
      path.style.strokeDashoffset = `${len * (1 - p)}`;
    }
    const hero = slide.querySelector('.hero');
    if (hero) {
      const h = C.ease.out(C.prog(t, 0.0, 1.4));
      hero.style.opacity = String(0.35 + 0.65 * h);
      hero.style.transform = `translateY(${(1 - h) * 40}px)`;
    }
  }, { duration: 4 });
})();
