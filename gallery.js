for (const gallery of document.querySelectorAll('[data-gallery]')) {
  const image = gallery.querySelector('[data-main]');
  const full = gallery.querySelector('[data-full]');
  const caption = gallery.querySelector('[data-caption]');
  const choices = gallery.querySelectorAll('[data-preview]');

  for (const choice of choices) {
    choice.addEventListener('click', (event) => {
      if (event.button !== 0 || event.ctrlKey || event.shiftKey || event.altKey || event.metaKey) return;
      event.preventDefault();
      for (const item of choices) item.removeAttribute('aria-current');
      choice.setAttribute('aria-current', 'true');
      image.alt = choice.dataset.alt;
      image.src = choice.href;
      full.href = choice.href;
      caption.textContent = choice.dataset.label;
    });
  }
}
