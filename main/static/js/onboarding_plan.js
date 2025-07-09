document.addEventListener('DOMContentLoaded', () => {
  // Stepper logic
  const stepperItems = Array.from(document.querySelectorAll('.timeline-stepper .stepper-item'));
  const panels = Array.from(document.querySelectorAll('.timeline-step-content .timeline-step-panel'));
  const nextBtns = document.querySelectorAll('.next-step-btn');
  const prevBtns = document.querySelectorAll('.prev-step-btn');

  function setStep(activeIdx) {
    stepperItems.forEach((item, idx) => {
      item.classList.remove('active', 'completed');
      if (idx < activeIdx) item.classList.add('completed');
      if (idx === activeIdx) item.classList.add('active');
    });
    panels.forEach((panel, idx) => {
      panel.classList.toggle('active', idx === activeIdx);
    });
  }

  nextBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const nextIdx = parseInt(this.getAttribute('data-next'), 10);
      setStep(nextIdx);
    });
  });

  prevBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const prevIdx = parseInt(this.getAttribute('data-prev'), 10);
      setStep(prevIdx);
    });
  });

  // Timeline progressive reveal with progress bar
  const steps = Array.from(document.querySelectorAll('.timeline-step'));
  const progressBar = document.getElementById('timeline-progress-bar-inner');
  let revealedSteps = 1;

  function updateProgressBar() {
    if (!progressBar || steps.length === 0) return;
    const percent = ((revealedSteps - 1) / (steps.length - 1)) * 100;
    progressBar.style.width = steps.length === 1 ? '100%' : percent + '%';
  }

  if (steps.length) {
    // Only the first step is active at start
    steps.forEach((step, idx) => {
      if (idx === 0) {
        step.classList.add('active');
        step.classList.remove('completed');
      } else {
        step.classList.remove('active');
        step.classList.remove('completed');
      }
      // Hide details for all
      const detail = step.querySelector('.step-detail');
      if (detail) detail.classList.add('hidden');
    });

    updateProgressBar();

    steps.forEach((step, idx) => {
      const btn = step.querySelector('.reveal-step');
      if (btn) {
        btn.addEventListener('click', () => {
          // Reveal detail for this step
          const detail = step.querySelector('.step-detail');
          if (detail) {
            detail.classList.toggle('hidden');
            btn.textContent = detail.classList.contains('hidden') ? 'Learn More' : 'Show Less';
          }
          // If detail is now visible, activate next step and update progress bar
          if (!detail.classList.contains('hidden') && steps[idx + 1]) {
            step.classList.add('completed');
            steps[idx + 1].classList.add('active');
            revealedSteps = Math.max(revealedSteps, idx + 2);
            updateProgressBar();
          }
        });
      }
    });
  }

  // Flip plan cards on click
  document.querySelectorAll('.plan-card').forEach(card => {
    card.addEventListener('click', (e) => {
      if (e.target.classList.contains('book-btn')) return;
      card.querySelector('.card-inner').classList.toggle('flipped');
    });
  });

  // Toggle renewals
  document.querySelectorAll('.renewal-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const detail = btn.parentElement.querySelector('.renewal-detail');
      detail.classList.toggle('hidden');
    });
  });
});
