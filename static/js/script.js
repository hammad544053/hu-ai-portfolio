document.addEventListener('DOMContentLoaded', function () {
  // 1. Secret Admin Shortcut (Press 'L' key 5 times rapidly)
  let loginKeyCount = 0;
  let loginKeyTimeout;

  window.addEventListener('keydown', function (e) {
    if (e.key && e.key.toLowerCase() === 'l') {
      loginKeyCount++;
      clearTimeout(loginKeyTimeout);

      if (loginKeyCount === 5) {
        loginKeyCount = 0;
        window.location.href = '/login';
      }

      loginKeyTimeout = setTimeout(() => {
        loginKeyCount = 0;
      }, 2000);
    }
  });

  // 2. 3D Portrait Frame Animation Setup
  const START_FRAME = 40;
  const END_FRAME = 240;
  const TOTAL_FRAMES = END_FRAME - START_FRAME + 1; // 201 frames
  const FRAME_PATH_PREFIX = '/static/frames_nobg/ezgif-frame-';
  const FRAME_PATH_SUFFIX = '.png';

  const canvas = document.getElementById('animation-canvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  const images = new Array(TOTAL_FRAMES);
  let currentFrameIndex = 0;
  let targetFrameIndex = 0;

  function getFrameFilename(frameNumber) {
    const paddedIndex = String(frameNumber).padStart(3, '0');
    return `${FRAME_PATH_PREFIX}${paddedIndex}${FRAME_PATH_SUFFIX}`;
  }

  function resizeCanvas() {
    if (!canvas || !ctx) return;
    const dpr = window.devicePixelRatio || 1;
    const width = window.innerWidth;
    const height = window.innerHeight;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';

    ctx.scale(dpr, dpr);
    renderCurrentFrame();
  }

  function drawFrame(img) {
    if (!ctx || !img || !img.complete || img.naturalWidth === 0) return;

    const canvasWidth = window.innerWidth;
    const canvasHeight = window.innerHeight;

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    const imgWidth = img.naturalWidth;
    const imgHeight = img.naturalHeight;

    let drawWidth = 0;
    let drawHeight = 0;
    let x = 0;
    let y = 0;

    if (canvasWidth <= 768) {
      const scale = Math.min((canvasWidth * 1.5) / imgWidth, (canvasHeight * 1.5) / imgHeight);
      drawWidth = imgWidth * scale;
      drawHeight = imgHeight * scale;
      x = (canvasWidth - drawWidth) / 2;
      y = 80;
    } else {
      const scale = Math.min((canvasWidth * 1.2) / imgWidth, (canvasHeight * 0.9) / imgHeight);
      drawWidth = imgWidth * scale;
      drawHeight = imgHeight * scale;
      x = canvasWidth - drawWidth + (canvasWidth * 0.10);
      y = (canvasHeight - drawHeight) / 2 + 10;
    }

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(img, x, y, drawWidth, drawHeight);
  }

  function renderCurrentFrame() {
    const relativeIndex = Math.max(0, Math.min(TOTAL_FRAMES - 1, Math.round(currentFrameIndex)));
    if (images[relativeIndex]) {
      drawFrame(images[relativeIndex]);
    }
  }

  function updateScrollProgress() {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;

    const headerNav = document.getElementById('main-nav');
    if (headerNav) {
      if (scrollTop > 50) {
        headerNav.classList.add('nav-hidden');
      } else {
        headerNav.classList.remove('nav-hidden');
      }
    }

    if (maxScroll <= 0) return;
    const progress = Math.max(0, Math.min(1, scrollTop / maxScroll));
    targetFrameIndex = progress * (TOTAL_FRAMES - 1);
  }

  function tick() {
    if (canvas && ctx) {
      const diff = targetFrameIndex - currentFrameIndex;
      if (Math.abs(diff) > 0.001) {
        currentFrameIndex += diff * 0.15;
        renderCurrentFrame();
      } else if (currentFrameIndex !== targetFrameIndex) {
        currentFrameIndex = targetFrameIndex;
        renderCurrentFrame();
      }
    }
    requestAnimationFrame(tick);
  }

  function initCanvasAnimation() {
    if (!canvas || !ctx) return;
    resizeCanvas();
    updateScrollProgress();

    const firstImg = new Image();
    firstImg.onload = () => {
      images[0] = firstImg;
      drawFrame(firstImg);

      const staticWrap = document.getElementById('static-hero-img');
      if (staticWrap) staticWrap.style.opacity = '0';
    };
    firstImg.src = getFrameFilename(START_FRAME);

    for (let frameNum = START_FRAME + 1; frameNum <= END_FRAME; frameNum++) {
      const img = new Image();
      const relativeIdx = frameNum - START_FRAME;
      img.onload = () => {
        images[relativeIdx] = img;
      };
      img.src = getFrameFilename(frameNum);
    }

    tick();
  }

  // 3. Mobile Navigation Controls
  const hamburger = document.getElementById('hamburger-btn');
  const closeBtn = document.getElementById('drawer-close-btn');
  const mobileNav = document.getElementById('mobile-drawer');

  function openDrawer() {
    if (mobileNav) mobileNav.classList.add('open');
    if (hamburger) hamburger.classList.add('active');
  }

  function closeDrawer() {
    if (mobileNav) mobileNav.classList.remove('open');
    if (hamburger) hamburger.classList.remove('active');
  }

  if (hamburger) hamburger.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);

  window.addEventListener('resize', resizeCanvas);
  window.addEventListener('scroll', updateScrollProgress, { passive: true });

  initCanvasAnimation();
});




// 4. Contact Form Direct Flask AJAX Submission
  const contactForm = document.getElementById('contact-form');
  const formStatus = document.getElementById('form-status');
  const submitBtn = document.getElementById('form-submit-btn');

  if (contactForm) {
    contactForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Sending...';
      }

      if (formStatus) {
        formStatus.className = 'form-status-msg';
        formStatus.innerText = 'Sending message...';
        formStatus.style.display = 'block';
      }

      const formData = new FormData(contactForm);

      try {
        const response = await fetch(contactForm.action, {
          method: 'POST',
          body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
          formStatus.className = 'form-status-msg success';
          formStatus.innerText = '✓ Message sent directly to inbox! I will get back to you soon.';
          contactForm.reset();
        } else {
          throw new Error(data.message || 'Error sending message');
        }
      } catch (error) {
        formStatus.className = 'form-status-msg error';
        formStatus.innerText = '✕ ' + (error.message || 'Error sending message. Please try again.');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerText = 'Send Message ➔';
        }
      }
    });
  }