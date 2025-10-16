(function () {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim();
    if (all) {
      return [...document.querySelectorAll(el)];
    } else {
      return document.querySelector(el);
    }
  };

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    const target = select(el, all);
    if (!target) return;
    if (all) {
      target.forEach((e) => e.addEventListener(type, listener));
    } else {
      target.addEventListener(type, listener);
    }
  };

  /**
   * Easy on scroll event listener
   */
  const onscroll = (el, listener) => {
    el.addEventListener("scroll", listener);
  };

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select("#navbar .scrollto", true) || [];
  const navbarlinksActive = () => {
    let position = window.scrollY + 200;
    navbarlinks.forEach((navbarlink) => {
      if (!navbarlink.hash) return;
      let section = select(navbarlink.hash);
      if (!section) return;
      if (
        position >= section.offsetTop &&
        position <= section.offsetTop + section.offsetHeight
      ) {
        navbarlink.classList.add("active");
      } else {
        navbarlink.classList.remove("active");
      }
    });
  };
  window.addEventListener("load", navbarlinksActive);
  onscroll(document, navbarlinksActive);

  /**
   * Scroll with offset on links with class .scrollto
   */
  const scrollto = (el) => {
    let header = select("#header");
    if (!header) return;
    let offset = header.offsetHeight;

    if (!header.classList.contains("header-scrolled")) {
      offset -= 10;
    }

    let element = select(el);
    if (!element) return;

    let elementPos = element.offsetTop;
    window.scrollTo({
      top: elementPos - offset,
      behavior: "smooth",
    });
  };

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select("#header");
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add("header-scrolled");
      } else {
        selectHeader.classList.remove("header-scrolled");
      }
    };
    window.addEventListener("load", headerScrolled);
    onscroll(document, headerScrolled);
  }

  /**
   * Back to top button
   */
  let backtotop = select(".back-to-top");
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add("active");
      } else {
        backtotop.classList.remove("active");
      }
    };
    window.addEventListener("load", toggleBacktotop);
    onscroll(document, toggleBacktotop);
  }

  /**
   * Mobile Navigation Toggle
   */
  on("click", ".mobile-nav-toggle", function () {
    const nav = select("#navbar");
    if (!nav) return;

    nav.classList.toggle("navbar-mobile");
    nav.classList.toggle("active");
    this.classList.toggle("bi-list");
    this.classList.toggle("bi-x");
  });




  /**
   * Smooth scroll for links
   */
  on(
    "click",
    ".scrollto",
    function (e) {
      if (this.hash && select(this.hash)) {
        e.preventDefault();

        scrollto(this.hash);
      }
    },
    true
  );

  /**
   * Scroll with offset on page load
   */
  window.addEventListener("load", () => {
    if (window.location.hash && select(window.location.hash)) {
      scrollto(window.location.hash);
    }
  });

  /**
   * Sliders (guarded if Swiper is available)
   */
  const initSwipers = () => {
    if (typeof Swiper === "undefined") return;

    // Clients slider
    new Swiper(".clients-slider", {
      speed: 400,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },
      slidesPerView: "auto",
      pagination: {
        el: ".clients-slider .swiper-pagination",
        clickable: true,
      },
      breakpoints: {
        320: { slidesPerView: 2, spaceBetween: 20 },
        480: { slidesPerView: 3, spaceBetween: 30 },
        640: { slidesPerView: 4, spaceBetween: 40 },
        992: { slidesPerView: 6, spaceBetween: 50 },
      },
    });

    // Portfolio details slider
    new Swiper(".portfolio-details-slider", {
      speed: 600,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },
      slidesPerView: 1,
      pagination: {
        el: ".portfolio-details-slider .swiper-pagination",
        type: "bullets",
        clickable: true,
      },
      navigation: {
        nextEl: ".portfolio-details-slider .swiper-button-next",
        prevEl: ".portfolio-details-slider .swiper-button-prev",
      },
    });

    // Page (hero) slider
    new Swiper(".page-slider", {
      speed: 600,
      loop: true,
      autoplay: {
        delay: 6000,
        disableOnInteraction: false,
      },
      slidesPerView: 1,
      effect: "fade",
      pagination: {
        el: ".page-slider .swiper-pagination",
        clickable: true,
      },
    });

    // Testimonials slider (News section)
    new Swiper(".testimonials-slider", {
      speed: 600,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },
      slidesPerView: 1,
      pagination: {
        el: ".testimonials-slider .swiper-pagination",
        clickable: true,
      },
      breakpoints: {
        480: { slidesPerView: 1, spaceBetween: 20 },
        576: { slidesPerView: 2, spaceBetween: 25 },
        768: { slidesPerView: 3, spaceBetween: 30 },
        992: { slidesPerView: 3, spaceBetween: 40 },
        1200: { slidesPerView: 3, spaceBetween: 50 },
        1400: { slidesPerView: 3, spaceBetween: 60 },
        1600: { slidesPerView: 3, spaceBetween: 40 },
        1800: { slidesPerView: 3, spaceBetween: 50 },
      },
    });
  };
  window.addEventListener("load", initSwipers);

  /**
   * Enhanced Scroll Animations
   */
  function initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);

    // Observe all animation elements
    document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right, .scale-in').forEach(el => {
      observer.observe(el);
    });
  }


  /**
   * Enhanced Button Interactions
   */
  function initButtonEnhancements() {
    // Add ripple effect to buttons
    document.querySelectorAll('.btn-modern').forEach(button => {
      button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        this.appendChild(ripple);

        setTimeout(() => {
          ripple.remove();
        }, 600);
      });
    });
  }

  /**
   * Loading States Management
   */
  function initLoadingStates() {
    // Show skeleton loading for images
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => {
      img.addEventListener('load', () => {
        img.classList.add('loaded');
      });
    });

    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-fill');
    const progressObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const target = entry.target;
          const width = target.dataset.width || '100%';
          setTimeout(() => {
            target.style.width = width;
          }, 200);
        }
      });
    });

    progressBars.forEach(bar => {
      progressObserver.observe(bar);
    });
  }

  /**
   * Smooth Scrolling for Anchor Links
   */
  function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  /**
   * Animation on scroll (guarded if AOS is available)
   */
  function aos_init() {
    if (typeof AOS === "undefined") return;
    AOS.init({
      duration: 1000,
      easing: "ease-in-out",
      once: true,
      mirror: false,
    });
  }
  /**
   * Ripple Effect CSS
   */
  function addRippleStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .btn-modern {
        position: relative;
        overflow: hidden;
      }

      .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
      }

      @keyframes ripple-animation {
        to {
          transform: scale(4);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Initiate everything
   */
  window.addEventListener("load", () => {
    aos_init();
    initSwipers();
    initScrollAnimations();
    initButtonEnhancements();
    initLoadingStates();
    initSmoothScrolling();
    addRippleStyles();
  });


  /**
   * Pure Counter (guarded)
   */
  if (typeof PureCounter !== "undefined") {
    new PureCounter();
  }
})();
/**
   * test console
   */
